# 🚨 AIDRA - Real-Time Flood Intelligence System

A decision-support dashboard for optimizing emergency resource allocation during flood disasters using multi-dimensional hazard and vulnerability analysis.

## 📋 Overview

AIDRA (Adaptive Disaster Resource Allocator) integrates real-time weather data, demographic information, and infrastructure capacity to:

- **Assess Risk**: Computes Adaptive Disaster Severity Score (ADSS) combining hazard, vulnerability, and exposure
- **Estimate Demand**: Projects resource needs (ambulances, rescue teams) based on risk and population
- **Prioritize Response**: Ranks zones by deployment priority considering multiple factors
- **Optimize Allocation**: Distributes limited resources efficiently to minimize overall casualties

Unlike reactive systems, AIDRA provides decision-makers with data-driven guidance for proactive resource positioning.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
# Clone repository
cd AIDRA

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with API key (optional)
echo "WEATHERAPI_KEY=your_api_key_here" > .env
```

### Running the System

```bash
# Start the dashboard
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`

## 🏗️ Architecture

### Core Modules

#### 1. **Risk Engine** (`core/risk_engine.py`)
Computes ADSS using weighted combination:
- **Hazard Score** (50%): Rainfall, river level, soil saturation, forecast
- **Vulnerability Score** (30%): Population density, elderly percentage, poverty vs. drainage and hospital capacity
- **Exposure Score** (20%): Critical facilities vs. road accessibility

Formula: `ADSS = 0.5×Hazard + 0.3×Vulnerability + 0.2×Exposure`

#### 2. **Demand Estimator** (`core/demand_estimator.py`)
Projects resource requirements:
- **Estimated Injuries**: `ADSS × Population_Density × 0.02`
- **Ambulances**: `Injuries ÷ 10`
- **Rescue Teams**: `ADSS × 5`
- **Relief Kits**: `Population_Density × 0.1`

#### 3. **Priority Engine** (`core/priority_engine.py`)
Ranks zones for deployment:
```
Priority = 0.4×ADSS + 0.3×Population + 0.2×Medical_Deficit + 0.1×Accessibility
```

Zones with higher scores receive resources first.

#### 4. **Allocation Engine** (`core/allocation_engine.py`)
Distributes constrained resources optimally:
- **Priority-weighted allocation**: Resources distributed proportional to priority scores
- **Deficit filling**: Remaining resources go to highest-deficit zones
- **Deficit tracking**: Records unmet demand for each zone

#### 5. **Data Pipeline** (`data/weather_api.py`)
- Fetches real-time weather from WeatherAPI
- Integrates with demographic/infrastructure data
- Falls back to synthetic data if API unavailable
- Includes retry logic and error handling

## 📊 Metrics & Outputs

### Key Performance Indicators

| Metric | Definition |
|--------|-----------|
| **ADSS** | Disaster severity (0-1, higher = worse) |
| **Priority Score** | Deployment priority ranking (0-1, higher = more urgent) |
| **Coverage %** | Percent of demand met for ambulances/rescue teams |
| **Deficit** | Unmet resource demand after allocation |

### Output Dataframe Columns

| Column | Description |
|--------|-------------|
| Zone | Geographic zone identifier |
| ADSS | Disaster severity score |
| Estimated_Injuries | Projected casualties |
| Ambulance_Needed | Required ambulances |
| Allocated_Ambulances | Ambulances assigned |
| Ambulance_Deficit | Unmet ambulance need |
| Rescue_Teams_Needed | Required rescue teams |
| Allocated_Rescue_Teams | Rescue teams assigned |
| Rescue_Deficit | Unmet rescue team need |
| Priority_Score | Deployment priority ranking |

## ⚙️ Configuration

Edit `config.py` to adjust system parameters:

```python
# Weight configuration
HAZARD_WEIGHT = 0.5              # Hazard importance
VULNERABILITY_WEIGHT = 0.3       # Vulnerability importance
EXPOSURE_WEIGHT = 0.2            # Exposure importance

# Resource calculations
INJURY_FACTOR = 0.02             # Injuries per unit ADSS×Population
AMBULANCE_DIVISOR = 10           # Injuries per ambulance
RESCUE_SCALING = 5               # Rescue teams per unit ADSS
RELIEF_FACTOR = 0.1              # Relief kits per capita

# API settings
API_TIMEOUT = 10                 # Request timeout seconds
API_RETRY_COUNT = 2              # Retry attempts if API fails
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_pipeline.py
```

Tests verify:
- Data normalization correctness
- ADSS computation validity
- Demand estimation accuracy
- Priority ranking logic
- Resource allocation optimization
- Full end-to-end pipeline

## 📈 Scenario Planning

Use `simulation/escalation_simulator.py` for "what-if" analysis:

```python
from simulation.escalation_simulator import simulate_escalation
from data.synthetic_generator import generate_zones

# Generate scenario
df = generate_zones(10)

# Simulate 24-hour escalation
history = simulate_escalation(df, hours=24, escalation_factor=1.05)

# Analyze resource adequacy over time
for h in history:
    stats = evaluate_resource_adequacy(h, total_ambulances=30, total_rescue=15)
    print(f"Hour {h.iloc[0]['Hour']}: Ambulance coverage {stats['ambulance_coverage']:.1f}%")
```

## 🔍 Logging

The system logs all operations for debugging and audit trails:

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("System initialized")
```

Log level controlled via `config.LOG_LEVEL` ("INFO", "DEBUG", "WARNING", "ERROR")

## 📁 File Structure

```
AIDRA/
├── app.py                        # Streamlit dashboard
├── config.py                     # Configuration parameters
├── requirements.txt              # Python dependencies
├── test_pipeline.py              # Unit tests
├── core/
│   ├── risk_engine.py           # ADSS computation
│   ├── demand_estimator.py      # Resource need projection
│   ├── priority_engine.py       # Zone prioritization
│   └── allocation_engine.py     # Resource optimization
├── data/
│   ├── weather_api.py           # Weather data fetching
│   └── synthetic_generator.py   # Test data generation
├── simulation/
│   └── escalation_simulator.py  # Scenario planning
└── utils/
    ├── normalization.py         # Min-max scaling
    └── logger.py               # Logging setup
```

## 🐛 Troubleshooting

### "WeatherAPI key not found"
- Create `.env` file in project root
- Add: `WEATHERAPI_KEY=your_key_from_weatherapi.com`
- Get free API key at https://www.weatherapi.com

### Dashboard won't start
- Verify all packages installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+)
- Try fresh environment: `pip install -r requirements.txt --upgrade`

### Synthetic data shows all zeros
- Normalization of constant values returns 0
- This is expected behavior - verify input data varies

## 📝 Output Interpretation

**High ADSS Zone (0.8+)**: Severe hazard, many vulnerable people, poor infrastructure
- **Action**: Deploy maximum resources, establish emergency shelters
- **Timeline**: Immediate deployment (< 1 hour)

**Medium ADSS Zone (0.5-0.8)**: Moderate hazard or significant vulnerabilities
- **Action**: Deploy proportional to priority ranking
- **Timeline**: Position within 2-4 hours

**Low ADSS Zone (<0.5)**: Minor hazard or well-prepared area
- **Action**: Standby or relief operations only
- **Timeline**: 4+ hours

## 🔐 Data Privacy

The system processes sensitive demographic data:
- Store only aggregated zone-level data
- Do not log individual names/addresses
- Follow GDPR/local data protection regulations
- Regular security audits recommended

## 📚 References

- WeatherAPI: https://www.weatherapi.com/docs/
- Disaster risk reduction frameworks: SENDAI Framework
- Resource allocation optimization: Operations Research

## 📧 Support

For issues or questions:
1. Check logs: Enable `LOG_LEVEL = "DEBUG"` in config.py
2. Run tests: `python test_pipeline.py`
3. Verify data: Check intermediate DataFrames in dashboard

## 📄 License

This project is provided as-is for disaster management research and operations.

---

**Last Updated**: February 2026
**Version**: 2.0 (Production-Ready)
