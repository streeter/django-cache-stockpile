from django.db import models
from django.core.cache import cache, parse_backend_uri
from stockpile import conf
from stockpile.utils import make_key, make_flush_key, invalidator


class FakeQuerySet(object):
    """
    Handles all the cache management for a QuerySet.
    
    Takes the string representation of a query and a function that can be
    called to get an iterator over some database results.
    """
    
    def __init__(self, query_string, iter_function, timeout=None):
        self.query_string = query_string
        self.iter_function = iter_function
        self.timeout = timeout
    
    def query_key(self):
        """Generate the cache key for this query."""
        return make_key('qs:%s' % self.query_string, with_locale=False)
    
    def __iter__(self):
        #try:
        #    query_key = self.query_key()
        #except query.EmptyResultSet:
        #    raise StopIteration
        query_key = self.query_key()
        
        # Try to fetch from the cache.
        cached = cache.get(query_key)
        if cached is not None:
            log.debug('cache hit: %s' % self.query_string)
            for obj in cached:
                obj.from_cache = True
                yield obj
            return
        
        log.debug('cache miss: %s' % self.query_string)
        
        # Do the database query, cache it once we have all the objects.
        iterator = self.iter_function()
        
        to_cache = []
        try:
            while True:
                obj = iterator.next()
                obj.from_cache = False
                to_cache.append(obj)
                yield obj
        except StopIteration:
            log.debug('stopping iteration w/ to_cache: %s' % to_cache)
            if to_cache:
                self.cache_objects(to_cache)
            raise
    
    def cache_objects(self, objects):
        """Cache query_key => objects, then update the flush lists."""
        query_key = self.query_key()
        flush_key = make_flush_key(self.query_string)
        cache.add(query_key, objects, timeout=self.timeout)
        invalidator.cache_objects(objects, query_key, query_flush)


class StockpileCachedQuerySet(models.query.QuerySet):
    
    def __init__(self, *args, **kwargs):
        super(StockpileCachedQuerySet, self).__init__(*args, **kwargs)
        self.timeout = None
    
    def flush_key(self):
        return flush_key(self.query_key())
    
    def query_key(self):
        sql, params = self.query.get_compiler(using=self.db).as_sql()
        return sql % params
    
    def iterator(self):
        iterator = super(StockpileCachedQuerySet, self).iterator
        if self.timeout == conf.TIMEOUT_NO_CACHE or not conf.ENABLED:
            return iter(iterator())
        else:
            try:
                query_string = self.query_key()
            except query.EmptyResultSet:
                return iterator()
            return iter(FakeQuerySet(query_string, iterator, self.timeout))
    
    def fetch_by_id(self):
        # TODO
        pass
    
    def cache(self, timeout=None):
        qs = self._clone()
        qs.timeout = timeout
        return qs
    
    def no_cache(self):
        return self.cache(conf.TIMEOUT_NO_CACHE)
    
    def _clone(self, *args, **kwargs):
        qs = super(StockpileCachedQuerySet, self)._clone(*args, **kwargs)
        qs.timeout = self.timeout
        return qs
