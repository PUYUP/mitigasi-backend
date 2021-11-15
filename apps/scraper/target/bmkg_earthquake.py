import pytz
import requests
import requests  # to get image from the web
import shutil  # to save it locally
import os

from bs4 import BeautifulSoup
from collections import defaultdict

from django.db import transaction
from django.utils import timezone
from django.apps import apps
from django.core.files import File
from django.conf import settings

from core.constant import HazardClassify

Hazard = apps.get_registered_model('threat', 'Hazard')
Earthquake = apps.get_registered_model('threat', 'Earthquake')
Impact = apps.get_registered_model('generic', 'Impact')
Attachment = apps.get_registered_model('generic', 'Attachment')


@transaction.atomic
def quake_feeled():
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
    local_timezone = pytz.timezone('Asia/Jakarta')

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
        locations_clean = [
            loc.strip().replace(' - ', '-') for loc in locations
        ]

        # separate impact and location name
        impacts = [loc.split(' ')[0] for loc in locations_clean]

        sub_administrative_areas = list()
        for loc in locations_clean:
            REMOVE_WORDS = ['Des.', 'Kel.', 'Kec.', 'Kab.']
            for r in REMOVE_WORDS:
                loc = loc.replace(r, '').strip()

            l = loc.split(' ')
            l.pop(0)
            l = [i for i in l if i]

            sub_administrative_areas.append(' '.join(l))

        locations_data = []
        for index, area in enumerate(sub_administrative_areas):
            location_data = {
                'sub_administrative_area': area,
                'impacts': [
                    {
                        'identifier': Impact.Identifier.IDE102,
                        'value': impacts[index],
                        'metric': Impact.Metric.MET101
                    }
                ]
            }

            locations_data.append(location_data)

        disaster_data = {
            'occur_at': local_datetime,
            'description': location,
            'source': 'BMKG',
            'classify': HazardClassify.HAC105,
            'incident': description
        }

        hazard_obj, created = Hazard.objects.update_or_create(**disaster_data)

        # create `earthquake` object
        earthquake_defaults = {
            'depth': depth,
            'latitude': latitude,
            'longitude': longitude,
            'magnitude': magnitude
        }

        Earthquake.objects.update_or_create(
            hazard=hazard_obj,
            defaults=earthquake_defaults
        )

        # set `location` and `impact`
        hazard_obj.set_locations(locations_data)

        # Set up the image URL and filename
        filename = shakemap_url.split("/")[-1]

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(shakemap_url, stream=True)
        attachments = list()

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
                attachment = Attachment.objects.create(identifier='shakemap')
                attachment.file.save(filename, fobj)
                attachments.append(attachment)

            if len(attachments) > 0:
                hazard_obj.set_attachments(attachments, True)

            # delete unused file
            if os.path.exists(filepath):
                os.remove(filepath)


@transaction.atomic
def quake_recent():
    """
    Shakemap formula:
    <Datetime>+<Jam>

    Jam: 09:51:58 WIB
    Datetime: 2021-10-23T02:51:58+00:00
    Result: 20211023095158.mmi.jpg
    """
    url = 'https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json'
    r = requests.get(url)
    res = r.json()
    info_gempa = res.get('Infogempa', {})
    gempa = [info_gempa.get('gempa', {})]
    shakemap_base_url = 'https://data.bmkg.go.id/DataMKG/TEWS/'
    local_timezone = pytz.timezone('Asia/Jakarta')

    for index, item in enumerate(gempa):
        datetime = item.get('DateTime', timezone.now())
        coordinates = item.get('Coordinates', 0).split(',')
        latitude = item.get('Lintang', 0)
        longitude = item.get('Bujur', 0)
        magnitude = item.get('Magnitude', 0)
        depth = item.get('Kedalaman', 0)
        incident = item.get('Wilayah', '')
        location = item.get('Dirasakan', '')
        potency = item.get('Potensi', '')
        shakemap = item.get('Shakemap', '')

        utc_datetime = timezone.datetime.strptime(
            datetime,
            '%Y-%m-%dT%H:%M:%S+00:00'
        )

        local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
        local_datetime = local_datetime.astimezone(local_timezone)

        # shakemap
        shakemap_url = '{}{}'.format(shakemap_base_url, shakemap)

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
        locations_clean = [
            loc.strip().replace(' - ', '-') for loc in locations
        ]

        # separate impact and location name
        impacts = [loc.split(' ')[0] for loc in locations_clean]

        sub_administrative_areas = list()
        for loc in locations_clean:
            REMOVE_WORDS = ['Des.', 'Kel.', 'Kec.', 'Kab.']
            for r in REMOVE_WORDS:
                loc = loc.replace(r, '').strip()

            l = loc.split(' ')
            l.pop(0)
            l = [i for i in l if i]

            sub_administrative_areas.append(' '.join(l))

        locations_data = []
        for index, area in enumerate(sub_administrative_areas):
            location_data = {
                'sub_administrative_area': area,
                'impacts': [
                    {
                        'identifier': Impact.Identifier.IDE102,
                        'value': impacts[index],
                        'metric': Impact.Metric.MET101
                    }
                ]
            }

            locations_data.append(location_data)

        hazard_data = {
            'occur_at': local_datetime,
            'description': '{} {}'.format(location, potency),
            'source': 'BMKG',
            'classify': HazardClassify.HAC105,
            'incident': incident
        }

        hazard_obj, created = Hazard.objects.update_or_create(**hazard_data)

        # create `earthquake` object
        earthquake_defaults = {
            'depth': depth,
            'latitude': latitude,
            'longitude': longitude,
            'magnitude': magnitude
        }

        Earthquake.objects.update_or_create(
            hazard=hazard_obj,
            defaults=earthquake_defaults
        )

        # set `location` and `impact`
        hazard_obj.set_locations(locations_data)

        # Set up the image URL and filename
        filename = shakemap_url.split("/")[-1]

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(shakemap_url, stream=True)
        attachments = list()

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
                attachment = Attachment.objects.create(identifier='shakemap')
                attachment.file.save(filename, fobj)
                attachments.append(attachment)

            if len(attachments) > 0:
                hazard_obj.set_attachments(attachments, True)

            # delete unused file
            if os.path.exists(filepath):
                os.remove(filepath)
