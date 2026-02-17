"""Resource demand estimation based on risk and vulnerability indicators"""

import pandas as pd
from utils.logger import setup_logger
import config

logger = setup_logger(__name__)

def estimate_demand(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate resource needs (ambulances, rescue teams, relief kits) based on ADSS and population factors.
    
    Args:
        df: DataFrame with ADSS and population metrics
        
    Returns:
        DataFrame with added demand columns: Estimated_Injuries, Ambulance_Needed, 
        Rescue_Teams_Needed, Relief_Kits_Needed
    """
    df = df.copy()
    
    # Validate required columns
    required = ["ADSS", "Population_Density"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        raise ValueError(f"Missing required columns: {missing}")
    
    # Estimate casualties
    df["Estimated_Injuries"] = (
        df["ADSS"] * df["Population_Density"] * config.INJURY_FACTOR
    ).round(0).astype(int)
    
    # Estimate ambulance needs
    df["Ambulance_Needed"] = (
        df["Estimated_Injuries"] / config.AMBULANCE_DIVISOR
    ).round(0).astype(int)
    
    # Estimate rescue teams needed
    df["Rescue_Teams_Needed"] = (
        df["ADSS"] * config.RESCUE_SCALING
    ).round(0).astype(int)
    
    # Estimate relief kits needed
    df["Relief_Kits_Needed"] = (
        df["Population_Density"] * config.RELIEF_FACTOR
    ).round(0).astype(int)
    
    logger.info(
        f"Demand estimated. Total injuries: {df['Estimated_Injuries'].sum()}, "
        f"Ambulances needed: {df['Ambulance_Needed'].sum()}, "
        f"Rescue teams needed: {df['Rescue_Teams_Needed'].sum()}"
    )
    
    return df
