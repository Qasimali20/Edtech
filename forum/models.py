from django.db import models
from django.contrib.auth.models import User
from .utils import detect_sentiment  # Make sure this is the updated function

from django.db import models
from django.contrib.auth.models import User
from .utils import detect_sentiment  # Ensure this function is updated

class Thread(models.Model):
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=10, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Analyze sentiment of the thread title
        self.sentiment_score, self.sentiment_label = detect_sentiment(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=10, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.sentiment_score, self.sentiment_label = detect_sentiment(self.content)
        if self.sentiment_label == "negative":
            # Do not save if sentiment is negative
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=10, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.sentiment_score, self.sentiment_label = detect_sentiment(self.content)
        if self.sentiment_label == "negative":
            # Do not save if sentiment is negative
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'
