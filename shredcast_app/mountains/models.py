from django.db import models

class Mountain(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255) # Format: 1111 Somestreet Way, Somecity, AB 11111
    latitude = models.FloatField()
    longitude = models.FloatField()
    google_place_id = models.CharField(max_length=255, default='')
    snocountry_id = models.CharField(max_length=255, default='')
