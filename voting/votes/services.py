# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..utils import get_model_instance
from .models import Vote
from .specifications import VotesCountsOfObjectSpecification
from .utils import CountsVotesCache


def like_content(content_object_id, content_type_id, author):
    """
    Leave positive vote for some content by some user.
    :param content_object_id: int - primary key of model instance which will give a vote.
    :param content_type_id: int - primary key of instance of contenttypes.ContentType.
    :param author: - instance of user, who leaving a vote.
    :return: None
    """
    obj = get_model_instance(content_object_id, content_type_id)
    Vote.create_like(
        author=author,
        content_object=obj,
    )


def dislike_content(content_object_id, content_type_id, author):
    """
    Leave negative vote for some content by some user.
    :param content_object_id: int - primary key of model instance which will give a vote.
    :param content_type_id: int - primary key of instance of contenttypes.ContentType.
    :param author: - instance of user, who leaving a vote.
    :return: None
    """
    obj = get_model_instance(content_object_id, content_type_id)
    Vote.create_dislike(
        author=author,
        content_object=obj,
    )


def retrieve_vote(content_object_id, content_type_id, author):
    """
    Revocation of vote for some content by some user.
    :param content_object_id: int - primary key of model instance which will give a vote.
    :param content_type_id: int - primary key of instance of contenttypes.ContentType.
    :param author: - instance of user, who leaving a vote.
    :return: None
    """
    v = Vote.objects.delete_vote(
        author=author,
        object_id=content_object_id,
        content_type_id=content_type_id,
    )
    return v


def get_count_votes_of_content_object(content_object_id, content_type_id):
    content_object = get_model_instance(content_object_id, content_type_id)
    vcache = CountsVotesCache(content_object)
    vcounts_spec = vcache.get()
    if isinstance(vcounts_spec, VotesCountsOfObjectSpecification):
        return vcounts_spec
    else:
        vcounts_spec = VotesCountsOfObjectSpecification(
            likes=Vote.objects.count_likes_for_content(content_object),
            dislikes=Vote.objects.count_dislikes_for_content(content_object),
            all=Vote.objects.count_all_votes_for_content(content_object),
        )
        vcache.set(vcounts_spec)
        return vcounts_spec
