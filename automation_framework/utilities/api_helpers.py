import requests
import configparser
import os
from typing import Dict, Any

class ApiHelper:
    def __init__(self):
        self.config = self._load_config()
        self.api_key = self.config['API']['API_KEY']
        self.base_url = self.config['API']['BASE_URL']
        
    def _load_config(self) -> configparser.ConfigParser:
        """
        Loads configuration from config.ini file
        
        Returns:
            ConfigParser with settings
            
        Raises:
            FileNotFoundError: if config file is not found
            configparser.Error: if config file has incorrect format
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        config.read(config_path)
        
        # Check for required sections and parameters
        required_sections = ['API', 'DB']
        required_params = {
            'API': ['API_KEY', 'BASE_URL'],
            'DB': ['DB_NAME']
        }
        
        for section in required_sections:
            if section not in config:
                raise configparser.Error(f"Missing section {section} in config")
                
            for param in required_params[section]:
                if param not in config[section]:
                    raise configparser.Error(f"Missing parameter {param} in section {section}")
                    
        return config
        
    def get_current_weather(self, city_id: int) -> Dict[str, Any]:
        """
        Get current weather for city by its ID
        
        Args:
            city_id: City ID
            
        Returns:
            Dict with weather data
            
        Raises:
            requests.exceptions.RequestException: if API request fails
            ValueError: if API response doesn't contain expected data
        """
        params = {
            'id': city_id,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'en'
        }
        
        print(f"Calling API for city {city_id} with parameters: {params}")
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            print(f"API error: {response.status_code} - {response.text}")
            response.raise_for_status()
            
        data = response.json()
        
        # Check for required data
        if 'main' not in data:
            raise ValueError(f"API response doesn't contain weather data: {data}")
            
        if 'temp' not in data['main'] or 'feels_like' not in data['main']:
            raise ValueError(f"API response doesn't contain temperature: {data['main']}")
            
        return data
