"""Disaster escalation simulation for scenario planning"""

from typing import List, Dict
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)

def simulate_escalation(df: pd.DataFrame, hours: int = 24, 
                       escalation_factor: float = 1.05) -> List[pd.DataFrame]:
    """
    Simulate how disaster conditions escalate over time.
    Useful for understanding resource needs under different scenarios.
    
    Args:
        df: Initial conditions dataframe
        hours: Hours to simulate
        escalation_factor: Hourly increase in severity (1.05 = 5% per hour)
        
    Returns:
        List of DataFrames showing state at each hour
    """
    history = []
    df_current = df.copy()
    
    logger.info(f"Simulating escalation for {hours} hours with factor {escalation_factor}")
    
    for hour in range(hours + 1):
        # Scale hazard factors
        df_current = df_current.copy()
        if hour > 0:
            scale = escalation_factor ** hour
            df_current["Rainfall"] = df["Rainfall"] * scale
            df_current["Forecast_Rainfall"] = df["Forecast_Rainfall"] * min(scale, 1.5)
            df_current["River_Level"] = df["River_Level"] * min(scale, 2.0)
        
        df_current["Hour"] = hour
        history.append(df_current.copy())
    
    logger.info(f"Simulation complete: {len(history)} time steps generated")
    return history

def compute_scenario_statistics(history: List[pd.DataFrame]) -> Dict:
    """
    Compute aggregate statistics across simulation timeline.
    
    Args:
        history: List of DataFrames from simulation
        
    Returns:
        Dictionary with statistics
    """
    if not history:
        return {}
    
    max_rainfall = max([h["Rainfall"].max() for h in history])
    avg_rainfall = np.mean([h["Rainfall"].mean() for h in history])
    peak_hour = max(range(len(history)), 
                   key=lambda i: history[i]["Rainfall"].sum())
    
    stats = {
        "max_rainfall": max_rainfall,
        "avg_rainfall": avg_rainfall,
        "total_hours": len(history),
        "peak_hour": peak_hour,
        "zones": len(history[0]) if history else 0
    }
    
    logger.info(f"Scenario stats: Max rainfall {max_rainfall:.1f}mm at hour {peak_hour}")
    return stats

def evaluate_resource_adequacy(df: pd.DataFrame, total_ambulances: int, 
                              total_rescue: int) -> Dict:
    """
    Evaluate if resources are adequate for current conditions.
    
    Args:
        df: Current conditions with demand estimates
        total_ambulances: Available ambulances
        total_rescue: Available rescue teams
        
    Returns:
        Dictionary with adequacy metrics
    """
    ambulance_need = df["Ambulance_Needed"].sum() if "Ambulance_Needed" in df.columns else 0
    rescue_need = df["Rescue_Teams_Needed"].sum() if "Rescue_Teams_Needed" in df.columns else 0
    
    results = {
        "ambulances_adequate": total_ambulances >= ambulance_need,
        "rescue_adequate": total_rescue >= rescue_need,
        "ambulance_coverage": (total_ambulances / ambulance_need * 100) if ambulance_need > 0 else 100,
        "rescue_coverage": (total_rescue / rescue_need * 100) if rescue_need > 0 else 100,
        "ambulance_surplus": total_ambulances - ambulance_need,
        "rescue_surplus": total_rescue - rescue_need
    }
    
    logger.info(
        f"Adequacy check: Ambulances {results['ambulance_coverage']:.1f}%, "
        f"Rescue {results['rescue_coverage']:.1f}%"
    )
    
    return results
