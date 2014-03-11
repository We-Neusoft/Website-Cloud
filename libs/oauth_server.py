#encoding=utf-8
from django.utils.http import urlsafe_base64_decode

import datetime
from uuid import UUID

from apps.oauth.models import Client, AccessToken
from apps.user_we.models import User

def authorize(authorization):
    if not authorization:
        return None

    method, credentials = authorization.split(' ')
    # 验证Basic方式
    if method.lower() == 'basic':
        client_id, client_secret = credentials.decode('base64').split(':')
        try:
            return Client.objects.get(client_id=client_id, client_secret=UUID(bytes=urlsafe_base64_decode(client_secret)))
        except (ValueError, Client.DoesNotExist):
            return None
    if method.lower() == 'bearer':
        try:
            access_token = AccessToken.objects.filter(expire_time__gte=datetime.datetime.now()).get(token=UUID(bytes=urlsafe_base64_decode(credentials)))
        except AccessToken.DoesNotExist:
            return None

        client = access_token.client
        user = access_token.user
        try:
            return User.objects.get(user=user, client=client)
        except User.DoesNotExist:
            user = User(client=client, user=user)
            user.save()
            return user
    else:
        return None
