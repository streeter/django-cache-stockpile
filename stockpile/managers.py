from django.db import models
from django.core.cache import cache
from stockpile import conf

import logging
log = logging.getLogger(__name__)


class CachedManager(models.manager.Manager):
    """
    A manager to store and retrieve cached objects.
    """
    def __init__(self, *args, **kwargs):
        super(CachedManager, self).__init__(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        if 'id' not in kwargs and 'pk' not in kwargs:
            return self.get_query_set().get(*args, **kwargs)
        # Look up in cache
        id = kwargs.get('id', kwargs.get('pk'))
        key = self.model._cache_key(id)
        if conf.ENABLED:
            o = cache.get(key)
            if o:
                o.from_cache = True
        if not conf.ENABLED or not o:
            o = self.get_query_set().get(*args, **kwargs)
            conf.ENABLED and cache.set(key, o, conf.TIMEOUT)
        return o
    
    def id_in(self, ids):
        return self.pk_in(ids)
    
    def pk_in(self, ids):
        keys = dict((id, self.model._cache_key(id)) for id in ids)
        if conf.ENABLED:
            objs = cache.get_many(keys.values())
            for k,o in objs.items():
                o.from_cache = True
            missed = [id for id, key in keys.items() if key not in objs]
        else:
            missed=ids
        
        keys = dict((o.cache_key, o) for o in self.filter(id__in=missed))
        conf.ENABLED and cache.set_many(keys, conf.TIMEOUT)
        
        return objs.values() + keys.values()
    
    def contribute_to_class(self, cls, name):
        models.signals.post_save.connect(self.signal_post, sender=cls)
        models.signals.post_delete.connect(self.signal_post, sender=cls)
        return super(CachedManager, self).contribute_to_class(cls, name)
    
    def signal_post(self, instance, **kwargs):
        self.invalidate(instance)
    
    def invalidate(self, *objects):
        if conf.ENABLED:
            cache.set_many(dict((o.cache_key, None) for o in objects))
