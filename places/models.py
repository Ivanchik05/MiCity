from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Place(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='places/')

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    section_id = models.CharField(max_length=50, unique=True)  # e.g., 'history', '17century'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LikeDislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{"Like" if self.is_like else "Dislike"} by {self.user.username} on {self.post.title}'
