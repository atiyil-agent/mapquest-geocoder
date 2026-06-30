import argparse
import os
import sys

import requests

API_KEY_ENV_VAR = "MAPQUEST_API_KEY"

# HTTPS only; query parameters are encoded by requests.
MAPQUEST_GEOCODE_URL = "https://www.mapquestapi.com/geocoding/v1/address"
DEFAULT_TIMEOUT = 15.0


def get_coordinates(api_key, location, timeout=DEFAULT_TIMEOUT):
    """
    Retrieve latitude and longitude for a given city or town using the MapQuest Geocoding API.

    On failure, returns (None, None). Errors are reported to stderr without including the API
    key or raw network exception text (which may echo the request URL containing the key).
    """
    params = {"key": api_key, "location": location}

    try:
        response = requests.get(
            MAPQUEST_GEOCODE_URL,
            params=params,
            timeout=timeout,
        )
    except requests.exceptions.RequestException:
        print(
            "Network error: could not complete the request to the geocoding service.",
            file=sys.stderr,
        )
        return None, None

    try:
        data = response.json()
    except ValueError:
        if response.status_code != 200:
            print(
                "HTTP error: the geocoding service returned an error "
                f"(status {response.status_code}).",
                file=sys.stderr,
            )
        else:
            print(
                "Invalid response from the geocoding service (not JSON).",
                file=sys.stderr,
            )
        return None, None

    if response.status_code != 200:
        # Do not print response body; it may be verbose and is unnecessary for the CLI user.
        print(
            "HTTP error: the geocoding service returned an error "
            f"(status {response.status_code}).",
            file=sys.stderr,
        )
        return None, None

    info = data.get("info") or {}
    if info.get("statuscode") != 0:
        messages = info.get("messages")
        if messages:
            print("API error:", messages, file=sys.stderr)
        else:
            print("API error: geocoding request was not successful.", file=sys.stderr)
        return None, None

    try:
        locations = data["results"][0]["locations"]
        if not locations:
            print("API error: no locations returned.", file=sys.stderr)
            return None, None
        location_data = locations[0]["latLng"]
        return location_data["lat"], location_data["lng"]
    except (KeyError, IndexError, TypeError):
        print(
            "API error: unexpected response shape from the geocoding service.",
            file=sys.stderr,
        )
        return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve latitude and longitude for a given city or town using the MapQuest Geocoding API."
    )
    parser.add_argument("location", help="City or town name")
    parser.add_argument(
        "--api-key",
        help=f"MapQuest API key (defaults to the {API_KEY_ENV_VAR} environment variable)",
    )
    args = parser.parse_args()

    location = (args.location or "").strip()
    if not location:
        parser.error("location must not be empty.")

    if args.api_key is not None:
        # An explicit flag is treated as authoritative; an empty value is an error
        # rather than silently falling back to the environment.
        api_key = args.api_key.strip()
        if not api_key:
            parser.error("--api-key must not be empty.")
    else:
        api_key = (os.environ.get(API_KEY_ENV_VAR) or "").strip()
        if not api_key:
            parser.error(
                f"an API key is required: pass --api-key or set the {API_KEY_ENV_VAR} "
                "environment variable."
            )

    lat, lng = get_coordinates(api_key, location)

    if lat is not None and lng is not None:
        print(f"Latitude: {lat}, Longitude: {lng}")
        sys.exit(0)

    print("Could not retrieve the coordinates for the provided location.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
