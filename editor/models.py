from django.db import models

class DropboxAccessToken(models.Model):
    key = models.CharField(max_length=50, unique=True)
    access_token = models.CharField(max_length=1024)
