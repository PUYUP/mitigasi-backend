import pytz
import requests
import geopy.geocoders
import requests  # to get image from the web
import shutil  # to save it locally
import os

from geopy.geocoders import Nominatim
from collections import defaultdict
from fake_useragent import UserAgent

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.apps import apps
from django.core.files import File
from django.conf import settings

Disaster = apps.get_registered_model('ews', 'Disaster')
DisasterLocation = apps.get_registered_model('ews', 'DisasterLocation')
DisasterAttachment = apps.get_registered_model('ews', 'DisasterAttachment')
Attribute = apps.get_registered_model('eav', 'Attribute')


def quake():
    """
    Shakemap formula:
    <Datetime>+<Jam>

    Jam: 09:51:58 WIB
    Datetime: 2021-10-23T02:51:58+00:00
    Result: 20211023095158.mmi.jpg
    """
    url = 'https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json'
    r = requests.get(url)
    res = r.json()
    info_gempa = res.get('Infogempa', {})
    gempa = info_gempa.get('gempa', {})
    shakemap_base_url = 'https://data.bmkg.go.id/DataMKG/TEWS/'
    disaster_objs = list()
    disaster_attributes = defaultdict(list)
    disaster_locations = defaultdict(list)
    location_objs = defaultdict(list)

    for index, item in enumerate(gempa):
        datetime = item.get('DateTime', timezone.now())
        coordinates = item.get('Coordinates', 0).split(',')
        magnitude = item.get('Magnitude', 0)
        depth = item.get('Kedalaman', 0)
        description = item.get('Wilayah', '')
        location = item.get('Dirasakan', '')

        utc_datetime = timezone.datetime.strptime(
            datetime,
            '%Y-%m-%dT%H:%M:%S+00:00'
        )

        local_timezone = pytz.timezone('Asia/Jakarta')
        local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
        local_datetime = local_datetime.astimezone(local_timezone)

        # generate shakemap from datetime
        dt_split = str(local_datetime).split('+')
        dt_only = dt_split[0]
        shakemap = dt_only.replace('-', '').replace(':', '').replace(' ', '')
        shakemap_url = '{}{}.mmi.jpg'.format(shakemap_base_url, shakemap)

        # latitude and longitude
        latitude = coordinates[0]
        longitude = coordinates[1]

        # depth
        numbers = []
        for word in depth.split():
            if word.isdigit():
                numbers.append(int(word))

        depth = numbers[0]

        # locations, don't forget clean white space before save to db
        locations = location.split(',')
        locations_clean = [loc.strip().replace(' - ', '-')
                           for loc in locations]

        # separate level and location name
        levels = [loc.split(' ')[0] for loc in locations_clean]

        names = list()
        for loc in locations_clean:
            REMOVE_WORDS = ['Des.', 'Kel.', 'Kec.', 'Kab.']
            for r in REMOVE_WORDS:
                loc = loc.replace(r, '').strip()

            l = loc.split(' ')
            l.pop(0)
            l = [i for i in l if i]

            names.append(' '.join(l))

        disaster_data = {
            'occur_at': local_datetime,
            'description': description,
            'source': 'BMKG',
            'identifier': Disaster._Identifier.I108,
            'title': description,
        }

        # check if exists
        if not Disaster.objects.filter(occur_at=local_datetime, title=description, identifier=Disaster._Identifier.I108).exists():
            disaster_obj: Disaster = Disaster(**disaster_data)
            disaster_objs.append(disaster_obj)

            # collect attributes
            disaster_attributes[index].append({
                'earthquake_epicenter_latitude': latitude,
                'earthquake_epicenter_longitude': longitude,
                'earthquake_depth': depth,
                'earthquake_magnitude': magnitude,
            })

            # collect locations
            disaster_locations[index].append({
                'names': names,
                'levels': levels,
            })

    if len(disaster_locations) > 0:
        for index in disaster_locations:
            geopy.geocoders.options.default_timeout = 7

            ua = UserAgent()
            geolocator = Nominatim(user_agent=ua.google)
            geolatlon = list()
            names = disaster_locations[index][0]['names']
            levels = disaster_locations[index][0]['levels']

            for name in names:
                geoloc = geolocator.geocode(
                    name,
                    language='id',
                    addressdetails=True,
                    namedetails=True
                )

                if geoloc:
                    geolatlon.append(
                        "{}, {}".format(geoloc.latitude, geoloc.longitude)
                    )

            for i, loc in enumerate(geolatlon):
                severity = levels[i]
                geoverse = geolocator.reverse(
                    loc,
                    language='id',
                    addressdetails=True
                )

                # Country
                country_code = geoverse.raw['address'].get('country_code')
                country = geoverse.raw['address'].get('country')

                # administrative_area
                administrative_area = geoverse.raw['address'].get('state')

                # build location object
                obj: DisasterLocation = DisasterLocation(
                    country=country,
                    country_code=country_code,
                    administrative_area=administrative_area,
                    latitude=geoverse.latitude,
                    longitude=geoverse.longitude,
                    severity=severity,
                )

                location_objs[index].append(obj)

    # Bulk create
    try:
        Disaster.objects.bulk_create(disaster_objs, ignore_conflicts=False)
    except Exception as e:
        print(e)

    latest_disaster_objs = Disaster.objects \
        .order_by('-id')[:len(disaster_objs)]

    total = len(disaster_locations)
    for index, obj in enumerate(latest_disaster_objs):
        x = (total - index) - 1

        # set attribute
        attributes = disaster_attributes[x][0]
        model_name = obj._meta.model_name
        model_ct = ContentType.objects.get(model=model_name)

        for key in attributes:
            value = attributes[key]
            attr, _created = Attribute.objects.get_or_create(
                name=key,
                slug=key,
                datatype=Attribute.TYPE_FLOAT
            )

            attr.entity_ct.set([model_ct])
            setattr(obj.eav, key, value)

        obj.eav.save()

        # set location
        locations = location_objs[x]
        for x in locations:
            setattr(x, 'disaster', obj)

        try:
            DisasterLocation.objects.bulk_create(
                locations,
                ignore_conflicts=True
            )
        except Exception as e:
            print(e)

        # Set up the image URL and filename
        filename = shakemap_url.split("/")[-1]

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(shakemap_url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Retrieve file from root path
            filepath = os.path.join(settings.PROJECT_PATH, filename)

            # Open a local file with wb ( write binary ) permission.
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            with open(filepath, 'rb') as f:
                fobj = File(f)
                attachment = DisasterAttachment.objects.create(
                    disaster=obj,
                    identifier='shakemap'
                )
                attachment.file.save(filename, fobj)

            # delete unused file
            if os.path.exists(filepath):
                os.remove(filepath)
