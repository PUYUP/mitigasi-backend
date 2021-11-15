import uuid
import datetime
import posixpath

from django.db import connections, models, transaction
from django.conf import settings
from django.db.models.fields import AutoField
from django.db.models import sql

from simple_history.models import HistoricalRecords


class AbstractCommonField(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(
        inherit=True,
        history_change_reason_field=models.TextField(null=True)
    )

    class Meta:
        abstract = True


class BulkCreateReturnIdManager(models.Manager):
    def dict_fetch_all(self, cursor):
        """Return all rows from a cursor as a dict"""
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    @transaction.atomic
    def bulk_create_return_id(self, objs, batch_size=2000):
        self._for_write = True
        fields = [
            f for f in self.model._meta.concrete_fields if not isinstance(f, AutoField)
        ]
        created_objs = []
        with transaction.atomic(using=self.db):
            with connections[self.db].cursor() as cursor:
                for item in [objs[i:i + batch_size] for i in range(0, len(objs), batch_size)]:
                    query = sql.InsertQuery(self.model)
                    query.insert_values(fields, item)
                    for raw_sql, params in query.get_compiler(using=self.db).as_sql():
                        cursor.execute(raw_sql, params)
                    raw = "SELECT * FROM %s WHERE id >= %s ORDER BY id DESC LIMIT %s" % (
                        self.model._meta.db_table, cursor.lastrowid, cursor.rowcount
                    )
                    cursor.execute(raw)
                    created_objs.extend(self.dict_fetch_all(cursor))

        return created_objs


def get_image_upload_path(instance, filename):
    return posixpath.join(datetime.datetime.now().strftime(settings.IMAGE_FOLDER), filename)
