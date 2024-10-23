import requests
import dpath
from typing import Optional, MutableMapping


class APIClient:
    """Api client to perform requests with optional JSON path extraction."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session = requests.Session()

    def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json_path: Optional[str] = None,
        close_session: bool = True,
        *args,
        **kwargs,
    ):
        """Perform GET request and optionally extract value and status code."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(
                url, params=params, headers=headers, *args, **kwargs
            )
            response.raise_for_status()
            json_data = response.json()
            if json_path:
                return (
                    self.extract_json_value(json_data, json_path),
                    response.status_code,
                )
            return json_data, response.status_code
        except requests.RequestException as e:
            err = f"Error during GET request: {e}"
            raise requests.RequestException(err)
        finally:
            if close_session:
                self.close()

    def post(
        self,
        endpoint: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        json_path: Optional[str] = None,
        close_session: bool = False,
        *args,
        **kwargs,
    ):
        """Perform GET request and optionally extract value and status code."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.post(
                url, data=data, json=json, headers=headers, *args, **kwargs
            )
            response.raise_for_status()
            json_data = response.json()
            if json_path:
                return (
                    self.extract_json_value(json_data, json_path),
                    response.status_code,
                )
            return json_data, response.status_code
        except requests.RequestException as e:
            err = f"Error during POST request: {e}"
            raise requests.RequestException(err)
        finally:
            if close_session:
                self.close()

    def options(
        self,
        endpoint: str,
        headers: Optional[dict] = None,
        close_session: bool = False,
    ):
        """Perform an OPTIONS request and return the headers."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.options(url, headers=headers)
            response.raise_for_status()
            json_data = response.headers
            return json_data, response.status_code
        except requests.RequestException as e:
            err = f"Error during OPTIONS request: {e}"
            raise requests.RequestException(err)
        finally:
            if close_session:
                self.close()

    @staticmethod
    def extract_json_value(json_data: dict | list, path: str):
        """Extract a value from a JSON object using a specified path with dpath."""
        try:
            if isinstance(json_data, list):
                json_data: MutableMapping
                return dpath.values(json_data, path)[0]
            return dpath.get(json_data, path)
        except KeyError:
            err = f"Could not extract value from JSON data using {path=}"
            raise KeyError(err)

    def close(self):
        """Close the current session."""
        self.session.close()
