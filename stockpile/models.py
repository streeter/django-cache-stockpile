from django.db import models
from django.utils import encoding
from stockpile.managers import CachedManager
from stockpile.utils import make_flush_key


class CachedModel(models.Model):
    """
    A model that can be inherited from to provide caching.
    """
    
    class Meta:
        abstract = True
    
    @classmethod
    def _prepare(cls):
        opts = cls._meta
        opts._prepare(cls)
        
        cls.add_to_class('objects', CachedManager())
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
    
    @property
    def cache_keys(self):
        fks = dict((f, getattr(self, f.attname)) for f in self._meta.fields
                    if isinstance(f, models.ForeignKey))
        
        keys = [fk.rel.to._cache_key(val) for fk, val in fks.items()
                if val is not None and hasattr(fk.rel.to, '_cache_key')]
        return (self.cache_key,) + tuple(keys)
    
    @property
    def flush_key(self):
        return make_flush_key(self)
    
    def _get_from_cache(self):
        if hasattr(self, '_from_cache'):
            return self._from_cache
        else:
            return False
    
    def _set_from_cache(self, value):
        self._from_cache = value
    
    from_cache = property(_get_from_cache, _set_from_cache)
