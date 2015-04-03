#!/usr/bin/env python

import time

from flask import request, current_app
import statsd

class Statsd(object):
    '''Statsd Extension for Flask

    This extension does a couple things
    1. Creates status code and latency metrics for all app request handlers
    2. Provides a client with flask-specific metric naming so you don't have
       to do it inline.

    - - - - - - - - - - - -

    app = Flask('myapp')
    statsd = Statsd(app, config={'STATSD_PREFIX': 'myprefix'})

    @app.route('/')
    def index():

        statsd.incr('doing_stuff')
        print 'DOING STUFF'

        with statsd.timer('doing_more_stuff'):
          print 'DOING MORE STUFF'

        return 'OK'

    - - - - - - - - - - - -

    Metrics follow the naming scheme:
    <prefix (optional)>.<app_name>.<metric_name>

    The following code will produce the following metrics:
     - COUNTER: stats.myprefix.myapp.doing_stuff
     - COUNTER: stats.myprefix.myapp.request_handlers.index.<status_code>
     - TIMER: stats.timers.myprefix.myapp.request_handlers.index.<status_code>
     - TIMER: stats.timers.myprefix.myapp.doing_more_stuff


    '''
    START_TIME_ATTR = "statsd_start_time"
    __client = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('STATSD_ENABLE_REQUEST_HANDLERS', True)
        app.config.setdefault('STATSD_HOST', 'localhost')
        app.config.setdefault('STATSD_PORT', 8125)
        app.config.setdefault('STATSD_PREFIX', None)
        app.config.setdefault('STATSD_RATE', 1)

        if app.config['STATSD_ENABLE_REQUEST_HANDLERS']:
            app.before_request(self._before_request)
            app.after_request(self._after_request)

    ###
    # Main Interface (proxy commands to pystatsd)
    ###


    def timer(self, stat, rate=None):
        return self._client.timer(
            rate = rate or current_app.config['STATSD_RATE'],
            stat = self._metric_name(stat)
        )

    def timing(self, stat, delta, rate=None):
        return self._client.timing(
            rate = rate or current_app.config['STATSD_RATE'],
            delta = delta,
            stat = self._metric_name(stat)
        )

    def incr(self, stat, count=1, rate=None):
        return self._client.incr(
            rate = rate or current_app.config['STATSD_RATE'],
            count = count,
            stat = self._metric_name(stat)
        )

    def decr(self, stat, count=1, rate=None):
        return self.incr(stat, -count, rate)

    ###
    # HELPERS
    ###

    def _metric_name(self, name):
        return "%s.%s" % (current_app.name, name)

    @property
    def _client(self):
        if not self.__client:
            self.__client = statsd.StatsClient(
                current_app.config['STATSD_HOST'],
                current_app.config['STATSD_PORT'],
                current_app.config['STATSD_PREFIX']
            )
        return self.__client


    ###
    # REQUEST HANDLER FUNCTIONALITY
    ###
    def _after_request(self, response):
        if not hasattr(request, self.START_TIME_ATTR) or \
           current_app.config['STATSD_RATE'] == 0 or \
           not request.endpoint:
            return response

        metric_name = ".".join(["request_handlers",
                                request.endpoint,
                                str(response.status_code)])

        self.timing(
            metric_name,
            int((time.time() - getattr(request, self.START_TIME_ATTR))*1000)
        )
        self.incr(metric_name)

        return response

    def _before_request(self):
        setattr(request, self.START_TIME_ATTR, time.time())
