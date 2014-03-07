#coding=utf-8
from django.contrib.auth.models import User
from django.db import models

from django_uuid_pk.fields import UUIDField

class User(models.Model):
    id = UUIDField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=u'用户')

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
