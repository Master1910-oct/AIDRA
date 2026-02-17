"""Risk assessment engine for computing ADSS (Adaptive Disaster Severity Score)"""

from typing import List
import pandas as pd
from utils.normalization import min_max_normalize
from utils.logger import setup_logger
import config

logger = setup_logger(__name__)

def compute_adss(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Adaptive Disaster Severity Score based on hazard, vulnerability, and exposure.
    
    The ADSS combines:
    - Hazard Score (rainfall, river level, soil saturation, forecast)
    - Vulnerability Score (population density, elderly %, poverty index, vs drainage & hospital capacity)
    - Exposure Score (critical facilities vs road access)
    
    Args:
        df: Input dataframe with hazard, vulnerability, and exposure columns
        
    Returns:
        DataFrame with added ADSS column (0-1 scale)
    """
    df = df.copy()
    
    # Define component columns
    hazard_cols = ["Rainfall", "River_Level", "Soil_Saturation", "Forecast_Rainfall"]
    vulnerability_cols = ["Population_Density", "Elderly_Percentage", "Poverty_Index"]
    inverse_vulnerability_cols = ["Drainage_Score", "Hospital_Capacity"]
    exposure_cols = ["Critical_Facilities"]
    inverse_exposure_cols = ["Road_Access"]
    
    all_norm_cols = (
        hazard_cols + vulnerability_cols +
        inverse_vulnerability_cols + exposure_cols + inverse_exposure_cols
    )
    
    # Validate required columns
    missing_cols = [col for col in all_norm_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing columns for ADSS: {missing_cols}")
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Normalize all columns to [0, 1]
    df_norm = min_max_normalize(df, all_norm_cols)
    
    # Compute hazard score (higher is worse)
    hazard_score = df_norm[hazard_cols].mean(axis=1)
    logger.debug(f"Hazard score range: {hazard_score.min():.3f} - {hazard_score.max():.3f}")
    
    # Compute vulnerability score
    # Low drainage and low hospital capacity increase vulnerability
    vulnerability_score = (
        df_norm[vulnerability_cols].mean(axis=1) +
        (1 - df_norm[inverse_vulnerability_cols].mean(axis=1))
    ) / 2
    logger.debug(f"Vulnerability score range: {vulnerability_score.min():.3f} - {vulnerability_score.max():.3f}")
    
    # Compute exposure score
    # Low road access increases exposure risk
    exposure_score = (
        df_norm[exposure_cols].mean(axis=1) +
        (1 - df_norm[inverse_exposure_cols].mean(axis=1))
    ) / 2
    logger.debug(f"Exposure score range: {exposure_score.min():.3f} - {exposure_score.max():.3f}")
    
    # Weighted combination
    df["ADSS"] = (
        config.HAZARD_WEIGHT * hazard_score +
        config.VULNERABILITY_WEIGHT * vulnerability_score +
        config.EXPOSURE_WEIGHT * exposure_score
    )
    
    # Ensure ADSS is in valid range
    df["ADSS"] = df["ADSS"].clip(0, 1)
    
    logger.info(f"ADSS computed. Range: {df['ADSS'].min():.3f} - {df['ADSS'].max():.3f}")
    return df
