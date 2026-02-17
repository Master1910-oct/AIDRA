"""Resource allocation optimization engine"""

import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)

def allocate_resources(df: pd.DataFrame, total_ambulances: int, total_rescue: int) -> pd.DataFrame:
    """
    Allocate limited ambulances and rescue teams optimally based on priority scores.
    Uses a priority-weighted allocation that respects both need and criticality.
    
    Args:
        df: DataFrame with demand and priority columns (must be sorted by priority)
        total_ambulances: Total ambulances available
        total_rescue: Total rescue teams available
        
    Returns:
        DataFrame with added allocation columns:
        Allocated_Ambulances, Allocated_Rescue_Teams, Ambulance_Deficit, Rescue_Deficit
    """
    df = df.copy()
    
    # Validate required columns
    required = ["Priority_Score", "Ambulance_Needed", "Rescue_Teams_Needed"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"Missing columns for allocation: {missing}")
        raise ValueError(f"Missing required columns: {missing}")
    
    # Initialize allocation columns
    df["Allocated_Ambulances"] = 0
    df["Allocated_Rescue_Teams"] = 0
    
    # Allocate ambulances using priority-weighted approach
    remaining_ambulances = total_ambulances
    if remaining_ambulances > 0:
        remaining_ambulances = _allocate_by_priority(
            df, "Ambulance_Needed", "Allocated_Ambulances", remaining_ambulances
        )
    
    # Allocate rescue teams using priority-weighted approach
    remaining_rescue = total_rescue
    if remaining_rescue > 0:
        remaining_rescue = _allocate_by_priority(
            df, "Rescue_Teams_Needed", "Allocated_Rescue_Teams", remaining_rescue
        )
    
    # Calculate deficits
    df["Ambulance_Deficit"] = (df["Ambulance_Needed"] - df["Allocated_Ambulances"]).clip(lower=0)
    df["Rescue_Deficit"] = (df["Rescue_Teams_Needed"] - df["Allocated_Rescue_Teams"]).clip(lower=0)
    
    # Log summary statistics
    total_ambulance_need = df["Ambulance_Needed"].sum()
    total_ambulance_allocated = df["Allocated_Ambulances"].sum()
    total_ambulance_deficit = df["Ambulance_Deficit"].sum()
    
    total_rescue_need = df["Rescue_Teams_Needed"].sum()
    total_rescue_allocated = df["Allocated_Rescue_Teams"].sum()
    total_rescue_deficit = df["Rescue_Deficit"].sum()
    
    ambulance_coverage = (total_ambulance_allocated / total_ambulance_need * 100) if total_ambulance_need > 0 else 0
    rescue_coverage = (total_rescue_allocated / total_rescue_need * 100) if total_rescue_need > 0 else 0
    
    logger.info(
        f"Resource allocation complete:\n"
        f"  Ambulances: {total_ambulance_allocated}/{total_ambulance_need} "
        f"({ambulance_coverage:.1f}% coverage), Deficit: {total_ambulance_deficit}\n"
        f"  Rescue Teams: {total_rescue_allocated}/{total_rescue_need} "
        f"({rescue_coverage:.1f}% coverage), Deficit: {total_rescue_deficit}"
    )
    
    return df

def _allocate_by_priority(
    df: pd.DataFrame, 
    need_col: str, 
    allocation_col: str, 
    total_available: int
) -> int:
    """
    Allocate resources based on priority score using a weighted distribution.
    Higher priority zones get more resources, but every zone gets at least some.
    
    Args:
        df: DataFrame with Priority_Score and need columns
        need_col: Column name for resource needs
        allocation_col: Column name for allocation results
        total_available: Total resources to allocate
        
    Returns:
        Remaining unallocated resources
    """
    remaining = total_available
    priority_sum = df["Priority_Score"].sum()
    
    # First pass: allocate by priority proportion
    if priority_sum > 0:
        for i in df.index:
            priority_share = df.loc[i, "Priority_Score"] / priority_sum
            allocated = min(
                int(remaining * priority_share),
                df.loc[i, need_col],
                remaining
            )
            df.loc[i, allocation_col] = allocated
            remaining -= allocated
    
    # Second pass: allocate remaining resources to zones with highest deficits
    if remaining > 0:
        df["Deficit"] = df[need_col] - df[allocation_col]
        high_deficit_zones = df[df["Deficit"] > 0].sort_values("Deficit", ascending=False).index
        
        for i in high_deficit_zones:
            if remaining <= 0:
                break
            deficit = df.loc[i, "Deficit"]
            additional = min(int(deficit), remaining)
            df.loc[i, allocation_col] += additional
            remaining -= additional
        
        df.drop("Deficit", axis=1, inplace=True)
    
    return remaining
