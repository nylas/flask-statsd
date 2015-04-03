"""
Flask-Statsd
-------------

Flask-Statsd is a flask extension that creates various utilities to
help the integration between flask and statsd.
"""
from setuptools import setup


setup(
    name='Flask-Statsd-Ext',
    version='0.0.2a1',
    url='http://nilas.com',
    author='Rob McQueen',
    author_email='rob@nilas.com',
    description='Statsd Extension for Flask',
    long_description=__doc__,
    py_modules=['flask_statsd'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'statsd'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
