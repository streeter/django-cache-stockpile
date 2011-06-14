from stockpile import conf
from django.test import TestCase
from .models import Account, DummyInfo

import logging
log = logging.getLogger(__name__)


class StockpileTest(TestCase):
    
    def setUp(self):
        # Don't use a fixture for caching reasons
        a1 = Account.objects.create(id=1, name='dummy_name_1')
        a2 = Account.objects.create(id=2, name='dummy_name_2')
        a3 = Account.objects.create(id=3, name='dummy_name_3')
        DummyInfo.objects.create(id=1, number=28, account1=a1, account2=a2)
        DummyInfo.objects.create(id=2, number=56, account1=a1, account2=a3)
    
    def test_noop(self):
        assert True
    
    def test_instantiate(self):
        a = Account(name='test')
        assert len(a.name) > 0
        a.save()
        assert a.pk > 0
    
    def test_cache_key(self):
        a = Account.objects.get(pk=1)
        assert a.cache_key == 'o:tests.account:1'
        assert not a.from_cache
    
    def test_cache_hit(self):
        a = Account.objects.get(pk=1)
        assert a.pk > 0
        assert not a.from_cache
        
        a2 = Account.objects.get(pk=1)
        assert a.pk == a2.pk
        assert a2.from_cache
    
    def test_cache_invalidate(self):
        a = Account.objects.get(pk=2)
        assert not a.from_cache
        
        a2 = Account.objects.get(pk=2)
        assert a.pk == a2.pk
        assert a2.from_cache
        
        a.name = 'something else'
        a.save()
        
        a3 = Account.objects.get(pk=2)
        assert a.pk == a3.pk and a2.pk == a3.pk
        assert not a3.from_cache
    
    def test_reverse_broken(self):
        a = Account.objects.get(pk=1)
        d = DummyInfo.objects.get(pk=1)
        assert not d.account1.from_cache
        d.account1 = Account.objects.get(pk=1)
        assert d.account1.from_cache
    
    def test_pk_in_uncached(self):
        objects = Account.objects.pk_in([1, 2, 3])
        assert len(objects) == 3
        for o in objects:
            assert not o.from_cache
    
    def test_pk_in_single_cached(self):
        a = Account.objects.get(pk=1)
        assert not a.from_cache
        objects = Account.objects.pk_in([1, 2, 3])
        assert len(objects) == 3
        for o in objects:
            if o.id == a.id:
                assert o.from_cache
            else:
                assert not o.from_cache
    
    def test_pk_in_cached(self):
        objects = Account.objects.pk_in([1, 2, 3])
        assert len(objects) == 3
        for o in objects:
            assert not o.from_cache
        
        objects = Account.objects.pk_in([1, 2, 3])
        assert len(objects) == 3
        for o in objects:
            assert o.from_cache
