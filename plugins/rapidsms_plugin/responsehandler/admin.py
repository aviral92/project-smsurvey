from django.contrib import admin

# Register your models here.
from .models import ParticipantModel
admin.site.register(ParticipantModel)
from .models import OwnerModel
admin.site.register(OwnerModel)