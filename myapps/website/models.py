from django.db import models

class ContactMethod(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('line', 'Line'),
        ('wechat', 'WeChat'),
        ('telegram', 'Telegram'),
    ]
    
    contact_type = models.CharField(
        max_length=10,
        choices=CONTACT_TYPE_CHOICES,
        default='line',
    )
    contact_id = models.CharField(max_length=255)
    contact_url = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)  # Optional field for phone number

    def __str__(self):
        return f"{self.get_contact_type_display()} - {self.name} ({self.contact_id})"