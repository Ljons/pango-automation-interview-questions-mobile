# Weather Testing Project

This project includes a set of automated test cases and enhancements to verify weather data obtained from the OpenWeatherMap API and the Android OpenWeatherMap Mobile App.

## Table of Contents

1. [Test Cases and Enhancements](#test-cases-and-enhancements)
2. [Installation](#installation)
3. [API Documentation](#api-documentation)
4. [License](#license)

---

## Test Cases and Enhancements

### 1. Verify get_current_weather with Celsius Metric and English Language

- **Validate Status Code**
  - Ensure the HTTP response code is `200` when retrieving current weather data for a set of cities.
- **Insert Temperature and Feels_like Data**
  - Insert temperature and feels_like data into the database for each city.
- **Data Verification**
  - Verify that temperature and feels_like fields in the database match the API response.

---

### 2. Utilize Weather Data for Multiple Cities via City ID

**Example Endpoint:**  
`https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}`

- **Data Insertion**
  - Insert temperature and feels_like data for each city (queried by city ID) into the database.
- **Database Enhancement**
  - Create a new column in the database for average temperature for each city.
- **Data Assertion**
  - Assert that the inserted data matches the API response.
- **Reporting**
  - Print the city with the highest average temperature.

---

### 3. Dynamic API Key and Base URL Configuration

- **Configuration Management**
  - Implement logic to retrieve the `API_KEY` and `BASE_URL` from `config.ini`, ensuring tests can run seamlessly in different environments without code changes.

---

### 4. Mobile Question: City Temperature Discrepancy Analysis

- **APK Installation**
  - Install the Android OpenWeatherMap APK on a device or emulator.
- **Configuration**
  - Configure the mobile app to display temperature in Celsius.
- **Comparative Temperature Analysis**
  - Select at least 20 cities to test.
  - Compare the mobile app’s temperature readings with the OpenWeatherMap API (can use API Endpoint: `https://api.openweathermap.org/data/2.5/weather?id={city id}&appid={API key}`) responses for the same cities.
  - Insert both sets of data (Mobile App and API) into the same database used in previous tests.
- **Reporting**
  - Generate a concise report highlighting any cities where there is a discrepancy between the Mobile App and the API temperature data.

---

## Installation

To set up your environment, run one of the following commands:

- Using the requirements file:
  ```bash
  pip install -r requirements.txt
