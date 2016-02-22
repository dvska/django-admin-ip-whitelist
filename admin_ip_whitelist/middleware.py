import logging

import django
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseForbidden

from models import DjangoAdminAccessIPWhitelist, ADMIN_ACCESS_WHITELIST_PREFIX

log = logging.getLogger(__name__)


class AdminAccessIPWhiteListMiddleware(object):
    def __init__(self):
        """
        Middleware init is called once per server on startup - do the heavy
        lifting here.
        """
        # If disabled or not enabled raise MiddleWareNotUsed so django
        # processes next middleware.
        self.ENABLED = getattr(settings, 'ADMIN_ACCESS_WHITELIST_ENABLED', False)
        self.DEBUG = getattr(settings, 'ADMIN_ACCESS_WHITELIST_DEBUG', False)
        self.USE_HTTP_X_FORWARDED_FOR = getattr(settings, 'ADMIN_ACCESS_WHITELIST_USE_HTTP_X_FORWARDED_FOR', False)
        self.ADMIN_ACCESS_WHITELIST_MESSAGE = getattr(settings, 'ADMIN_ACCESS_WHITELIST_MESSAGE', 'You are banned.')

        if not self.ENABLED:
            raise MiddlewareNotUsed("django-banish is not enabled via settings.py")

        log.debug("[django-admin-ip-whitelist] status = enabled")

        # Prefix All keys in cache to avoid key collisions
        self.ABUSE_PREFIX = 'DJANGO_ADMIN_ACCESS_WHITELIST_ABUSE:'
        self.WHITELIST_PREFIX = ADMIN_ACCESS_WHITELIST_PREFIX

        for whitelist in DjangoAdminAccessIPWhitelist.objects.all():
            cache_key = self.WHITELIST_PREFIX + whitelist.ip
            cache.set(cache_key, "1")

    def _get_ip(self, request):
        ip = request.META['REMOTE_ADDR']
        if self.USE_HTTP_X_FORWARDED_FOR or not ip or ip == '127.0.0.1':
            ip = request.META.get('HTTP_X_FORWARDED_FOR', ip).split(',')[0].strip()
        return ip

    def process_request(self, request):
        if not request.path.startswith('/admin'):
            return None

        ip = self._get_ip(request)

        user_agent = request.META.get('HTTP_USER_AGENT', None)

        log.debug("GOT IP FROM Request: %s and User Agent %s" % (ip, user_agent))

        if self.is_whitelisted(ip):
            return None
        else:
            return self.http_response_forbidden(self.ADMIN_ACCESS_WHITELIST_MESSAGE + '\n<!-- {} -->'.format(ip), content_type="text/html")

    @staticmethod
    def http_response_forbidden(message, content_type):
        if django.VERSION[:2] > (1, 3):
            kwargs = {'content_type': content_type}
        else:
            kwargs = {'mimetype': content_type}
        return HttpResponseForbidden(message, **kwargs)

    def is_whitelisted(self, ip):
        # If a whitelist key exists, return True to allow the request through
        is_whitelisted = cache.get(self.WHITELIST_PREFIX + ip)
        if is_whitelisted:
            log.debug("/Admin access IP: " + self.WHITELIST_PREFIX + ip)
        return is_whitelisted

