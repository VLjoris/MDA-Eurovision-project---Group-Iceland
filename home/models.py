# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Features(models.Model):
    code = models.TextField(db_column='Code', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    continent = models.TextField(blank=True, null=True)
    langoff_1 = models.TextField(blank=True, null=True)
    lat = models.TextField(blank=True, null=True)
    lon = models.TextField(blank=True, null=True)
    colonizer1 = models.TextField(blank=True, null=True)
    religion = models.TextField(db_column='Religion', blank=True, null=True)  # Field name made lowercase.
    immigrants = models.TextField(db_column='Immigrants', blank=True, null=True)  # Field name made lowercase.
    country_border_code = models.TextField(blank=True, null=True)
    utc_offset = models.TextField(db_column='UTC_offset', blank=True, null=True)  # Field name made lowercase.
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_features'


class MeanScores(models.Model):
    from_country = models.TextField(db_column="From country_iso2",blank=True, null=True)
    to_country = models.TextField(db_column="To country_iso2",blank=True, null=True)
    points = models.TextField(db_column="Points",blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_meanscores'

class Tele(models.Model):
    from_country = models.TextField(blank=True, null=True)
    to_country = models.TextField(blank=True, null=True)
    jury_or_voting = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    voted = models.TextField(blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_televoting'

class JuRy(models.Model):
    from_country = models.TextField(blank=True, null=True)
    to_country = models.TextField(blank=True, null=True)
    jury_or_voting = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    voted = models.TextField(blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_juryvoting'

class MeanScoresByYear(models.Model):
    year = models.TextField(db_column="Year",blank=True, null=True)
    to_country = models.TextField(db_column="To country_iso2",blank=True, null=True)
    points = models.TextField(db_column="Points",blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_meanscoresbyyear'        

class ISO(models.Model):
    code = models.TextField(db_column='Code', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(db_column="Name",blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'home_iso'    

#https://github.com/jmeichle/django_graphs/tree/master/graphs

#https://pypi.org/project/django-netjsongraph/