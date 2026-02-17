"""Data normalization utilities"""

from typing import List
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)

def min_max_normalize(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Min-max normalize specified columns to [0, 1] range.
    Handles edge cases where all values are identical.
    
    Args:
        df: Input dataframe
        columns: List of column names to normalize
        
    Returns:
        DataFrame with normalized columns
        
    Raises:
        ValueError: If column doesn't exist
    """
    df = df.copy()
    
    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found, skipping normalization")
            continue
            
        try:
            col_min = df[col].min()
            col_max = df[col].max()
            col_range = col_max - col_min
            
            if col_range == 0:
                logger.warning(f"Column '{col}' has constant values, setting to 0")
                df[col] = 0
            else:
                df[col] = (df[col] - col_min) / col_range
                # Ensure values are in [0, 1] range (handles floating point errors)
                df[col] = df[col].clip(0, 1)
        except Exception as e:
            logger.error(f"Error normalizing column '{col}': {e}")
            df[col] = 0
    
    return df
