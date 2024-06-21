from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class ExtractedText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"Extracted text for {self.user.username}"
    
class SummaryText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"Summarized text for {self.user.username}"
