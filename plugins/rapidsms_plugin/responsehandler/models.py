from django.db import models

# Create your models here.


class ParticipantModel(models.Model):
    instance_id = models.IntegerField(default=-1)
    phone_number = models.CharField(max_length=30)
    owner_id = models.IntegerField(default=-1)


class OwnerModel(models.Model):
    owner_id = models.IntegerField(default=-1)
    plugin_id = models.IntegerField(default=-1)
    token = models.CharField(max_length=200)
    url = models.CharField(max_length=255)