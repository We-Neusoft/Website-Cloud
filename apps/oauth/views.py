#coding=utf8
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

import datetime, json
from uuid import UUID

from models import AccessToken, AuthorizationCode, Client, RedirectionUri
from forms import AuthenticationForm, InitializationForm, TokenForm

from libs import oauth_server
from environment import get_environment

def authorize(request):
    result = get_environment(request)
    result.update(csrf(request))

    # 验证是否为登录表单
    # TODO 当系统有初始化、登录以外的入口时，此处需要改进（SunFulong@2014-1-7）
    form = AuthenticationForm(request.POST)

    # 非登录表单，返回登录画面
    if not form.is_valid():
        # 验证应用端身份
        form, client = verify_client(request.REQUEST)
        if issubclass(form.__class__, HttpResponse):
            return form

        result.update({'name': client.name})
        request.session.set_expiry(0)
        request.session.update(form.cleaned_data)

        return render_to_response('oauth/authorize.html', result)
    # 是登录表单，进行相关验证
    else:
        action = form.cleaned_data['action']
        username = form.cleaned_data['username']
        domain = form.cleaned_data['domain']
        password = form.cleaned_data['password']

        # 验证应用端身份
        form, client = verify_client(request.REQUEST)
        if issubclass(form.__class__, HttpResponse):
            return form

        result.update({'name': client.name})
        response_type = form.cleaned_data['response_type']
        client_id = form.cleaned_data['client_id']
        redirect_uri = request.session['redirect_uri']
        scope = request.session['scope']
        state = request.session['state']

        # 处理code请求
        if response_type == 'code':
            # 处理登录以外的请求
            if not action.lower() == 'login'.lower():
                return callback_client(redirect_uri + '?error=access_denied', state)

            # 验证表单合法性
            if not username or not domain or not password:
                result.update({'error': '请输入邮箱地址及密码'})
                return render_to_response('oauth/authorize.html', result)

            # 验证用户合法性
            user = authenticate(email=username + '@' + domain, password=password)
            if not user:
                result.update({'error': '邮箱地址或密码错误，请重新输入'})
                return render_to_response('oauth/authorize.html', result)

            # 生成code
            code = AuthorizationCode(client=client, user=user, redirect_uri=redirect_uri, expire_time=datetime.datetime.now() + datetime.timedelta(minutes=10))
            code.save()

            return callback_client(redirect_uri + '?code=' + urlsafe_base64_encode(code.code.bytes), state)
        else:
            return callback_client(redirect_uri + '?error=unsupported_response_type', state), None

@csrf_exempt
def token(request):
    # 验证应用端合法性
    client = oauth_server.authorize(request.META.get('HTTP_AUTHORIZATION'))
    if not client:
        response = HttpResponse('401 Unauthorized', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Please provide your client_id and client_secret."'
        return response

    # 验证是否为令牌表单
    form = TokenForm(request.POST)
    if not form.is_valid():
        return error_response('invalid_request')

    grant_type = form.cleaned_data['grant_type']
    code = form.cleaned_data['code']
    redirect_uri = form.cleaned_data['redirect_uri']

    # 处理authorization_code请求
    if grant_type == 'authorization_code':
        try:
            code = AuthorizationCode.objects.filter(expire_time__gte=datetime.datetime.now()).get(client=client, code=UUID(bytes=urlsafe_base64_decode(code)), redirect_uri=redirect_uri)
        except AuthorizationCode.DoesNotExist:
            return error_response('invalid_grant')

        try:
            token = AccessToken(client=client, user=code.user, code=code.code, expire_time=datetime.datetime.now() + datetime.timedelta(hours=1))
            token.save()
        except IntegrityError:
            AccessToken.objects.get(code=code.code).delete()
            code.delete()
            return error_response('invalid_grant')

        return success_response(urlsafe_base64_encode(token.token.bytes))
    else:
        return error_response('unsupported_grant_type')

def verify_client(form):
    # 验证请求合法性
    form = InitializationForm(form)
    if not form.is_valid():
        return HttpResponse('Invalid_request'), None

    state = form.cleaned_data['state']

    # 验证应用端身份
    client_id = form.cleaned_data['client_id']
    try:
        client = Client.objects.get(client_id=client_id)
    except Client.DoesNotExist:
        return HttpResponse('Invalid client id.'), None

    # 验证重定向URI合法性
    redirect_uri = form.cleaned_data['redirect_uri']
    try:
        RedirectionUri.objects.filter(client=client).get(redirect_uri=redirect_uri)
    except RedirectionUri.DoesNotExist:
        return HttpResponse('Mismatching redirection URI.'), client

    return form, client

def callback_client(uri, state):
    if state:
        uri += '&state=' + state

    return HttpResponseRedirect(uri)

def success_response(token):
    result = {'access_token': token, 'token_type': 'bearer', 'expires_in': 3600}

    response = HttpResponse(json.dumps(result), content_type='application/json;charset=UTF-8')
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-store'
    return response

def error_response(error):
    result = {'error': error}

    response = HttpResponse(json.dumps(result), content_type='application/json;charset=UTF-8', status=400)
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-store'
    return response
