from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    following = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    def __str__(self):
        return self.username

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="posted_by"
    )

    def __str__(self):
        return self.title

class Like(models.Model):
    target = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes_received"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="likes_by"
    )

class Tag(models.Model):
    name = models.CharField(max_length=20)
    post = models.ManyToManyField(Post, related_name="tags")

    def __str__(self):
        return self.name