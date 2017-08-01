from django.db import models

# Create your models here.


class ParticipantModel(models.Model):
    instance_id = models.IntegerField(default=-1)
    phone_number = models.CharField(max_length=30)
