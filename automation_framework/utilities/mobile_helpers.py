from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from appium.options.common.base import AppiumOptions
import time
from typing import Dict, Any, List
import logging
import os
import subprocess
from selenium.webdriver.common.by import By

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileHelper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Appium driver"""
        try:
            # Check if app is installed
            if not self.is_app_installed():
                logger.info("Installing OpenWeather app...")
                self.install_app()
            
            # Driver setup
            options = AppiumOptions()
            options.set_capability('platformName', 'Android')
            options.set_capability('automationName', 'UiAutomator2')
            options.set_capability('deviceName', 'emulator-5554')
            options.set_capability('appPackage', 'uk.co.openweather')
            options.set_capability('appActivity', 'uk.co.openweather.MainActivity')
            options.set_capability('noReset', True)
            options.set_capability('autoGrantPermissions', True)
            options.set_capability('newCommandTimeout', 3600)
            
            logger.info("=== Driver Setup ===")
            logger.info(f"Capabilities: {options.to_capabilities()}")
            
            # Connect to Appium server
            appium_url = 'http://127.0.0.1:4723'
            logger.info(f"Connecting to Appium server at: {appium_url}")
            
            self.driver = webdriver.Remote(
                command_executor=appium_url,
                options=options
            )
            self.wait = WebDriverWait(self.driver, 20)
            
            # Check session state
            logger.info("Checking session state...")
            self.driver.current_activity
            logger.info("Session is active")
            
            # Launch app
            logger.info("Launching OpenWeather app...")
            self.driver.activate_app('uk.co.openweather')
            
            logger.info("=== Driver setup completed successfully ===")
            return self.driver
            
        except Exception as e:
            logger.error(f"Error during driver setup: {str(e)}")
            logger.error(f"Full error stack: {e.__class__.__name__}: {str(e)}")
            raise

    def is_app_installed(self):
        """Check if app is installed"""
        try:
            result = subprocess.run(
                [r"C:\Users\aleks\AppData\Local\Android\Sdk\platform-tools\adb.exe", 'shell', 'pm', 'list', 'packages', 'uk.co.openweather'],
                capture_output=True,
                text=True
            )
            return 'uk.co.openweather' in result.stdout
        except Exception as e:
            logger.error(f"Error checking app installation: {str(e)}")
            return False

    def install_app(self):
        """Install app"""
        try:
            apk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'OpenWeather_1.1.7_APKPure.apk')
            logger.info(f"APK path: {apk_path}")
            
            if not os.path.exists(apk_path):
                raise Exception(f"APK file not found at: {apk_path}")
            
            result = subprocess.run(
                [r"C:\Users\aleks\AppData\Local\Android\Sdk\platform-tools\adb.exe", 'install', apk_path],
                capture_output=True,
                text=True
            )
            
            if 'Success' not in result.stdout:
                raise Exception(f"App installation error: {result.stdout}")
            
            logger.info("App installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing app: {str(e)}")
            raise
        
    def configure_celsius(self):
        """Configure temperature display in Celsius"""
        try:
            # Wait for main screen to load
            self.logger.info("Waiting for main screen to load...")
            self.wait.until(EC.presence_of_element_located((AppiumBy.ID, "uk.co.openweather:id/action_bar_root")))
            
            # Find settings button using content-desc
            self.logger.info("Looking for settings button...")
            settings_button = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().className(\"android.view.ViewGroup\").instance(11)"))
            )
            self.logger.info("Settings button found, clicking...")
            settings_button.click()
            
            # Wait for settings screen to load
            self.logger.info("Waiting for settings screen to load...")
            self.wait.until(EC.presence_of_element_located((AppiumBy.ID, "uk.co.openweather:id/action_bar_root")))
            
            # Find units switch
            self.logger.info("Looking for units switch...")
            units_switch = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup"))
            )
            self.logger.info("Switch found, clicking...")
            units_switch.click()
            
            # Find Celsius switch
            self.logger.info("Looking for Celsius switch")
            units_switch_c = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "°C"))
            )
            self.logger.info("Switch found, clicking...")
            units_switch_c.click()
            
            # Go back
            self.logger.info("Going back...")
            back_button = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Navigate up"))
            )
            back_button.click()
            
            # Find units switch again
            self.logger.info("Looking for units switch...")
            units_switch = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup"))
            )
            # Go back
            self.logger.info("Going back...")
            back_s_button = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().description(\"Navigate up\")"))
            )
            back_s_button.click()
            
            self.logger.info("Temperature display configured to Celsius")
        except Exception as e:
            self.logger.error(f"Error configuring Celsius: {str(e)}")
            raise
            
    def get_temperature_for_city(self, city_name: str) -> Dict[str, float]:
        """
        Get temperature for city
        
        Args:
            city_name: City name
            
        Returns:
            Dict with temperature and feels like
        """
        try:
            # Search for city
            search_button = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Search"]'))
            )
            search_button.click()
            
            search_input = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Search")'))
            )
            search_input.clear()
            search_input.send_keys(city_name)
            
            # Press Enter
            self.logger.info("Pressing Enter key...")
            search_input.send_keys(Keys.ENTER)
            
            # Wait for city list to appear
            self.logger.info("Waiting for city list to appear...")
            time.sleep(3)  # Increased wait time
            
            # Wait for search result
            self.logger.info(f"Searching for city {city_name}...")
            city_result = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{city_name}')]"))
            )
            self.logger.info(f"City {city_name} found, clicking...")
            city_result.click()
            
            # Get temperature
            temperature_element = self.wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "°C")]'))
            )
            temperature = int(temperature_element.text.replace('°C', '').strip())
            
            # Get feels like
            feels_like_element = self.wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Feels like ")]'))
            )
            feels_like = int(feels_like_element.text.replace('°C', '').replace('Feels like ', '').strip())

            self.logger.info(f"Successfully retrieved data for city {city_name}")
            return {
                'temperature': temperature,
                'feels_like': feels_like
            }
        except TimeoutException:
            self.logger.error(f"Timeout while searching for city {city_name}")
            raise
        except NoSuchElementException:
            self.logger.error(f"Element not found for city {city_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting data for city {city_name}: {str(e)}")
            raise
            
    def close(self):
        """Close driver"""
        try:
            if self.driver:
                self.driver.quit() 
                self.logger.info("Driver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing driver: {str(e)}")
            raise 