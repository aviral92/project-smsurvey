from django.db import models

# Create your models here.


class Participant(models.Model):
    instance_id = models.IntegerField
    phone_number = models.CharField(max_length=30)