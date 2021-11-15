import requests

from django.utils import timezone
from django.apps import apps
from django.db import transaction

from bs4 import BeautifulSoup
from collections import defaultdict

Hazard = apps.get_registered_model('threat', 'Hazard')


def tup_to_dict(tup, dict):
    for x, y in tup:
        dict.setdefault(y.lower(), []).append(x)
    return dict


@transaction.atomic
def dibi(param={}, request=None):
    ALL = False
    URL = "https://dibi.bnpb.go.id/xdibi"

    classify = param.get('classify', '')  # default scrape all
    start = param.get('start', 0)
    fetch = param.get('fetch', None)

    if request and request.user.is_superuser and fetch == 'all':
        ALL = True

    param = {
        'pr': '',
        'kb': '',
        'jn': classify,
        'th': '',
        'bl': '',
        'tb': 2,
        'st': 3,
        'start': start
    }
    page = requests.get(URL, params=param, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id='mytabel').findChildren('tr')
    permalinks = list()

    # extract permalink from href
    for tr in results:
        href = None
        a_tag = tr.find('a', {'title': 'Detail Bencana'})
        if a_tag:
            href = a_tag['href']

        if href:
            permalinks.append(href)

    # crawling each permalink
    for index, permalink in enumerate(permalinks):
        url = requests.get(permalink, verify=False)
        soup = BeautifulSoup(url.content, "html.parser")

        nama_kejadian = soup.find(id='nama_kejadian').get('value')
        latitude = soup.find(id='latitude').get('value')
        longitude = soup.find(id='longitude').get('value')
        keterangan = soup.find(id='keterangan').get_text()
        sumber = soup.find(id='sumber').get('value')
        tgl = soup.find(id='tgl').get('value')
        id_jenis_bencana = soup.find(id='id_jenis_bencana').get('value')
        prop = soup.find_all('input', {'name': 'prop'})[0].get('value')
        kab = soup.find_all('input', {'name': 'kab'})[0].get('value')
        penyebab = soup.find(id='penyebab').get_text()
        kronologis = soup.find(id='kronologis').get_text()

        # province name and code
        prop_list = prop.split('.')
        prop_name = prop_list[1].strip()
        prop_code = prop_list[0].strip()

        # city name and code
        kab_list = kab.split('.')
        kab_name = kab_list[1].strip()
        kab_code = kab_list[0].strip()

        # start Hazard create
        # get classify from source
        classify = id_jenis_bencana.split('.')[0].replace(' ', '')
        classify_mapper = None

        if classify == '101':
            classify_mapper = '101'
        elif classify == '102':
            classify_mapper = '103'
        elif classify == '103':
            classify_mapper = '106'
        elif classify == '105':
            classify_mapper = '102'
        elif classify == '106':
            classify_mapper = '107'
        elif classify == '107':
            classify_mapper = '104'
        elif classify == '108':
            classify_mapper = '105'
        elif classify == '109':
            classify_mapper = '108'
        elif classify == '111':
            classify_mapper = '109'
        elif classify == '999':
            classify_mapper = '999'

        # hazard data
        hazard_data = {
            'classify': classify_mapper,
            'incident': nama_kejadian,
            'description': keterangan,
            'source': sumber,
            'reason': penyebab,
            'chronology': kronologis,
            'occur_at': tgl,
        }

        hazard_obj, created = Hazard.objects.update_or_create(**hazard_data)

        # set locations
        locations_data = [
            {
                'administrative_area': prop_name,
                'administrative_area_code': prop_code,
                'sub_administrative_area': kab_name,
                'sub_administrative_area_code': kab_code,
                'latitude': latitude,
                'longitude': longitude
            }
        ]

        hazard_obj.set_locations(locations_data)
