"""Priority ranking engine for resource deployment optimization"""

import pandas as pd
from utils.logger import setup_logger
import config

logger = setup_logger(__name__)

def compute_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute deployment priority scores incorporating multiple factors:
    - Disaster severity (ADSS)
    - Population exposure
    - Medical infrastructure deficit
    - Accessibility (road access)
    
    Args:
        df: DataFrame with ADSS, population, and infrastructure metrics
        
    Returns:
        DataFrame sorted by Priority_Score (descending) with added columns:
        Medical_Deficit and Priority_Score
    """
    df = df.copy()
    
    # Validate required columns
    required = ["ADSS", "Population_Density", "Hospital_Capacity", "Road_Access"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"Missing columns for priority: {missing}")
        raise ValueError(f"Missing required columns: {missing}")
    
    # Compute medical deficit (how much hospital capacity is overwhelmed)
    max_hospital = df["Hospital_Capacity"].max()
    if max_hospital == 0:
        logger.warning("Hospital capacity is zero, setting medical deficit to 0.5")
        df["Medical_Deficit"] = 0.5
    else:
        df["Medical_Deficit"] = 1 - (df["Hospital_Capacity"] / max_hospital)
    
    # Normalize population density
    max_pop = df["Population_Density"].max()
    pop_normalized = df["Population_Density"] / max_pop if max_pop > 0 else 0
    
    # Compute priority score with configurable weights
    df["Priority_Score"] = (
        config.PRIORITY_ADSS_WEIGHT * df["ADSS"] +
        config.PRIORITY_POPULATION_WEIGHT * pop_normalized +
        config.PRIORITY_MEDICAL_WEIGHT * df["Medical_Deficit"] +
        config.PRIORITY_ACCESSIBILITY_WEIGHT * (1 - df["Road_Access"])
    )
    
    # Normalize priority score to [0, 1]
    max_priority = df["Priority_Score"].max()
    if max_priority > 0:
        df["Priority_Score"] = df["Priority_Score"] / max_priority
    
    # Sort by priority descending
    df = df.sort_values("Priority_Score", ascending=False).reset_index(drop=True)
    
    logger.info(
        f"Priority computed. Top zone: {df.iloc[0]['Zone'] if len(df) > 0 else 'N/A'} "
        f"(score: {df.iloc[0]['Priority_Score']:.3f})"
    )
    
    return df
