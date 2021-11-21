import logging
import os
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import transaction, IntegrityError
from django.core.files.base import ContentFile

from core.constant import HazardClassify

# Get an instance of a logger
logger = logging.getLogger(__name__)


class GenericObjSet(object):
    @transaction.atomic
    def set_impacts(self, impacts, locations_obj):
        for index, location in enumerate(locations_obj):
            ct = ContentType.objects.get_for_model(location)
            impacts_data = impacts.get(index, None)
            impacts_obj = list()

            if impacts_data:
                for data in impacts_data:
                    kwargs = {
                        'content_type': ct,
                        'object_id': location.id,
                    }

                    uid = data.pop('uuid', None)
                    if uid:
                        kwargs.update({'uuid': uid})

                    try:
                        o, _created = location.impacts.filter(uuid=uid).update_or_create(
                            defaults=data,
                            **kwargs
                        )
                    except IntegrityError as e:
                        logger.error(e)

                    impacts_obj.append(o)

                if len(impacts_obj) > 0:
                    sorted_impacts_obj = sorted(
                        impacts_obj, key=lambda d: d.id
                    )

                    location.impacts.set(sorted_impacts_obj)

    @transaction.atomic
    def set_locations(self, locations):
        locations_obj = list()
        ct = ContentType.objects.get_for_model(self)

        # extract and remove `impacts` from `locations`
        impacts = {
            i: v for i, v in enumerate([o.pop('impacts', None) for o in locations]) if v and len(v) > 0
        }

        for data in locations:
            kwargs = {
                'content_type': ct,
                'object_id': self.id,
            }

            uid = data.pop('uuid', None)
            if uid:
                kwargs.update({'uuid': uid})

            o, _create = self.locations.filter(uuid=uid).update_or_create(
                defaults=data,
                **kwargs
            )

            locations_obj.append(o)

        # `impacts` created after `locations` created
        sorted_locations_obj = sorted(locations_obj, key=lambda d: d.id)
        self.set_impacts(impacts, sorted_locations_obj)

        # set `locations` to instance
        self.locations.set(sorted_locations_obj)

        # set `earthquake` location
        if len(sorted_locations_obj) > 0:
            self.set_eartquake_value(location=sorted_locations_obj[0])

    def verify_attachments(self, attachments):
        return [
            x for x in attachments if x.activities.first().user.id == self.activities.first().user.id
        ]

    @transaction.atomic
    def set_eartquake_value(self, **kwargs):
        from apps.threat.models import DISASTER_CLASSIFY_MODEL_MAPPER as mapper

        # only for earthquake
        # set `latitude` and `longitude` as epicentrum
        if hasattr(self, 'classify') and self.classify == HazardClassify.HAC105:
            location = kwargs.get('location', None)
            data = dict()

            if location:
                data.update({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                })

            disaster_model = mapper.get(self.classify, None)
            model_name = disaster_model._meta.model_name

            # but make sure it has activities
            # indicate submit by user, not scraper
            if disaster_model and self.activities.filter(user__isnull=False).exists() and hasattr(self, model_name) and data:
                try:
                    obj = disaster_model.objects.filter(hazard_id=self.id)
                    if obj.exists():
                        obj.update(**data)
                except FieldError as e:
                    print(e)

    @transaction.atomic
    def set_attachments(self, attachments, bypass_verification=False):
        attachments_obj = list()

        if not bypass_verification:
            attachments = self.verify_attachments(attachments)

        # attachments without `hazard`
        attachments_without_hazard = [
            x for x in attachments if not x.hazard.exclude(id=self.id).exists()
        ]

        # attachments with `hazard`
        attachments_with_hazard = [
            x for x in attachments if x.hazard.exclude(id=self.id).exists()
        ]

        if len(attachments_without_hazard) > 0:
            attachments_obj.extend(attachments_without_hazard)

        # create new attachments if they has `hazard`
        if len(attachments_with_hazard) > 0:
            new_attachments = list()

            # just copied it then reupload file
            for attachment in attachments_with_hazard:
                filename = os.path.basename(attachment.filename)

                attachment.pk = None
                attachment.uuid = uuid.uuid4()
                attachment.file = ContentFile(
                    attachment.file.read(),
                    filename
                )

                attachment.save()
                new_attachments.append(attachment)

                # don't forget create `activity`
                attachment.activities.create(
                    user=self.activities.first().user
                )

            # set as new attachments
            attachments_obj.extend(new_attachments)

        if len(attachments_obj) > 0:
            self.attachments.set(attachments_obj)
