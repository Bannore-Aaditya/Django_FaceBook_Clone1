from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_images', default='blank_profile_pic.png')
    location = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField(blank=True)
    created = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
   post_id = models.CharField(max_length=120, blank=True)
   username = models.CharField(max_length=120, blank=True)

class FollowerCount(models.Model):
    followers = models.CharField(max_length=120, blank=True)
    user = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user
