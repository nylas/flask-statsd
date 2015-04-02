#!/usr/bin/env python

import time
import urllib

from flask import request, current_app
import statsd

class Statsd(object):
    '''Statsd Extension for Flask'''
    START_TIME_ATTR = "statsd_start_time"

    _client = None

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('STATSD_ENABLED', True)
        app.config.setdefault('STATSD_HOST', 'localhost')
        app.config.setdefault('STATSD_PORT', 8125)
        app.config.setdefault('STATSD_PREFIX', None)
        app.config.setdefault('STATSD_RATE', 1)

        if app.config['STATSD_ENABLED']:
            app.before_request(self._before_request)
            app.after_request(self._after_request)

    def _after_request(self, response):
        if not hasattr(request, self.START_TIME_ATTR) or \
           current_app.config['STATSD_RATE'] == 0:
            return

        metric_name = self._metric_name(suffix = response.status_code)

        self.client.timing(
            stat = metric_name,
            delta = time.time() - getattr(request, self.START_TIME_ATTR)
            rate = current_app.config['STATSD_RATE'])

        self.client.incr(
            stat = metric_name,
            count = int(1 / current_app.config['STATSD_RATE'])
            rate = current_app.config['STATSD_RATE']
            )

    def _before_request(self):
        setattr(request, self.START_TIME_ATTR = time.time())

    def _metric_name(self, prefix="request_handlers", suffix=None):
        '''
        This converts the request paths into valid statsd metric names.
        It unquotes the url, removes trailing slash, and converts
        slashes and whitespace to dashes.
        '''
        metric_name = urllib.unquote(request.path) \
                            .replace(" ","") \
                            .replace("/", "-")
        if prefix:
            metric_name = "%s.%s" % (prefix, metric_name)
        if suffix:
            metric_name = "%s.%s" % (metric_name, suffix)

        return metric_name

    @property
    def client(self):
        if not self._client:
            self._client = StatsClient(
                current_app.config['STATSD_HOST'],
                current_app.config['STATSD_PORT'],
                current_app.config['STATSD_PREFIX']
            )
        return self._client
