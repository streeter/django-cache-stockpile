#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test

import stockpile

class mytest(test):
    def run(self, *args, **kwargs):
        from runtests import runtests
        runtests()
        # Upgrade().run(dist=True)
        # test.run(self, *args, **kwargs)

setup(
    name='django-cache-stockpile',
    version=stockpile.__version__,
    author='Chris Streeter',
    author_email='pypi@chrisstreeter.com',
    url='http://github.com/streeter/django-cache-stockpile',
    description = 'A simple django ORM caching layer.',
    long_description=open('README.markdown').read(),
    packages=find_packages(),
    license='BSD',
    zip_safe=False,
    install_requires=[
    ],
    test_suite = 'stockpile.tests',
    include_package_data=True,
    cmdclass={"test": mytest},
    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
