import flask
import mock
import unittest

import flask_statsd

class FlaskStatsdTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)

        @app.route('/')
        def index():
            return "Test", 200

        @app.route('/fail')
        def fail():
            return "FAIL", 500

        self.statsd = flask_statsd.Statsd(app)

        self.test_client = app.test_client()

    def test_successful_response(self):
        with mock.patch('flask_statsd.Statsd.client') as mock_client:
            self.test_client.get("/")

            mock_client.incr.assert_called_with(
                stat = 'request_handlers.index.200',
                count = mock.ANY,
                rate = mock.ANY)

            mock_client.timing.assert_called_with(
                stat = 'request_handlers.index.200',
                delta = mock.ANY,
                rate = mock.ANY)

    def test_failed_response(self):
        with mock.patch('flask_statsd.Statsd.client') as mock_client:
            self.test_client.get("/fail")

            mock_client.incr.assert_called_with(
                stat = 'request_handlers.fail.500',
                count = mock.ANY,
                rate = mock.ANY)

            mock_client.timing.assert_called_with(
                stat = 'request_handlers.fail.500',
                delta = mock.ANY,
                rate = mock.ANY)

if __name__ == '__main__':
    unittest.main()
