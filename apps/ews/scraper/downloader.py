import shutil  # to save it locally
import requests  # to get image from the web
import magic
import requests
import httplib2
import mimetypes
import io
import os
import urllib

from django.core.files.base import ContentFile

MAX_SIZE = 4*1024*1024
VALID_IMAGE_MIMETYPES = ["image"]
VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]


def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    # http://stackoverflow.com/a/10543969/396300
    return any([url.endswith(e) for e in extension_list])


def valid_url_mimetype(url, mimetype_list=VALID_IMAGE_MIMETYPES):
    # http://stackoverflow.com/a/10543969/396300
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return any([mimetype.startswith(m) for m in mimetype_list])
    else:
        return False


def image_exists(domain, path, url):
    # http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
    scheme = urllib.parse.urlparse(url).scheme

    try:
        conn = httplib2.HTTPConnection('{}//{}'.format(scheme, domain))
        conn.request('HEAD', path)
        response = conn.getresponse()
        conn.close()
    except:
        return False

    return response.status == 200


def retrieve_image(url):
    response = requests.get(url)
    return io.StringIO(response.content)


def get_mimetype(fobject):
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(fobject.read(1024))
    fobject.seek(0)
    return mimetype


def valid_image_mimetype(fobject):
    # http://stackoverflow.com/q/20272579/396300
    mimetype = get_mimetype(fobject)
    if mimetype:
        return mimetype.startswith('image')
    else:
        return False


def valid_image_size(image, max_size=MAX_SIZE):
    width, height = image.size
    if (width * height) > max_size:
        return (False, "Image is too large")
    return (True, image)


def split_url(url):
    parse_object = urllib.parse.urlparse(url)
    return parse_object.netloc, parse_object.path


def get_url_tail(url):
    return url.split('/')[-1]


def get_extension(filename):
    return os.path.splitext(filename)[1]


def pil_to_django(image, format="JPEG"):
    # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
    fobject = io.StringIO.StringIO()
    image.save(fobject, format=format)
    return ContentFile(fobject.getvalue())


# Importing Necessary Modules
