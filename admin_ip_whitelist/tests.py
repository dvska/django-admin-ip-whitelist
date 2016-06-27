from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from testfixtures import LogCapture, log_capture

from .models import ADMIN_ACCESS_WHITELIST_PREFIX, DjangoAdminAccessIPWhitelist


class MiddlewareTests(TestCase):
    def tearDown(self):
        cache.clear()

    def test_other_view(self):
        other_url = reverse('test')
        response = self.client.get(other_url, REMOTE_ADDR="5.5.5.5")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, 'Hello, World!')

    def test_denied(self):
        admin_url = reverse('admin:index')

        with LogCapture() as l:
            response = self.client.get(admin_url, REMOTE_ADDR="5.5.5.5")

        expected_response = "You are banned.\n<!-- 5.5.5.5 -->"
        self.assertEquals(response.status_code, 403)  # forbidden
        self.assertEquals(response.content, expected_response)
        self.assertEquals(response['content-type'], 'text/html')

        module_name = 'admin_ip_whitelist.middleware'
        l.check(
            (module_name, "DEBUG", "[django-admin-ip-whitelist] status = enabled"),
            (module_name, "DEBUG", "GOT IP FROM Request: 5.5.5.5 and User Agent None"),
        )

    @override_settings(ADMIN_ACCESS_WHITELIST_MESSAGE='Leave, now.')
    def test_denied_custom_message(self):
        admin_url = reverse('admin:index')

        with LogCapture() as l:
            response = self.client.get(admin_url, REMOTE_ADDR="5.5.5.5")
        expected_response = "Leave, now.\n<!-- 5.5.5.5 -->"
        self.assertEquals(response.status_code, 403)  # forbidden
        self.assertEquals(response.content, expected_response)
        self.assertEquals(response['content-type'], 'text/html')

        module_name = 'admin_ip_whitelist.middleware'
        l.check(
            (module_name, "DEBUG", "[django-admin-ip-whitelist] status = enabled"),
            (module_name, "DEBUG", "GOT IP FROM Request: 5.5.5.5 and User Agent None"),
        )

    @override_settings(ADMIN_ACCESS_WHITELIST_USE_HTTP_X_FORWARDED_FOR=True)
    @log_capture()
    def test_http_x_forward_for(self, l):
        DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason='You are special',
            ip='1.2.3.4',
        )
        admin_url = reverse('admin:index')

        # Allowed, the FORWARDED address is being considered.
        response = self.client.get(
            admin_url, REMOTE_ADDR="5.5.5.5",
            HTTP_X_FORWARDED_FOR="1.2.3.4, 4.4.4.4, 3.3.3.3")
        self.assertEquals(response.status_code, 302)  # redirect
        expected_url = "{}?next={}".format(reverse('admin:login'), admin_url)
        self.assertEquals(response.url, expected_url)

        # Allowed, If no forwarded address is given, it falls back
        # to REMOTE_ADDR.
        response = self.client.get(
            admin_url, REMOTE_ADDR="1.2.3.4")
        self.assertEquals(response.status_code, 302)  # redirect
        expected_url = "{}?next={}".format(reverse('admin:login'), admin_url)
        self.assertEquals(response.url, expected_url)

        module_name = 'admin_ip_whitelist.middleware'
        l.check(
            (module_name, "DEBUG", "[django-admin-ip-whitelist] status = enabled"),
            (module_name, "DEBUG", "GOT IP FROM Request: 1.2.3.4 and User Agent None"),
            (module_name, "DEBUG", "/Admin access IP: DJANGO_ADMIN_ACCESS_WHITELIST:1.2.3.4"),
            (module_name, "DEBUG", "GOT IP FROM Request: 1.2.3.4 and User Agent None"),
            (module_name, "DEBUG", "/Admin access IP: DJANGO_ADMIN_ACCESS_WHITELIST:1.2.3.4"),
        )

    @log_capture()
    def test_allowed(self, l):
        DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason='You are special',
            ip='1.2.3.4',
        )
        admin_url = reverse('admin:index')

        # This user is not allowed.
        response = self.client.get(admin_url, REMOTE_ADDR="5.5.5.5")
        expected_response = "You are banned.\n<!-- 5.5.5.5 -->"
        self.assertEquals(response.status_code, 403)  # forbidden
        self.assertEquals(response.content, expected_response)
        self.assertEquals(response['content-type'], 'text/html')

        # This user is special.
        response = self.client.get(admin_url, REMOTE_ADDR="1.2.3.4")
        self.assertEquals(response.status_code, 302)  # redirect
        expected_url = "{}?next={}".format(reverse('admin:login'), admin_url)
        self.assertEquals(response.url, expected_url)

        module_name = 'admin_ip_whitelist.middleware'
        l.check(
            (module_name, "DEBUG", "[django-admin-ip-whitelist] status = enabled"),
            (module_name, "DEBUG", "GOT IP FROM Request: 5.5.5.5 and User Agent None"),
            (module_name, "DEBUG", "GOT IP FROM Request: 1.2.3.4 and User Agent None"),
            (module_name, "DEBUG", "/Admin access IP: DJANGO_ADMIN_ACCESS_WHITELIST:1.2.3.4"),
        )


class ModelTests(TestCase):
    def tearDown(self):
        cache.clear()

    def test_instance_create_and_update(self):
        self.assertEquals(len(cache._cache.keys()), 0)
        cache_key = ADMIN_ACCESS_WHITELIST_PREFIX + '1.2.3.4'
        self.assertEquals(cache.get(cache_key), None)
        obj = DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason='You are special',
            ip='1.2.3.4',
        )
        self.assertEquals(len(cache._cache.keys()), 1)
        self.assertEquals(cache.get(cache_key), '1')

        obj.ip = '5.5.5.5'
        obj.save()

        self.assertEquals(cache.get(cache_key), None)
        new_cache_key = ADMIN_ACCESS_WHITELIST_PREFIX + '5.5.5.5'
        self.assertEquals(cache.get(new_cache_key), '1')
        self.assertEquals(len(cache._cache.keys()), 1)

    def test_instance_delete(self):
        self.assertEquals(len(cache._cache.keys()), 0)
        obj = DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason='You are special',
            ip='1.2.3.4',
        )
        self.assertEquals(len(cache._cache.keys()), 1)
        cache_key = ADMIN_ACCESS_WHITELIST_PREFIX + '1.2.3.4'
        self.assertEquals(cache.get(cache_key), '1')
        obj.delete()
        self.assertEquals(cache.get(cache_key), None)

    def test_unicode(self):
        obj = DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason=u"This is what a cat looks like: \U0001F408",
            ip='1.2.3.4',
        )

        self.assertEquals(
            unicode(obj),
            u"Whitelisted 1.2.3.4 (This is what a cat looks like: \U0001F408)"
        )

    def test_str(self):
        obj = DjangoAdminAccessIPWhitelist.objects.create(
            whitelist_reason=u"This is what a cat looks like: \U0001F408",
            ip='1.2.3.4',
        )

        self.assertEquals(
            str(obj),
            "Whitelisted 1.2.3.4 (This is what a cat looks like: \xF0\x9F\x90\x88)"
        )
