===============
Stockpile Cache
===============

Stockpile provides limited automatic caching and invalidation for Django models
through the ORM. Objects fetched through `.objects.get(pk=..)` or
`.objects.get(id=..)` are cached by the primary key. In addition, there is
a way to get objects with the methods `.objects.pk_in(id_list)` and
`.objects.id_in(id_list)`.


Requirements
------------

Stockpile requires Django 1.3.  It was written and tested on Python 2.6.


Installation
------------

Get it from [pypi](http://pypi.python.org/pypi/django-cache-stockpile):

```bash
pip install django-cache-stockpile
```

or [github](http://github.com/streeter/django-cache-stockpile):

```bash
pip install -e git://github.com/streeter/django-cache-stockpile.git#egg=django-cache-stockpile
```


Running Tests
-------------

```bash
git clone git://github.com/streeter/django-cache-stockpile.git
cd django-cache-stockpile
pip install -r requirements.txt
python runtests.py
```
