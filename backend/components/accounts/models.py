from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import models
from django.contrib.auth.models import User


class ProfilePicture(models.Model):
    profile_picture = models.ImageField(storage=S3Boto3Storage(), null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_avatar_url(self):
        if self.profile_picture:
            return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{self.profile_picture.name}"
        return None

    class Meta:
        app_label = 'accounts'
