# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType


def get_model_instance(obj_id, content_type_id):
    """
    :param obj_id: int - primary key of model instance
    :param content_type_id: int - primary key of ContentType instance
    :return: Instance of model that matches to content type with given identificator (content_type_id)
    """
    ct = ContentType.objects.get_for_id(content_type_id)
    obj = ct.get_object_for_this_type(pk=obj_id)
    return obj
