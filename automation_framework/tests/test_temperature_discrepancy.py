import pytest
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DBHelper
from automation_framework.utilities.mobile_helpers import MobileHelper

# Dictionary of cities for testing (ID: name)
CITIES = {
    2643743: "London",
    1850147: "Tokyo",
    5128581: "New York",
    524901: "Moscow",
    703448: "Kyiv",
    2800866: "Brussels",
    2950159: "Berlin",
    3067696: "Prague",
    3117735: "Madrid",
    3169070: "Rome",
    3173435: "Milan",
    3172394: "Naples",
    2988507: "Paris",
    2759794: "Amsterdam",
    2618425: "Copenhagen",
    2673730: "Stockholm",
    658225: "Helsinki",
    6453366: "Oslo",
    6455259: "Paris"
}

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

@pytest.fixture(scope="module")
def db():
    return DBHelper()

@pytest.fixture(scope="module")
def mobile():
    mobile = MobileHelper()
    mobile.setup_driver()
    mobile.configure_celsius()
    yield mobile
    mobile.close()

def test_temperature_discrepancy(api, db, mobile):
    """
    Test checks temperature discrepancies between mobile app and API
    
    Steps:
    1. Get data from API for each city
    2. Get data from mobile app
    3. Compare data and save discrepancies
    4. Generate report about discrepancies
    """
    print("\nComparing temperatures between mobile app and API:")
    print("-" * 80)
    
    for city_id, city_name in CITIES.items():
        # Get data from API
        api_data = api.get_current_weather(city_id)
        api_temp = api_data['main']['temp']
        api_feels_like = api_data['main']['feels_like']
        
        # Save API data to DB
        db.insert_api_weather_data(city_id, api_temp, api_feels_like)
        
        # Get data from mobile app
        mobile_data = mobile.get_temperature_for_city(city_name)
        mobile_temp = mobile_data['temperature']
        mobile_feels_like = mobile_data['feels_like']
        
        # Save mobile app data to DB
        db.insert_mobile_weather_data(city_id, mobile_temp, mobile_feels_like)
        
        # Print data
        print(f"\nCity: {city_name}")
        print(f"API temperature: {api_temp}°C")
        print(f"Mobile temperature: {mobile_temp}°C")
        print(f"Difference: {abs(api_temp - mobile_temp):.2f}°C")
        print("-" * 40)
    
    # Get cities with discrepancies
    discrepancies = db.get_cities_with_discrepancies(threshold=1.0)
    
    if discrepancies:
        print("\nCities with discrepancies more than 1°C:")
        print("-" * 80)
        for city in discrepancies:
            city_name = CITIES.get(city['city_id'], f"City with ID {city['city_id']}")
            print(f"\nCity: {city_name}")
            print(f"API temperature: {city['api_temperature']}°C")
            print(f"Mobile temperature: {city['mobile_temperature']}°C")
            print(f"Difference: {city['temperature_difference']:.2f}°C")
            print(f"Check time: {city['timestamp']}")
    else:
        print("\nNo discrepancies more than 1°C found") 