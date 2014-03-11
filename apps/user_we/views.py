from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode

import json
from libs import oauth_server

def get_info(request):
    user = oauth_server.authorize(request.META.get('HTTP_AUTHORIZATION'))

    if user is None:
        return HttpResponse(None)

    return HttpResponse(json.dumps({'user_id': urlsafe_base64_encode(user.id.bytes)}))

def get_privacy(request):
    user = oauth_server.authorize(request.META.get('HTTP_AUTHORIZATION'))

    if user is None:
        return HttpResponse(None)

    return HttpResponse(json.dumps({'email': user.user.email}))
