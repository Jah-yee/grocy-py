import pytest
from unittest.mock import MagicMock
from grocy.errors import GrocyError


class TestGrocyError:
    def test_html_error_page(self):
        """Non-JSON body (e.g. reverse proxy 502 HTML page) should not raise JSONDecodeError."""
        response = MagicMock()
        response.status_code = 502
        response.text = "<html><body>Bad Gateway</body></html>"
        response.json.side_effect = ValueError("Expecting value")

        error = GrocyError(response)
        assert error.status_code == 502
        assert error.message == "<html><body>Bad Gateway</body></html>"

    def test_json_without_error_message(self):
        """JSON body without 'error_message' key should not raise KeyError."""
        response = MagicMock()
        response.status_code = 400
        response.text = '{"detail": "Invalid request"}'
        response.json.return_value = {"detail": "Invalid request"}

        error = GrocyError(response)
        assert error.status_code == 400
        assert error.message == '{"detail": "Invalid request"}'

    def test_json_with_error_message(self):
        """JSON body with 'error_message' key should use that message."""
        response = MagicMock()
        response.status_code = 400
        response.text = '{"error_message": "Object not found"}'
        response.json.return_value = {"error_message": "Object not found"}

        error = GrocyError(response)
        assert error.status_code == 400
        assert error.message == "Object not found"

    def test_empty_body(self):
        """Empty response body should set message to None."""
        response = MagicMock()
        response.status_code = 204
        response.text = ""

        error = GrocyError(response)
        assert error.status_code == 204
        assert error.message is None
