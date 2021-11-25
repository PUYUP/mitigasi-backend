from django.db import models


class AbstractProvinces(models.Model):
    prov_id = models.IntegerField(primary_key=True, db_index=True)
    prov_name = models.CharField(max_length=255, db_index=True)
    locationid = models.IntegerField(db_index=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'territory_provinces'
        abstract = True

    def __str__(self) -> str:
        return self.prov_name


class AbstractCities(models.Model):
    city_id = models.IntegerField(primary_key=True, db_index=True)
    city_name = models.CharField(max_length=255, db_index=True)
    prov_id = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'territory_cities'
        abstract = True

    def __str__(self) -> str:
        return self.city_name


class AbstractDistricts(models.Model):
    dis_id = models.IntegerField(primary_key=True, db_index=True)
    dis_name = models.CharField(max_length=255, db_index=True)
    city_id = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'territory_districts'
        abstract = True

    def __str__(self) -> str:
        return self.dis_name


class AbstractSubDistricts(models.Model):
    subdis_id = models.IntegerField(primary_key=True, db_index=True)
    subdis_name = models.CharField(max_length=255, db_index=True)
    dis_id = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'territory_subdistricts'
        abstract = True

    def __str__(self) -> str:
        return self.subdis_name
