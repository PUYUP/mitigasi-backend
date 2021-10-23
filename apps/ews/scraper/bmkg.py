import pytz
import requests
import json

from datetime import datetime
from django.utils import timezone


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

    for item in gempa:
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
        shakemap_img = '{}{}.mmi.jpg'.format(shakemap_base_url, shakemap)

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
        print(locations)
