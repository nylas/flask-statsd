import flask
import mock
import unittest

import flask_statsd

class FlaskStatsdTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask("myapp")
        statsd = flask_statsd.Statsd(app)
        self.test_client = app.test_client()

        @app.route('/')
        def index():
            statsd.incr("test_incr")

            with statsd.timer("test_timer"):
                pass

            return "Test", 200

        @app.route('/fail')
        def fail():
            return "FAIL", 500


    def test_successful_response(self):
        with mock.patch('flask_statsd.Statsd._client') as mock_client:
            self.test_client.get("/")

            mock_client.incr.call_args_list == [
                mock.call(count=1, stat='myapp.test_incr', rate=1),
                mock.call(count=1, stat='myapp.request_handlers.index.200', rate=1)
            ]

            mock_client.timing.assert_called_with(
                stat = 'myapp.request_handlers.index.200',
                delta = mock.ANY,
                rate = mock.ANY)

            mock_client.timer.assert_called_with(
                stat = 'myapp.test_timer',
                rate = mock.ANY)

    def test_failed_response(self):
        with mock.patch('flask_statsd.Statsd._client') as mock_client:
            self.test_client.get("/fail")

            mock_client.incr.assert_called_with(
                stat = 'myapp.request_handlers.fail.500',
                count = 1,
                rate = mock.ANY)

            mock_client.timing.assert_called_with(
                stat = 'myapp.request_handlers.fail.500',
                delta = mock.ANY,
                rate = mock.ANY)

if __name__ == '__main__':
    unittest.main()
