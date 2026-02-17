"""Weather data fetching module with API integration"""

import os
import requests
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

API_KEY = os.getenv("WEATHERAPI_KEY")

ZONES: Dict[str, Dict[str, float]] = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867}
}

def fetch_weather_data(use_synthetic: bool = False) -> pd.DataFrame:
    """
    Fetch real-time weather data from WeatherAPI.
    Falls back to synthetic data if API is unavailable.
    
    Args:
        use_synthetic: Force synthetic data generation
        
    Returns:
        DataFrame with weather and demographic data for all zones
        
    Raises:
        ValueError: If API key is missing and synthetic=False
    """
    if use_synthetic:
        logger.info("Using synthetic data generation")
        return _generate_synthetic_data()
    
    if not API_KEY:
        logger.warning("WeatherAPI key not found. Switching to synthetic data.")
        return _generate_synthetic_data()
    
    records = []
    failed_zones = []
    
    for city, coords in ZONES.items():
        try:
            weather_data = _fetch_single_zone(city, coords)
            if weather_data:
                records.append(weather_data)
            else:
                failed_zones.append(city)
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            failed_zones.append(city)
    
    if not records:
        logger.error("All zones failed. Falling back to synthetic data.")
        return _generate_synthetic_data()
    
    if failed_zones:
        logger.warning(f"Failed to fetch data for zones: {failed_zones}")
    
    df = pd.DataFrame(records)
    logger.info(f"Successfully fetched data for {len(records)} zones")
    return df

def _fetch_single_zone(city: str, coords: Dict[str, float]) -> Optional[Dict]:
    """
    Fetch weather data for a single zone with retries.
    
    Args:
        city: City name
        coords: Dictionary with 'lat' and 'lon' keys
        
    Returns:
        Dictionary with zone data or None if failed
    """
    from config import API_TIMEOUT, API_RETRY_COUNT
    
    url = (
        f"https://api.weatherapi.com/v1/forecast.json?"
        f"key={API_KEY}&q={coords['lat']},{coords['lon']}&days=2&aqi=yes&hours=24"
    )
    
    for attempt in range(API_RETRY_COUNT):
        try:
            response = requests.get(url, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            forecast = data.get("forecast", {}).get("forecastday", [{}])[0]
            
            rainfall = float(current.get("precip_mm", 0))
            forecast_rain = sum(
                float(hour.get("precip_mm", 0))
                for hour in forecast.get("hour", [])
            )
            
            return {
                "Zone": city,
                "Rainfall": max(0, rainfall),  # Ensure non-negative
                "River_Level": max(0, float(current.get("precip_last_3h_mm", 5))),
                "Soil_Saturation": min(1.0, float(current.get("humidity", 60)) / 100),
                "Forecast_Rainfall": max(0, forecast_rain),
                "Population_Density": 3000,
                "Elderly_Percentage": 12,
                "Poverty_Index": 0.4,
                "Drainage_Score": 0.6,
                "Hospital_Capacity": 300,
                "Critical_Facilities": 10,
                "Road_Access": 0.8,
                "Temperature": float(current.get("temp_c", 25)),
                "Wind_Speed": float(current.get("wind_kph", 0))
            }
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {city} (attempt {attempt+1}/{API_RETRY_COUNT})")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error fetching {city} (attempt {attempt+1}/{API_RETRY_COUNT})")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {city}: {e.response.status_code}")
            break
        except Exception as e:
            logger.error(f"Unexpected error fetching {city}: {e}")
            break
    
    return None

def fetch_hourly_forecast(use_synthetic: bool = False) -> pd.DataFrame:
    """
    Fetch hourly temperature forecast for all zones.
    
    Args:
        use_synthetic: Force synthetic data generation
        
    Returns:
        DataFrame with hourly forecast: Zone, Hour, Datetime, Temperature
    """
    if use_synthetic:
        logger.info("Using synthetic hourly forecast")
        return _generate_synthetic_timeseries()
    
    if not API_KEY:
        logger.warning("WeatherAPI key not found. Using synthetic forecast.")
        return _generate_synthetic_timeseries()
    
    records = []
    
    for city, coords in ZONES.items():
        try:
            url = (
                f"https://api.weatherapi.com/v1/forecast.json?"
                f"key={API_KEY}&q={coords['lat']},{coords['lon']}&days=2&aqi=yes"
            )
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get hourly data from forecast
            forecast_days = data.get("forecast", {}).get("forecastday", [])
            hour_counter = 0
            
            for day in forecast_days:
                for hour_data in day.get("hour", []):
                    records.append({
                        "Zone": city,
                        "Hour": hour_counter,
                        "Datetime": hour_data.get("time", ""),
                        "Temperature": float(hour_data.get("temp_c", 25)),
                        "Rainfall": float(hour_data.get("precip_mm", 0)),
                        "Humidity": float(hour_data.get("humidity", 60)),
                        "Wind_Speed": float(hour_data.get("wind_kph", 0))
                    })
                    hour_counter += 1
                    
                    # Limit to 24 hours for clarity
                    if hour_counter >= 24:
                        break
                if hour_counter >= 24:
                    break
                    
        except Exception as e:
            logger.warning(f"Failed to fetch hourly forecast for {city}: {e}")
            # Add synthetic fallback
            fallback = _generate_synthetic_timeseries(city_filter=city)
            records.extend(fallback.to_dict('records'))
    
    if records:
        logger.info(f"Fetched hourly forecast for {len(set([r['Zone'] for r in records]))} zones")
        return pd.DataFrame(records)
    
    return _generate_synthetic_timeseries()

def _generate_synthetic_timeseries(city_filter: Optional[str] = None) -> pd.DataFrame:
    """
    Generate synthetic hourly temperature data for visualization.
    
    Args:
        city_filter: Specific city to generate for, or None for all
        
    Returns:
        DataFrame with hourly forecast
    """
    import numpy as np
    np.random.seed(42)
    
    records = []
    cities = [city_filter] if city_filter else list(ZONES.keys())
    
    for city_idx, city in enumerate(cities):
        # Base temperature for the city
        base_temp = 25 + city_idx * 2
        
        for hour in range(24):
            # Temperature changes with time of day (cooler at night, warmer mid-day)
            time_factor = np.sin(hour / 24 * np.pi)  # 0 to 1 pattern
            temp = base_temp + time_factor * 5 + np.random.normal(0, 1)
            
            records.append({
                "Zone": city,
                "Hour": hour,
                "Datetime": f"2026-02-17 {hour:02d}:00",
                "Temperature": round(max(15, min(40, temp)), 1),
                "Rainfall": max(0, np.random.normal(5, 3)) if hour > 12 else max(0, np.random.normal(2, 1)),
                "Humidity": 40 + time_factor * 30 + np.random.normal(0, 5),
                "Wind_Speed": 10 + abs(np.random.normal(0, 4))
            })
    
    return pd.DataFrame(records)

def _generate_synthetic_data() -> pd.DataFrame:
    """
    Generate synthetic weather data for testing and fallback.
    
    Returns:
        DataFrame with synthetic data for all zones
    """
    import numpy as np
    np.random.seed(42)
    
    records = []
    for city in ZONES.keys():
        records.append({
            "Zone": city,
            "Rainfall": np.random.uniform(10, 100),
            "River_Level": np.random.uniform(2, 8),
            "Soil_Saturation": np.random.uniform(0.3, 0.9),
            "Forecast_Rainfall": np.random.uniform(20, 80),
            "Population_Density": np.random.uniform(2000, 4000),
            "Elderly_Percentage": np.random.uniform(8, 16),
            "Poverty_Index": np.random.uniform(0.2, 0.6),
            "Drainage_Score": np.random.uniform(0.3, 0.8),
            "Hospital_Capacity": np.random.uniform(200, 400),
            "Critical_Facilities": np.random.randint(5, 15),
            "Road_Access": np.random.uniform(0.5, 0.95),
            "Temperature": np.random.uniform(20, 35),
            "Wind_Speed": np.random.uniform(5, 30)
        })
    
    logger.info(f"Generated synthetic data for {len(records)} zones")
    return pd.DataFrame(records)
