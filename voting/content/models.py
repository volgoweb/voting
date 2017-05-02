# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class BaseContent(models.Model):
    title = models.CharField(max_length=150, verbose_name=_('Title'))
    text = models.TextField(max_length=5000, verbose_name=_('Text'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'))

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Article(BaseContent):
    class Meta:
        abstract = False
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')


class News(BaseContent):
    class Meta:
        abstract = False
        verbose_name = _('News')
        verbose_name_plural = _('News')
