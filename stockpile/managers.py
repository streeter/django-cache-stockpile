from django.db import models
from stockpile import conf
from stockpile.query import StockpileCachedQuerySet


class StockpileCacheManager(models.manager.Manager):
    """
    A manager to store and retrieve cached objects.
    """
    def __init__(self, *args, **kwargs):
        self.key_prefix = conf.PREFIX
        self.timeout = conf.TIMEOUT_DEFAULT
        super(StockpileCacheManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return StockpileCachedQuerySet(model=self.model, timeout=self.timeout,
            key_prefix=self.key_prefix)

    def cache(self, *args, **kwargs):
        return self.get_query_set().cache(*args, **kwargs)

    def clean(self, *args, **kwargs):
        # Use reset instead if you are using memcached, as clean makes no
        # sense (extra bandwidth when
        # memcached will automatically clean iself).
        return self.get_query_set().clean(*args, **kwargs)

    def reset(self, *args, **kwargs):
        return self.get_query_set().reset(*args, **kwargs)
