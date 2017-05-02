# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from . import services
from .specifications import VoteContentResponseSpecification
from .exceptions import VoteAlreadyExists


def leave_vote(request, service_func):
    try:
        service_func(
            content_object_id=request.GET.get('content_id'),
            content_type_id=request.GET.get('content_type_id'),
            author=request.user,
        )
    except ObjectDoesNotExist:
        resp = VoteContentResponseSpecification(VoteContentResponseSpecification.CONTENT_OBJECT_NOT_FOUND)
        return JsonResponse(resp.to_dict())
    except VoteAlreadyExists:
        resp = VoteContentResponseSpecification(VoteContentResponseSpecification.DUBLICATE_CONSTRAINT)
        return JsonResponse(resp.to_dict())
    resp = VoteContentResponseSpecification(VoteContentResponseSpecification.SUCCESS)
    return JsonResponse(resp.to_dict())


@login_required
def like_content(request):
    return leave_vote(request, services.like_content)


@login_required
def dislike_content(request):
    return leave_vote(request, services.dislike_content)


@login_required
def retrieve_vote(request):
    try:
        services.retrieve_vote(
            content_object_id=request.GET.get('content_id'),
            content_type_id=request.GET.get('content_type_id'),
            author=request.user,
        )
    except ObjectDoesNotExist:
        resp = VoteContentResponseSpecification(VoteContentResponseSpecification.CONTENT_OBJECT_NOT_FOUND)
        return JsonResponse(resp.to_dict())
    resp = VoteContentResponseSpecification(VoteContentResponseSpecification.SUCCESS)
    return JsonResponse(resp.to_dict())


@login_required
def get_votes_counts(request):
    spec = services.get_count_votes_of_content_object(
        content_object_id=request.GET.get('content_id'),
        content_type_id=request.GET.get('content_type_id'),
    )
    return JsonResponse(spec.to_dict())


