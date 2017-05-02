# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class CommentManager(models.Manager):
    def of_content(self, content_obj):
        """
        Comments related with given content object
        :param content_obj: Instance of some model
        :return: Queryset
        """
        qs = self.get_queryset().filter(
            content_object=content_obj,
        )
        return qs


class Comment(models.Model):
    text = models.TextField(max_length=5000, verbose_name=_('Text'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = CommentManager()

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    @classmethod
    def create(cls, text, author, content_obj):
        """
        Create and return comment instance.
        :param text: str - comment text
        :param author: instance of primary user model
        :param content_obj: instance of some model
        :return: Comment
        """
        comment = cls(
            text=text,
            author=author,
            content_object=content_obj,
        )
        comment.save()
        return comment
