import requests

from django.utils import timezone
from django.apps import apps

from bs4 import BeautifulSoup
from collections import defaultdict
from core.constant import DisasterIdentifier

Disaster = apps.get_registered_model('ews', 'Disaster')
DisasterLocation = apps.get_registered_model('ews', 'DisasterLocation')


def tup_to_dict(tup, dict):
    for x, y in tup:
        dict.setdefault(y.lower(), []).append(x)
    return dict


def dibi(param):
    ALL = False
    URL = "https://dibi.bnpb.go.id/xdibi"
    identifier = param.get('identifier', '')

    param = {
        'pr': '',
        'kb': '',
        'jn': identifier,
        'th': '',
        'bl': '',
        'tb': 2,
        'st': 3,
        'start': param.get('start', 0)
    }
    page = requests.get(URL, params=param, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id='mytabel').findChildren('tr')
    hrefs = list()
    incidents = list()

    # last saved disaster
    last_saved = Disaster.objects \
        .filter(identifier=identifier) \
        .order_by('-id').last()
    last_srapped = last_saved.occur_at if last_saved else None

    dictionary = {}
    disaster_incidents = tup_to_dict(DisasterIdentifier.choices, dictionary)

    for tr in results:
        # get href
        _href = None
        _a = tr.find('a', {'title': 'Detail Bencana'})
        if _a:
            _href = _a['href']

        # get incident name
        _incident = tr.findAll('td')[3::3]
        if len(_incident) > 0:
            _name = _incident[0].get_text().lower()
            _code = disaster_incidents.get(_name)

            d = {
                'label': _name,
                'code': _code[0],
            }
            incidents.append(d)

        # by date
        _date = tr.findAll('td')[1::1]
        if len(_date) > 0:
            x = _date[0]
            year = x.find('span', {'title': 'Tahun'}).get_text()
            month = x.find('span', {'title': 'Bulan'}).get_text()
            day = x.find('span', {'title': 'Tanggal'}).get_text()
            date = timezone.datetime(int(year), int(month), int(day)).date()
            today = timezone.datetime.today().date()

            if _href:
                if ALL and last_srapped.date() < today:
                    hrefs.append(_href)
                else:
                    if today == date:
                        hrefs.append(_href)

    disaster_objs = list()
    locations = list()

    # check has new data
    if len(hrefs) <= 0:
        return None

    for index, href in enumerate(hrefs):
        url = requests.get(href, verify=False)
        soup = BeautifulSoup(url.content, "html.parser")
        incident_identifier = incidents[index]

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

        locality = defaultdict(list)
        sub_locality = defaultdict(list)

        location = {
            'latitude': latitude,
            'longitude': longitude,
            'administrative_area': {
                'name': prop_name,
                'code': prop_code,
            },
            'sub_administrative_area': {
                'name': kab_name,
                'code': kab_code,
            },
        }

        states = soup.find(id='hal3').find_all('li')
        kec_name = None
        kec_code = None
        des_name = None
        des_code = None

        for state in states:
            state_name = state.get_text()
            state_name_list = state_name.split('.')

            # kecamatan
            locality[kab_code]

            if 'Kec.' in state_name:
                kec_name = state_name_list[2].strip()
                kec_code = state_name_list[0].strip()

                locality[kab_code].append({
                    'name': kec_name,
                    'code': kec_code,
                })

            location.update({
                'locality': locality
            })

            # desa
            sub_locality[kec_code]

            if 'Desa' in state_name:
                des_name = state_name_list[1].replace('Desa', '').strip()
                des_code = state_name_list[0].strip()

                sub_locality[kec_code].append({
                    'name': des_name,
                    'code': des_code,
                })

            location.update({
                'sub_locality': sub_locality
            })

        disaster_obj = Disaster(
            identifier=incident_identifier.get('code'),
            title=nama_kejadian,
            occur_at=tgl,
            source=sumber,
            description=keterangan,
            reason=penyebab,
            chronology=kronologis
        )

        disaster_objs.append(disaster_obj)
        locations.append(location)

    # insert disaster to database
    if len(disaster_objs) > 0:
        try:
            Disaster.objects.bulk_create(disaster_objs, ignore_conflicts=False)
        except Exception as e:
            print(e)

        total = len(locations)
        disaster_location_objs = list()
        latest_disaster_objs = Disaster.objects.order_by('-id')[:10]

        for index, item in enumerate(latest_disaster_objs):
            x = (total - index) - 1

            try:
                y = locations[x]
            except IndexError:
                y = None

            if y:
                latitude = y.get('latitude')
                longitude = y.get('longitude')
                level_1 = y.get('administrative_area')
                level_2 = y.get('sub_administrative_area')
                level_3 = y.get('locality')
                level_4 = y.get('sub_locality')

                _l1_name = level_1.get('name')
                _l1_code = level_1.get('code')

                _l2_name = level_2.get('name')
                _l2_code = level_2.get('code')

                _common_location = {
                    'disaster': item,
                    'country': 'Indonesia'.upper(),
                    'country_code': 'ID',

                    'latitude': latitude,
                    'longitude': longitude,

                    'administrative_area': _l1_name.upper(),
                    'administrative_area_code': _l1_code,

                    'sub_administrative_area': _l2_name.upper(),
                    'sub_administrative_area_code': _l2_code,
                }

                if level_3:
                    for l3 in level_3.get(_l2_code):
                        _l3_code = l3.get('code')
                        l4 = level_4.get(_l3_code)

                        if not l4:
                            location_obj = DisasterLocation(
                                **_common_location,

                                locality=l3.get('name'),
                                locality_code=_l3_code,
                            )

                            disaster_location_objs.append(location_obj)
                        else:
                            for _l4 in l4:
                                _l4_code = _l4.get('code')
                                location_obj = DisasterLocation(
                                    **_common_location,

                                    locality=l3.get('name'),
                                    locality_code=_l3_code,

                                    sub_locality=_l4.get('name'),
                                    sub_locality_code=_l4_code,
                                )

                                disaster_location_objs.append(location_obj)
                else:
                    location_obj = DisasterLocation(**_common_location)
                    disaster_location_objs.append(location_obj)

        # insert disaster location
        if len(disaster_location_objs) > 0:
            try:
                DisasterLocation.objects.bulk_create(
                    disaster_location_objs,
                    ignore_conflicts=False
                )
            except Exception as e:
                print(e)

    return True
