"""Synthetic data generation for testing and development"""

from typing import Optional
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_zones(n_zones: int = 20, seed: Optional[int] = 42) -> pd.DataFrame:
    """
    Generate synthetic disaster scenario data for testing.
    
    Args:
        n_zones: Number of zones to generate
        seed: Random seed for reproducibility (None for random)
        
    Returns:
        DataFrame with synthetic hazard, vulnerability, and exposure data
    """
    if seed is not None:
        np.random.seed(seed)
    
    data = {
        "Zone": [f"Zone_{i+1:02d}" for i in range(n_zones)],

        # Hazard factors (higher = worse)
        "Rainfall": np.random.uniform(10, 300, n_zones),  # mm
        "River_Level": np.random.uniform(1, 12, n_zones),  # meters
        "Soil_Saturation": np.random.uniform(0.2, 1.0, n_zones),  # 0-1
        "Forecast_Rainfall": np.random.uniform(10, 250, n_zones),  # mm

        # Vulnerability factors
        "Population_Density": np.random.uniform(500, 6000, n_zones),  # persons/km²
        "Elderly_Percentage": np.random.uniform(5, 30, n_zones),  # percent
        "Poverty_Index": np.random.uniform(0.05, 0.9, n_zones),  # 0-1

        # Resilience/Mitigation factors (higher = better)
        "Drainage_Score": np.random.uniform(0.1, 1.0, n_zones),  # 0-1
        "Hospital_Capacity": np.random.uniform(30, 600, n_zones),  # beds

        # Exposure factors
        "Critical_Facilities": np.random.randint(1, 25, n_zones),  # count
        "Road_Access": np.random.uniform(0.2, 1.0, n_zones),  # 0-1 (higher = better)
        
        # Additional factors
        "Temperature": np.random.uniform(15, 40, n_zones),  # Celsius
        "Wind_Speed": np.random.uniform(5, 100, n_zones)  # km/h
    }

    df = pd.DataFrame(data)
    logger.info(f"Generated synthetic data for {n_zones} zones")
    return df

def generate_timeseries(n_zones: int = 5, n_hours: int = 24) -> pd.DataFrame:
    """
    Generate synthetic time-series data for scenario evolution.
    
    Args:
        n_zones: Number of zones
        n_hours: Number of time steps
        
    Returns:
        DataFrame with time-indexed hazard data
    """
    np.random.seed(42)
    
    data = []
    for zone_id in range(n_zones):
        base_rainfall = np.random.uniform(20, 100)
        for hour in range(n_hours):
            # Simulate rainfall intensity peak
            time_factor = np.sin(hour / n_hours * np.pi)
            rainfall = base_rainfall * time_factor + np.random.normal(0, 10)
            
            data.append({
                "Zone_ID": f"Zone_{zone_id+1:02d}",
                "Hour": hour,
                "Rainfall": max(0, rainfall),
                "River_Level": 3 + time_factor * 2 + np.random.normal(0, 0.5),
                "Soil_Saturation": 0.5 + 0.3 * time_factor + np.random.normal(0, 0.05)
            })
    
    df = pd.DataFrame(data)
    logger.info(f"Generated time-series for {n_zones} zones, {n_hours} hours")
    return df
