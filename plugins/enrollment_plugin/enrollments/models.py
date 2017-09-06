from django.db import models

# Create your models here.


class OwnerModel(models.Model):
    owner_id = models.IntegerField(default=-1)
    plugin_id = models.IntegerField(default=-1)
    token = models.CharField(max_length=200)
    url = models.CharField(max_length=255)


class EnrollmentModel(models.Model):
    owner_id = models.IntegerField(default=-1)
    plugin_id = models.IntegerField(default=-1)
    enrollment_id = models.IntegerField(default=-1)
    enrollment_name = models.CharField(max_length=25)
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
