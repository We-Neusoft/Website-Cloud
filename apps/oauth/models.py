#coding=utf-8
from django.contrib.auth.models import User
from django.db import models

from django_uuid_pk.fields import UUIDField

class Client(models.Model):
    id = UUIDField(primary_key=True)
    admin = models.ForeignKey(User, verbose_name=u'管理员')
    name = models.CharField(u'应用名', max_length=32)
    client_id = models.SlugField(u'应用ID', max_length=30)
    client_secret = UUIDField(auto=True, verbose_name=u'密钥')

    def __unicode__(self):
        return self.client_id

    class Meta:
        verbose_name = u'应用端'
        verbose_name_plural = u'应用端'

class RedirectionUri(models.Model):
    client = models.ForeignKey(Client, verbose_name=u'应用端')
    redirect_uri = models.URLField(u'地址')

    class Meta:
        verbose_name = u'跳转地址'
        verbose_name_plural = u'跳转地址'

class AuthorizationCode(models.Model):
    client = models.ForeignKey(Client, verbose_name=u'应用端')
    user = models.ForeignKey(User, verbose_name=u'鉴权用户')
    code = UUIDField(auto=True, verbose_name=u'鉴权码')
    redirect_uri = models.URLField(u'地址')
    expire_time = models.DateTimeField(u'过期时间')

    class Meta:
        verbose_name = u'鉴权码'
        verbose_name_plural = u'鉴权码'

class AccessToken(models.Model):
    client = models.ForeignKey(Client, verbose_name=u'应用端')
    user = models.ForeignKey(User, verbose_name=u'鉴权用户')
    code = UUIDField(unique=True, verbose_name=u'鉴权码')
    token = UUIDField(auto=True, verbose_name=u'访问令牌')
    expire_time = models.DateTimeField(u'过期时间')

    class Meta:
        verbose_name = u'访问令牌'
        verbose_name_plural = u'访问令牌'
