from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.EmailField()
    recipient = models.EmailField()
    topic = models.CharField(max_length=255)
    text = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    folder = models.CharField(max_length=30, choices=[
        ("inbox", "Входящие"),
        ("sent", "Отправленные"),
        ("archive", "Архив"),
        ("trash", "Корзина")
    ], default="inbox")
    previous_folder = models.CharField(max_length=30, blank=True, null=True)

