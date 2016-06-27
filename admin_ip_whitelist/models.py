# dvska made
# Licensed under the Apache License, Version 2.0 (the "License");


from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

ADMIN_ACCESS_WHITELIST_PREFIX = 'DJANGO_ADMIN_ACCESS_WHITELIST:'
WHITELIST_PREFIX = 'DJANGO_ADMIN_ACCESS_WHITELIST:'


class DjangoAdminAccessIPWhitelist(models.Model):
    whitelist_reason = models.CharField(max_length=255, help_text="Reason for the whitelist?")
    ip = models.CharField(max_length=255, help_text='Enter an IP to whitelist')

    def __unicode__(self):
        return "Whitelisted %s (%s)" % (self.ip, self.whitelist_reason)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    class Meta:
        permissions = (("can_whitelist_user", "Can Whitelist User"),)
        verbose_name = "Django /admin access IP whitelist"
        verbose_name_plural = "Django /admin access allowed IPs"
        db_table = 'django_admin_access_ip_whitelist'


def _generate_cache_key(instance):
    return ADMIN_ACCESS_WHITELIST_PREFIX + instance.ip


def _update_cache(sender, **kwargs):
    # add a whitelist entry
    instance = kwargs.get('instance')
    cache_key = _generate_cache_key(instance)
    cache.set(cache_key, "1")


def _delete_cache(sender, **kwargs):
    instance = kwargs.get('instance')
    cache_key = _generate_cache_key(instance)
    cache.delete(cache_key)


post_save.connect(_update_cache, sender=DjangoAdminAccessIPWhitelist)
post_delete.connect(_delete_cache, sender=DjangoAdminAccessIPWhitelist)
