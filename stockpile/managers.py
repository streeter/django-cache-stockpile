from django.db import models
from django.core.cache import cache
from stockpile import conf
from stockpile.query import CachedQuerySet
from stockpile.utils import invalidator

import logging
log = logging.getLogger(__name__)


class StockpileCacheManager(models.manager.Manager):
    """
    A manager to store and retrieve cached objects.
    """
    def __init__(self, *args, **kwargs):
        super(StockpileCacheManager, self).__init__(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        if 'id' not in kwargs and 'pk' not in kwargs:
            return self.get_query_set().get(*args, **kwargs)
        # Look up in cache
        if 'id' in kwargs:
            id = kwargs['id']
        else:
            id = kwargs['pk']
        key = self.model._cache_key(id)
        o = cache.get(key)
        if o:
            o.from_cache = True
        else:
            o = self.get_query_set().get(*args, **kwargs)
            if o:
                cache.set(key, o)
        return o
    
    def id_in(self, ids):
        return self.pk_in(ids)
    
    def pk_in(self, ids):
        # For each item in the set, get the cache key
        keys = dict((id, self.model._cache_key(id)) for id in ids)
        # Lookup all the keys
        objs = cache.get_many(keys.values())
        for k,o in objs.items():
            o.from_cache = True
        missed = [id for id, key in keys.items() if key not in objs]
        
        keys = dict((o.cache_key, o) for o in self.filter(id__in=missed))
        cache.set_many(keys)
        
        return objs.values() + keys.values()
    
    def contribute_to_class(self, cls, name):
        models.signals.post_save.connect(self.post_save, sender=cls)
        models.signals.post_delete.connect(self.post_delete, sender=cls)
        return super(StockpileCacheManager, self).contribute_to_class(cls, name)
    
    def post_save(self, instance, **kwargs):
        self.invalidate(instance)

    def post_delete(self, instance, **kwargs):
        self.invalidate(instance)
    
    def invalidate(self, *objects):
        keys = dict((o.cache_key, None) for o in objects)
        #log.debug('Invalidating keys: %s' % keys)
        cache.set_many(keys)
        
        #keys = [k for o in objects for k in o.cache_keys]
        #invalidator.invalidate_keys(keys)
    
    #def get_query_set(self):
    #    return CachedQuerySet(model=self.model)
    #
    #def cache(self, *args, **kwargs):
    #    return self.get_query_set().cache(*args, **kwargs)
    #
    #def clean(self, *args, **kwargs):
    #    # Use reset instead if you are using memcached, as clean makes no
    #    # sense (extra bandwidth when
    #    # memcached will automatically clean iself).
    #    return self.get_query_set().clean(*args, **kwargs)
    #
    #def reset(self, *args, **kwargs):
    #    return self.get_query_set().reset(*args, **kwargs)
