from stockpile import conf
from django.test import TestCase
from stockpile.models import get_ticket


class StockpileTest(TestCase):
    
    def setUp(self):
        pass
    
    def test_noop(self):
        assert True
