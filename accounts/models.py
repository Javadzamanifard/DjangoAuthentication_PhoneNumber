from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from datetime import timedelta

import random 


class CustomUser(AbstractUser):
    usable_password = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=('شماره همراه'))
    is_phone_verified = models.BooleanField(default=False, verbose_name=('فعال بودن'))
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    
    def otp_generate(self):
        otp = str(random.randint(100000, 999999))
        self.otp_code = otp
        self.otp_expiry = timezone.now() + timedelta(minutes=2)
        self.save()
        return otp
    
    def __str__(self):
        return self.phone_number

