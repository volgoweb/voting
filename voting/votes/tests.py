# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.cache import cache

from model_mommy import mommy

from .services import like_content, dislike_content, get_count_votes_of_content_object
from .models import Vote
from .exceptions import VoteAlreadyExists
from . import views


class BaseTest(TestCase):
    def setUp(self):
        self.users = mommy.make(settings.AUTH_USER_MODEL, _quantity=10)

        article = mommy.make('content.Article', author=self.users[0])
        news = mommy.make('content.News', author=self.users[0])
        comment = mommy.make('comments.Comment', author=self.users[0])
        self.content = [
            article,
            news,
            comment,
        ]


class VoteServicesTest(BaseTest):
    def _get_kwargs_for_service(self, index=0):
        user = self.users[index]
        obj = self.content[index]
        ct = ContentType.objects.get_for_model(obj)
        kw = dict(
            content_object_id=obj.pk,
            content_type_id=ct.pk,
            author=user
        )
        return kw

    # def test_liking_service(self):
    #     for i, obj in enumerate(self.content):
    #         like_content(**self._get_kwargs_for_service(i))
    #         count_likes = Vote.objects.count_likes_for_content(obj)
    #         self.assertEqual(count_likes, 1)
    #
    # def test_votes_twicely_of_same_user(self):
    #     index = 0
    #     obj = self.content[index]
    #     service_kwargs = self._get_kwargs_for_service(index)
    #
    #     like_content(**service_kwargs)
    #     count_likes = Vote.objects.count_likes_for_content(obj)
    #     self.assertEqual(count_likes, 1)
    #
    #     with self.assertRaises(VoteAlreadyExists):
    #         dislike_content(**service_kwargs)
    #     count_dislikes = Vote.objects.count_dislikes_for_content(obj)
    #     self.assertEqual(count_dislikes, 0)

    def test_getting_votes_counts(self):
        index = 0
        service_kwargs = self._get_kwargs_for_service(index)
        like_content(**service_kwargs)
        for i in range(2):
            service_kwargs['author'] = self.users[i + 1]
            dislike_content(**service_kwargs)

        count_votes_kw = service_kwargs.copy()
        del count_votes_kw['author']
        counts_spec = get_count_votes_of_content_object(**count_votes_kw)
        self.assertEqual(counts_spec.likes, 1)
        self.assertEqual(counts_spec.dislikes, 2)
        self.assertEqual(counts_spec.all, 3)

        # --- test cache ---
        # getting from cache
        self.assertNumQueries(1, get_count_votes_of_content_object, **count_votes_kw)

        # check cache consistency
        counts_spec = get_count_votes_of_content_object(**count_votes_kw)
        self.assertEqual(counts_spec.likes, 1)
        self.assertEqual(counts_spec.dislikes, 2)
        self.assertEqual(counts_spec.all, 3)

        # after creation of vote object cache will be cleared
        service_kwargs['author'] = self.users[-1]
        dislike_content(**service_kwargs)
        self.assertNumQueries(4, get_count_votes_of_content_object, **count_votes_kw)



class VoteViewsTest(object):
    def setUp(self):
        super(VoteViewsTest, self).setUp()
        self.request_factory = RequestFactory()
        self.user = self.users[0]

    def _test_leave_vote_view(self, url, views_func, index=0):
        obj = self.content[index]
        ct = ContentType.objects.get_for_model(obj)
        d = dict(
            content_id=obj.pk,
            content_type_id=ct.pk,
        )
        request = self.request_factory.get(url, data=d)
        request.user = self.user
        resp = views_func(request)
        json_obj = json.loads(resp.content)
        self.assertEqual(json_obj['code'], 1)

    def test_like_view(self):
        url = reverse('votes:like_content')
        self._test_leave_vote_view(url, views.like_content)

    def test_dislike_view(self):
        url = reverse('votes:dislike_content')
        self._test_leave_vote_view(url, views.dislike_content)

    def test_retrieve_vote_view(self):
        obj = self.content[0]
        Vote.create_like(content_object=obj, author=self.user)
        url = reverse('votes:retrieve_vote')
        self._test_leave_vote_view(url, views.retrieve_vote)

    def test_count_votes_view(self):
        index = 0
        obj = self.content[index]
        ct = ContentType.objects.get_for_model(obj)

        Vote.create_like(content_object=obj, author=self.user)

        d = dict(
            content_id=obj.pk,
            content_type_id=ct.pk,
        )
        url = reverse('votes:votes_counts')
        request = self.request_factory.get(url, data=d)
        request.user = self.user
        resp = views.get_votes_counts(request)
        json_obj = json.loads(resp.content)
        self.assertEqual(json_obj['likes'], 1)
        self.assertEqual(json_obj['dislikes'], 0)
        self.assertEqual(json_obj['all'], 1)
