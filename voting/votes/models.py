# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .exceptions import VoteAlreadyExists
from .utils import CountsVotesCache


class VoteManager(models.Manager):
    def count_votes_for_content(self, content_object, vote_type=None):
        ct = ContentType.objects.get_for_model(content_object)
        qs = self.get_queryset().filter(
            content_type=ct,
            object_id=content_object.pk,
        )
        if vote_type:
            qs = qs.filter(vote_type=vote_type)
        return qs.count()

    def count_likes_for_content(self, content_object):
        return self.count_votes_for_content(content_object, self.model.TYPE_IS_LIKE)

    def count_dislikes_for_content(self, content_object):
        return self.count_votes_for_content(content_object, self.model.TYPE_IS_DISLIKE)

    def count_all_votes_for_content(self, content_object):
        return self.count_votes_for_content(content_object)

    def delete_vote(self, object_id, content_type_id, author):
        ct = ContentType.objects.get(pk=content_type_id)
        self.filter(
            content_type=ct,
            object_id=object_id,
            author=author,
        ).delete()


class Vote(models.Model):
    TYPE_IS_LIKE = 1
    TYPE_IS_DISLIKE = -1
    TYPE_CHOICES = {
        TYPE_IS_LIKE: _('Is like'),
        TYPE_IS_DISLIKE: _('Is like'),
    }
    vote_type = models.SmallIntegerField(choices=TYPE_CHOICES.items(), db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = VoteManager()

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        unique_together = ['author', 'content_type', 'object_id']

    @classmethod
    def _create(cls, vote_type, content_object, author):
        ct = ContentType.objects.get_for_model(content_object)
        v, created = cls.objects.get_or_create(
            content_type=ct,
            object_id=content_object.pk,
            author=author,
            defaults=dict(
                vote_type=vote_type,
                content_type=ct,
                object_id=content_object.pk,
                author=author,
            )
        )
        if not created:
            raise VoteAlreadyExists
        else:
            print('CREATED Vote #%d' % v.pk)
        return v

    @classmethod
    def create_like(cls, content_object, author):
        return cls._create(cls.TYPE_IS_LIKE, content_object, author)

    @classmethod
    def create_dislike(cls, content_object, author):
        return cls._create(cls.TYPE_IS_DISLIKE, content_object, author)


@receiver(post_save, sender=Vote)
@receiver(pre_delete, sender=Vote)
def clear_cache_of_votes_counts(sender, instance, **kwargs):
    v_cache = CountsVotesCache(instance.content_object)
    v_cache.clear()
