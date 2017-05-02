from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType


class CountsVotesCache(object):
    def __init__(self, content_object):
        self.content_object = content_object
        self.content_type = ContentType.objects.get_for_model(content_object)

    def get(self):
        v = cache.get(self.key)
        return v

    def set(self, value):
        cache.set(self.key, value)

    def clear(self):
        cache.delete(self.key)

    @property
    def key(self):
        key = 'votes_counts:#{ct_id}#{obj_id}'.format(
            ct_id=self.content_type.pk,
            obj_id=self.content_object.pk,
        )
        return key
