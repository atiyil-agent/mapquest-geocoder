import io
import unittest
from unittest.mock import MagicMock, patch

import requests

from mapquest_geocoder.geocode import MAPQUEST_GEOCODE_URL, get_coordinates, main


class TestGetCoordinates(unittest.TestCase):
    def test_success(self):
        payload = {
            "info": {"statuscode": 0},
            "results": [{"locations": [{"latLng": {"lat": 40.7, "lng": -74.0}}]}],
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = payload

        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp) as mock_get:
            lat, lng = get_coordinates("key", "New York", timeout=5.0)

        self.assertEqual((lat, lng), (40.7, -74.0))
        mock_get.assert_called_once_with(
            MAPQUEST_GEOCODE_URL,
            params={"key": "key", "location": "New York"},
            timeout=5.0,
        )

    def test_uses_https_endpoint(self):
        self.assertTrue(MAPQUEST_GEOCODE_URL.lower().startswith("https://"))

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_network_error_does_not_echo_exception_or_key(self, stderr):
        with patch("mapquest_geocoder.geocode.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            lat, lng = get_coordinates("SECRET_KEY", "Boston")
        self.assertEqual((lat, lng), (None, None))
        err = stderr.getvalue()
        self.assertNotIn("SECRET_KEY", err)
        self.assertNotIn("Boston", err)

    def test_http_non_200(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.json.return_value = {}
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))

    def test_api_statuscode_nonzero(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "info": {"statuscode": 400, "messages": ["invalid location"]},
            "results": [],
        }
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))

    def test_invalid_json(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("not json")
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))

    def test_non_200_non_json_body_reports_http_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_resp.json.side_effect = ValueError()
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))

    def test_malformed_results(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"info": {"statuscode": 0}, "results": []}
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))

    def test_empty_locations_list(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "info": {"statuscode": 0},
            "results": [{"locations": []}],
        }
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            lat, lng = get_coordinates("k", "x")
        self.assertEqual((lat, lng), (None, None))


class TestMain(unittest.TestCase):
    def test_exit_zero_on_success(self):
        payload = {
            "info": {"statuscode": 0},
            "results": [{"locations": [{"latLng": {"lat": 1.0, "lng": 2.0}}]}],
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = payload

        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            with patch("sys.argv", ["prog", "Paris", "--api-key", "k"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        self.assertEqual(ctx.exception.code, 0)

    def test_exit_one_on_failure(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.json.return_value = {}
        with patch("mapquest_geocoder.geocode.requests.get", return_value=mock_resp):
            with patch("sys.argv", ["prog", "Paris", "--api-key", "k"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        self.assertEqual(ctx.exception.code, 1)

    def test_empty_location_exits_with_code_2(self):
        with patch("sys.argv", ["prog", "   ", "--api-key", "k"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
        self.assertEqual(ctx.exception.code, 2)

    def test_empty_api_key_exits_with_code_2(self):
        with patch("sys.argv", ["prog", "Paris", "--api-key", "  "]):
            with self.assertRaises(SystemExit) as ctx:
                main()
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
