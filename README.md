# MapQuest Geocoder

This package provides a command-line tool that, given a city or town name, retrieves its latitude and longitude using the MapQuest Geocoding API.

## Installation
- Activate your virtual environment
  - macOS/Linux (in the project directory `mapquest-geocoder`)
    - `source bin/activate`
  - Windows (using mapquest-geocoder\Scripts\activate.bat or Activate.ps1)
- Clone the repository and install the package:
  - `pip install .`

## Usage

- Run the command below to get the latitude and longitude of a city or town:
  - `mapquest-geocode "CITY_OR_TOWN_NAME" --api-key YOUR_API_KEY`
  - Example:
    - `mapquest-geocode "New York" --api-key YOUR_API_KEY`

### Providing the API key

The API key can be supplied in either of two ways:

- `--api-key` flag (takes precedence):
  - `mapquest-geocode "New York" --api-key YOUR_API_KEY`
- `MAPQUEST_API_KEY` environment variable (used when `--api-key` is omitted):
  - `export MAPQUEST_API_KEY=YOUR_API_KEY`
  - `mapquest-geocode "New York"`

If neither is provided, the command exits with an error.
