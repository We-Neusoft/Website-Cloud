from django.contrib.auth.models import User

from imaplib import IMAP4

from apps.oauth.models import AccessToken

ALLOWED_DOMAIN = ['nou.com.cn', 'neusoft.edu.cn']

class MailboxAuth(object):
    def authenticate(self, email=None, password=None):
        if not email.count('@') == 1:
            return None

        email = email.lower()
        domain = email.split('@')[1]
        if not domain in ALLOWED_DOMAIN:
            return None

        try:
            mailbox = IMAP4('mail.' + domain)
            mailbox.login(email, password)

            try:
                user = User.objects.get(username=email[:30])
            except User.DoesNotExist:
                user = User.objects.create_user(email[:30], email)
                user.save()

            return user
        except:
            return None

class TokenAuth(object):
    def authenticate(self, token=None):
        if not token:
            return None

        try:
            return AccessToken.objects.filter(expire_time__gte=datetime.datetime.now()).get(token=token).user
        except AccessToken.DoesNotExist:
            return None
