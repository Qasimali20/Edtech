from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    time_limit = models.DurationField()  # Time limit in minutes
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    content = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)  # Assume 'A', 'B', 'C', 'D'
    difficulty_level = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content[:50]

class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)  # Allow null values
    end_time = models.DateTimeField(null=True, blank=True)    # Allow null values
    score = models.IntegerField(null=True, blank=True)        # Allow null values
    created_at = models.DateTimeField(default=timezone.now)

class UserAnswer(models.Model):
    user_test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # Assume 'A', 'B', 'C', 'D'
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)

class UserPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    difficulty_level = models.IntegerField()
    correct_answers = models.IntegerField()
    incorrect_answers = models.IntegerField()
    adaptive_score = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update timestamp on save
