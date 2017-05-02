# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


class VoteContentRequestSpecification(object):
    """
    Object of this class uses as input data for use cases
    """
    def __init__(self, content_id, content_type_id, author):
        """
        :param content_id: int - primary key of content instance
        :param content_type_id: int - primary key of ContentType instance
        :param author: - instance of user model
        """
        self.content_id = content_id
        self.content_type_id = content_type_id
        self.author = author


class VoteContentResponseSpecification(object):
    """
    Object of this class uses as output data for frontend
    """
    SUCCESS = 1
    CONTENT_OBJECT_NOT_FOUND = -1
    DUBLICATE_CONSTRAINT = -2
    ANOTHER_ERROR = -3
    AVAILABLE_CODES = {
        SUCCESS: _('Success.'),
        CONTENT_OBJECT_NOT_FOUND: _('Content not found.'),
        DUBLICATE_CONSTRAINT: _('Retrying voting is prohibited.'),
        ANOTHER_ERROR: _('Voting failed.'),
    }

    def __init__(self, code):
        if code not in self.AVAILABLE_CODES.keys():
            raise ValueError()
        self.code = code

    def to_dict(self):
        return dict(
            code=self.code,
            msg=self.AVAILABLE_CODES[self.code],
        )


class VotesCountsOfObjectSpecification(object):
    def __init__(self, likes, dislikes, all):
        self.likes = likes
        self.dislikes = dislikes
        self.all = all

    def to_dict(self):
        return dict(
            likes=self.likes,
            dislikes=self.dislikes,
            all=self.all,
        )
