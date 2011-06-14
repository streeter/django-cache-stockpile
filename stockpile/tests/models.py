from stockpile.models import StockpileModel
from django.db import models


class Account(StockpileModel):
    name = models.CharField(max_length=20)


class DummyInfo(StockpileModel):
    number = models.IntegerField()
    account1 = models.ForeignKey(Account, related_name='account1')
    account2 = models.ForeignKey(Account, related_name='account2')
