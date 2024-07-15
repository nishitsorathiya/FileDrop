from django.db import models

class Drop(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='uploads/')
    code = models.CharField(max_length=7)

    def __str__(self):
        return self.code
