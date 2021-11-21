import re
import requests
import os
import shutil
import requests

from core.constant import HazardClassify
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import transaction

# from gevent import monkey as curious_george
# curious_george.patch_all(thread=False, select=False)


Attachment = apps.get_registered_model('generic', 'Attachment')
Hazard = apps.get_registered_model('threat', 'Hazard')
Earthquake = apps.get_registered_model('threat', 'Earthquake')


@transaction.atomic
def twitter(param={}, request=None):
    token = 'AAAAAAAAAAAAAAAAAAAAAMrwVwEAAAAAIElf4b0g3g6TLI9vmUOqH%2FMLqno%3DgXRvqwhVwZn8wqBe6ZgBTOiYBiFm6QbxTIUpvuzRoEEHXFAJA8'
    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json"
    }

    urls = list()
    accounts = [
        'bmkgwilayah2',
        'bmkgjogja',
        'infoBMKGMaluku',
        'bmkgpapua',
        'bmkgpadangpjg',
        'stageof_TPTI',
        'bmkgpriok',
        'bbMKG3',
        'BMKGSulsel',
        'StasiunAlor',
        'stageof_mataram',
        'StaklimJogja',
        'infoBMKG',
    ]

    for account in accounts:
        url = 'https://api.twitter.com/2/tweets/search/recent?query=from:%s+has:media+info gempa&expansions=attachments.media_keys,author_id&media.fields=url' % account
        urls.append(url)

    rs = (requests.get(u, headers=headers) for u in urls)

    for r in rs:
        res = r.json()
        data = res.get('data')
        includes = res.get('includes', {})
        media = includes.get('media')
        users = includes.get('users')

        if data and len(data) > 0:
            data_cleanest = [
                {
                    'text': re.sub(r'http\S+', '', t.get('text'), flags=re.MULTILINE),
                    'attachment_id': t.get('attachments', {}).get('media_keys')[0],
                    'photo_url': next((x for x in media if x.get('media_key') == t.get('attachments', {}).get('media_keys')[0]), {}).get('url'),
                    'user': next((x for x in users if x.get('id') == t.get('author_id')), {}).get('name'),
                } for t in data
            ]

            for d in data_cleanest:
                text = d.get('text')
                text_lower = text.lower()
                photo_url = d.get('photo_url')
                user = d.get('user')

                # magnitude
                mag = text_lower.split(',')[0].replace(' ', '')
                mag = float(re.search(r'\d+', mag).group())

                # location
                loc = text_lower.split('lok:')[1]
                loc_ls = loc.split('ls')[0]
                loc_bt = loc.split('bt')[0]

                try:
                    loc_bt_a = loc_bt.split('-')[1]
                except IndexError as e:
                    loc_bt_a = None

                try:
                    loc_bt_b = loc_bt.split(',')[1]
                except IndexError as e:
                    loc_bt_b = None

                ls = loc_ls.replace(' ', '')
                bt = loc_bt_a or loc_bt_b
                bt = bt.replace(' ', '')

                # depth
                try:
                    depth_a = text_lower.split('kedalaman')[1]
                except IndexError as e:
                    depth_a = None

                try:
                    depth_b = text_lower.split('kedlmn')[1]
                except IndexError as e:
                    depth_b = None

                depth = depth_a or depth_b
                depth_float = 0

                if depth:
                    depth_float = float(re.search(r'\d+', depth).group())

                earthquake_defaults = {
                    'latitude': float('-%s' % float(ls)),
                    'longitude': float(bt),
                    'magnitude': mag,
                    'depth': depth_float
                }

                data = {
                    'source': user,
                    'classify': HazardClassify.HAC105,
                    'incident': text
                }

                hazard_obj, created = Hazard.objects.update_or_create(**data)

                Earthquake.objects.update_or_create(
                    hazard=hazard_obj,
                    defaults=earthquake_defaults
                )

                # Attachments
                if photo_url:
                    # Set up the image URL and filename
                    filename = photo_url.split("/")[-1]

                    # Open the url image, set stream to True, this will return the stream content.
                    r = requests.get(photo_url, stream=True)
                    attachments = list()

                    # Check if the image was retrieved successfully
                    if r.status_code == 200:
                        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                        r.raw.decode_content = True

                        # Retrieve file from root path
                        filepath = os.path.join(
                            settings.PROJECT_PATH, filename)

                        # Open a local file with wb ( write binary ) permission.
                        with open(filename, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)

                        with open(filepath, 'rb') as f:
                            fobj = File(f)
                            attachment = Attachment.objects \
                                .create(identifier='shakemap')
                            attachment.file.save(filename, fobj)
                            attachments.append(attachment)

                        if len(attachments) > 0:
                            hazard_obj.set_attachments(attachments, True)

                        # delete unused file
                        if os.path.exists(filepath):
                            os.remove(filepath)
