import pytest
import requests
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DBHelper

# List of city IDs for testing
CITY_IDS = [
    2643743,  # London
    1850147,  # Tokyo
    5128581,  # New York
    524901,   # Moscow
    703448,   # Kyiv
]

# Dictionary for storing city names
CITY_NAMES = {
    2643743: "London",
    1850147: "Tokyo",
    5128581: "New York",
    524901: "Moscow",
    703448: "Kyiv"
}

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

@pytest.fixture(scope="module")
def db():
    return DBHelper()

def test_get_current_weather(api, db):
    """
    Test checks:
    1. API response status code (should be 200)
    2. Data storage in DB
    3. Data consistency between DB and API
    """
    for city_id in CITY_IDS:
        # Get data from API
        params = {
            'id': city_id,
            'appid': api.api_key,
            'units': 'metric',
            'lang': 'en'
        }
        
        response = requests.get(api.base_url, params=params)
        print(f"Status code for city {city_id}: {response.status_code}")
        
        # Check status code
        assert response.status_code == 200, \
            f"Unexpected status code {response.status_code} for city {city_id}. Expected 200."
        
        weather_data = response.json()
        
        # Check data presence
        assert weather_data is not None, f"Failed to get data for city {city_id}"
        assert 'main' in weather_data, f"Response for city {city_id} does not contain weather data"
        assert 'temp' in weather_data['main'], f"Response for city {city_id} does not contain temperature"
        
        # Get temperature and feels like
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        
        # Save data to DB
        db.insert_api_weather_data(city_id, temperature, feels_like)
        
        # Get data from DB
        db_data = db.get_weather_data(city_id)
        
        # Check data consistency
        assert db_data is not None, f"Data for city {city_id} not found in DB"
        assert abs(db_data['api_temperature'] - temperature) < 0.01, \
            f"Temperature in DB ({db_data['api_temperature']}) does not match API ({temperature})"
        assert abs(db_data['api_feels_like'] - feels_like) < 0.01, \
            f"Feels like in DB ({db_data['api_feels_like']}) does not match API ({feels_like})"

def test_multiple_cities_weather_data(api, db):
    """
    Test checks:
    1. Data storage for multiple cities
    2. Average temperature calculation
    3. Data consistency between API and DB
    4. City with highest temperature identification
    """
    # Collect data for all cities
    for city_id in CITY_IDS:
        params = {
            'id': city_id,
            'appid': api.api_key,
            'units': 'metric',
            'lang': 'en'
        }
        
        response = requests.get(api.base_url, params=params)
        assert response.status_code == 200, \
            f"Unexpected status code {response.status_code} for city {city_id}"
        
        weather_data = response.json()
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        
        # Save data to DB
        db.insert_api_weather_data(city_id, temperature, feels_like)
        
        # Check data in DB
        db_data = db.get_weather_data(city_id)
        assert db_data is not None, f"Data for city {city_id} not found in DB"
        assert abs(db_data['api_temperature'] - temperature) < 0.01, \
            f"Temperature in DB ({db_data['api_temperature']}) does not match API ({temperature})"
        assert abs(db_data['api_feels_like'] - feels_like) < 0.01, \
            f"Feels like in DB ({db_data['api_feels_like']}) does not match API ({feels_like})"
    
    # Get city with highest average temperature
    hottest_city = db.get_city_with_highest_average_temp()
    assert hottest_city is not None, "Failed to find city with highest temperature"
    
    # Print result
    city_name = CITY_NAMES.get(hottest_city['city_id'], f"City with ID {hottest_city['city_id']}")
    print(f"\nCity with highest average temperature: {city_name}")
    print(f"Average temperature: {hottest_city['average_temperature']:.2f}°C")


