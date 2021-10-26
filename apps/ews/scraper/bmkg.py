import pytz
import requests
import requests  # to get image from the web
import shutil  # to save it locally
import os

from bs4 import BeautifulSoup
from collections import defaultdict

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.apps import apps
from django.core.files import File
from django.conf import settings
from django.db.models import Q

Disaster = apps.get_registered_model('ews', 'Disaster')
DisasterLocation = apps.get_registered_model('ews', 'DisasterLocation')
DisasterAttachment = apps.get_registered_model('ews', 'DisasterAttachment')
Attribute = apps.get_registered_model('eav', 'Attribute')


@transaction.atomic
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
    local_timezone = pytz.timezone('Asia/Jakarta')

    # last saved disaster
    last_saved = Disaster.objects \
        .filter(identifier=Disaster._Identifier.DIS108) \
        .exclude(eav__dis108_status__isnull=True) \
        .order_by('id') \
        .last()

    future_date = timezone.datetime(
        int(1900),
        int(12),
        int(31),
        tzinfo=local_timezone
    )
    future_date_local = future_date.astimezone(local_timezone)

    last_saved_dt = last_saved.occur_at.astimezone(local_timezone)  \
        if last_saved else future_date_local

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
            'identifier': Disaster._Identifier.DIS108,
            'title': description,
        }

        # check if exists
        checker = Disaster.objects \
            .filter(
                occur_at=local_datetime,
                title=description,
                identifier=Disaster._Identifier.DIS108
            ) \
            .exclude(eav__dis108_status__isnull=True)

        if local_datetime > last_saved_dt and not checker.exists():
            disaster_obj: Disaster = Disaster(**disaster_data)
            disaster_objs.append(disaster_obj)

            # collect attributes
            disaster_attributes[index].append({
                'dis108_epicenter_latitude': latitude,
                'dis108_epicenter_longitude': longitude,
                'dis108_depth': depth,
                'dis108_magnitude': magnitude,
            })

            # collect locations
            disaster_locations[index].append({
                'names': names,
                'levels': levels,
            })

    if len(disaster_locations) > 0:
        for index in disaster_locations:
            names = disaster_locations[index][0]['names']
            levels = disaster_locations[index][0]['levels']

            for index, name in enumerate(names):
                severity = levels[index]

                # build location object
                # latitude and longitude set when user show disaster detail
                obj = DisasterLocation(
                    administrative_area=name, severity=severity)

                location_objs[index].append(obj)

    # Bulk create
    # sorted by occur_at
    new_disaster_objs = sorted(disaster_objs, key=lambda d: d.occur_at)

    try:
        Disaster.objects.bulk_create(new_disaster_objs, ignore_conflicts=False)
    except Exception as e:
        print(e)

    latest_disaster_objs = Disaster.objects \
        .order_by('-id')[:len(disaster_objs)]

    for index, obj in enumerate(latest_disaster_objs):
        # set attribute
        attributes = disaster_attributes[index][0]
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
        locations = location_objs[index]
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


@transaction.atomic
def quake_realtime():
    url = 'https://inatews.bmkg.go.id/?act=realtimeev'
    param = {}
    page = requests.get(url, params=param, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all('form', {'name': 'myform'})

    disaster_objs = list()
    disaster_attributes = defaultdict(list)
    location_objs = defaultdict(list)
    local_timezone = pytz.timezone('Asia/Jakarta')

    # last saved disaster
    last_saved = Disaster.objects \
        .filter(
            Q(identifier=Disaster._Identifier.DIS108),
            Q(eav__dis108_status__isnull=False)
            & Q(eav__dis108_status='preliminary')
        ) \
        .order_by('id') \
        .last()

    future_date = timezone.datetime(
        int(1900),
        int(12),
        int(31),
        tzinfo=local_timezone
    )
    future_date_local = future_date.astimezone(local_timezone)

    last_saved_dt = last_saved.occur_at.astimezone(local_timezone)  \
        if last_saved else future_date_local

    for index, form in enumerate(results):
        waktu = form.find('input', {'name': 'waktu'}) \
            .get('value').replace('  ', ' ')

        lintang = form.find('input', {'name': 'lintang'}).get('value')
        bujur = form.find('input', {'name': 'bujur'}).get('value')
        dalam = form.find('input', {'name': 'dalam'}).get('value')
        mag = form.find('input', {'name': 'mag'}).get('value')
        area = form.find('input', {'name': 'area'}).get('value')
        koordinat = form.find('input', {'name': 'koordinat'}).get('value')
        status = form.find('input', {'name': 'status'}).get('value')

        if waktu:
            waktu = waktu.split('.')
            waktu = waktu[0]

            utc_datetime = timezone.datetime.strptime(
                waktu,
                '%Y/%m/%d %H:%M:%S'
            )

            local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
            local_datetime = local_datetime.astimezone(local_timezone)

            checker = Disaster.objects \
                .filter(
                    Q(title=area),
                    Q(occur_at=local_datetime),
                    Q(eav__dis108_status__isnull=False)
                    & Q(eav__dis108_status='preliminary')
                )

            if local_datetime > last_saved_dt and not checker.exists():
                data = {
                    'title': area,
                    'occur_at': local_datetime,
                    'source': 'BMKG',
                    'identifier': Disaster._Identifier.DIS108,
                }

                obj = Disaster(**data)
                disaster_objs.append(obj)

                # collect attribute
                attrdata = {
                    'dis108_epicenter_latitude': lintang,
                    'dis108_epicenter_longitude': bujur,
                    'dis108_magnitude': mag,
                    'dis108_depth': dalam,
                    'dis108_status': status,
                }
                disaster_attributes[index].append(attrdata)

                # collect location
                obj = DisasterLocation(latitude=lintang, longitude=bujur,)
                location_objs[index].append(obj)

    if len(disaster_objs) > 0:
        # sorted by occur_at
        new_disaster_objs = sorted(disaster_objs, key=lambda d: d.occur_at)

        try:
            Disaster.objects.bulk_create(
                new_disaster_objs,
                ignore_conflicts=False
            )
        except Exception as e:
            print(e)

    latest_disaster_objs = Disaster.objects \
        .order_by('-id')[:len(disaster_objs)]

    for index, obj in enumerate(latest_disaster_objs):
        # set attribute
        if len(disaster_attributes) > 0:
            attributes = disaster_attributes[index][0]
            model_name = obj._meta.model_name
            model_ct = ContentType.objects.get(model=model_name)

            for key in attributes:
                value = attributes[key]
                datatype = Attribute.TYPE_FLOAT

                if 'status' in key:
                    datatype = Attribute.TYPE_TEXT

                attr, _created = Attribute.objects.get_or_create(
                    name=key,
                    slug=key,
                    datatype=datatype
                )

                attr.entity_ct.set([model_ct])
                setattr(obj.eav, key, value)

            obj.eav.save()

        # set location
        if len(location_objs) > 0:
            locations = location_objs[index]
            for loc in locations:
                setattr(loc, 'disaster', obj)

            try:
                DisasterLocation.objects.bulk_create(
                    locations,
                    ignore_conflicts=True
                )
            except Exception as e:
                print(e)
