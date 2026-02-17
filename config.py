"""Configuration settings for AIDRA system"""

# Weight configuration for ADSS calculation
HAZARD_WEIGHT = 0.5
VULNERABILITY_WEIGHT = 0.3
EXPOSURE_WEIGHT = 0.2

# Validate weights sum to 1
assert abs((HAZARD_WEIGHT + VULNERABILITY_WEIGHT + EXPOSURE_WEIGHT) - 1.0) < 0.01, \
    "Weights must sum to 1.0"

# Resource multipliers
INJURY_FACTOR = 0.02
AMBULANCE_DIVISOR = 10
RESCUE_SCALING = 5
RELIEF_FACTOR = 0.1

# Priority weights
PRIORITY_ADSS_WEIGHT = 0.4
PRIORITY_POPULATION_WEIGHT = 0.3
PRIORITY_MEDICAL_WEIGHT = 0.2
PRIORITY_ACCESSIBILITY_WEIGHT = 0.1

# Logging and validation
LOG_LEVEL = "INFO"
MIN_DATA_POINTS = 3  # Minimum zones for analysis
API_TIMEOUT = 10  # seconds
API_RETRY_COUNT = 2
