import uuid
import datetime
import posixpath

from django.db import models
from django.conf import settings


class AbstractCommonField(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_image_upload_path(instance, filename):
    return posixpath.join(datetime.datetime.now().strftime(settings.IMAGE_FOLDER), filename)
