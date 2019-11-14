from django.db import models
from django.conf import settings

# Create your models here.
class Hashtag(models.Model):
  content = models.TextField(unique=True)

  def __str__(self):
    return self.content

class Photo(models.Model):
  photo = models.ImageField()
  content = models.TextField()
  longitude = models.FloatField()
  latitude = models.FloatField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_articles', blank=True)
  hashtags = models.ManyToManyField(Hashtag, blank=True)

  def __str__(self):
    return f'[{self.pk}] {self.photo}'

class Comment(models.Model):
  photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  content = models.TextField(max_length=300)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-pk',]

  def __str__(self):
    return self.content  