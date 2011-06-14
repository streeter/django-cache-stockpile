from django.db import models
from django.utils import encoding
from stockpile.managers import StockpileCacheManager


class StockpileModel(models.Model):
    """
    A model that can be inherited from to provide caching.
    """
    #__metaclass__ = StockpileModelBase
    
    @classmethod
    def _prepare(cls):
        opts = cls._meta
        opts._prepare(cls)
        
        cls.add_to_class('objects', StockpileCacheManager())
        cls.add_to_class('nocache', models.manager.Manager())
        # TODO - make this configurable
        cls.add_to_class('_default_manager', cls.nocache)
        
        models.signals.class_prepared.send(sender=cls)
    
    @classmethod
    def _cache_key(cls, pk):
        key_parts = ('o', cls._meta, pk)
        return ':'.join(map(encoding.smart_unicode, key_parts))
    
    @property
    def cache_key(self):
        return self._cache_key(self.pk)
