from stockpile.models import CachedModel
from django.db import models


class Account(CachedModel):
    name = models.CharField(max_length=20)


class DummyInfo(CachedModel):
    number = models.IntegerField()
    account1 = models.ForeignKey(Account, related_name='account1')
    account2 = models.ForeignKey(Account, related_name='account2')
