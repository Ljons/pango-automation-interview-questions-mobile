import sqlite3
import configparser
import os
from typing import Dict, Any, List
from datetime import datetime

class DBHelper:
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')
        self.config.read(config_path)
        self.db_name = self.config['DB']['DB_NAME']
        self._create_table()
    
    def _create_table(self):
        """Creates table for storing weather data"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Drop old table if exists
            cursor.execute('DROP TABLE IF EXISTS weather_data')
            
            # Create new table with correct structure
            cursor.execute('''
                CREATE TABLE weather_data (
                    city_id INTEGER PRIMARY KEY,
                    api_temperature REAL,
                    api_feels_like REAL,
                    mobile_temperature REAL,
                    mobile_feels_like REAL,
                    average_temperature REAL,
                    temperature_difference REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def insert_api_weather_data(self, city_id: int, temperature: float, feels_like: float):
        """
        Insert weather data from API into database
        
        Args:
            city_id: City ID
            temperature: Temperature
            feels_like: Feels like temperature
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO weather_data 
                (city_id, api_temperature, api_feels_like, average_temperature)
                VALUES (?, ?, ?, ?)
            ''', (city_id, temperature, feels_like, temperature))
            conn.commit()
    
    def insert_mobile_weather_data(self, city_id: int, temperature: float, feels_like: float):
        """
        Insert weather data from mobile app into database
        
        Args:
            city_id: City ID
            temperature: Temperature
            feels_like: Feels like temperature
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Update mobile app data
            cursor.execute('''
                UPDATE weather_data 
                SET mobile_temperature = ?,
                    mobile_feels_like = ?,
                    temperature_difference = ABS(api_temperature - ?),
                    average_temperature = (api_temperature + ?) / 2
                WHERE city_id = ?
            ''', (temperature, feels_like, temperature, temperature, city_id))
            
            # If record doesn't exist, create new one
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO weather_data 
                    (city_id, mobile_temperature, mobile_feels_like, average_temperature)
                    VALUES (?, ?, ?, ?)
                ''', (city_id, temperature, feels_like, temperature))
            
            conn.commit()
    
    def get_weather_data(self, city_id: int) -> Dict[str, Any]:
        """
        Get weather data for city
        
        Args:
            city_id: City ID
            
        Returns:
            Dict with weather data
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT api_temperature, api_feels_like, 
                       mobile_temperature, mobile_feels_like,
                       average_temperature, temperature_difference
                FROM weather_data
                WHERE city_id = ?
            ''', (city_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'api_temperature': result[0],
                    'api_feels_like': result[1],
                    'mobile_temperature': result[2],
                    'mobile_feels_like': result[3],
                    'average_temperature': result[4],
                    'temperature_difference': result[5]
                }
            return None
            
    def get_cities_with_discrepancies(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """
        Get list of cities with temperature discrepancies
        
        Args:
            threshold: Discrepancy threshold in degrees
            
        Returns:
            List of cities with discrepancies
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city_id, api_temperature, mobile_temperature,
                       temperature_difference, timestamp
                FROM weather_data
                WHERE temperature_difference > ?
                ORDER BY temperature_difference DESC
            ''', (threshold,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'city_id': row[0],
                    'api_temperature': row[1],
                    'mobile_temperature': row[2],
                    'temperature_difference': row[3],
                    'timestamp': row[4]
                })
            return results

    def get_city_with_highest_average_temp(self) -> Dict[str, Any]:
        """
        Get city with highest average temperature
        
        Returns:
            Dict with city data and its temperature
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city_id, average_temperature
                FROM weather_data
                ORDER BY average_temperature DESC
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                return {
                    'city_id': result[0],
                    'average_temperature': result[1]
                }
            return None

