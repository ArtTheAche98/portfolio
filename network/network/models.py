from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    content = models.TextField()
    image_url = models.URLField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts')

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    picture = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username