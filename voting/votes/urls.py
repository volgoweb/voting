# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import *

from .views import get_votes_counts, retrieve_vote, like_content, dislike_content

urlpatterns = [
    url(r'^api/like-content/$', like_content, name='like_content'),
    url(r'^api/dislike-content/$', dislike_content, name='dislike_content'),
    url(r'^api/retrieve-vote/$', retrieve_vote, name='retrieve_vote'),
    url(r'^api/votes-counts/$', get_votes_counts, name='votes_counts'),
]