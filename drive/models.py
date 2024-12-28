from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="subfolders")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class File(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
