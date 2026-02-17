# 🚀 QUICK START GUIDE

## Installation (2 Minutes)

### Option 1: Windows Users (Easiest)
```bash
# Just double-click this file:
startup.bat

# That's it! Dashboard opens automatically
```

### Option 2: Manual Setup
```bash
# Navigate to project
cd f:\AIDRA

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Running the System

### Start the Dashboard
```bash
streamlit run app.py
```

Expected output:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Open http://localhost:8501 in your browser

### Run Tests
```bash
python test_pipeline.py
```

Expected output:
```
==================================================
✓ All tests passed!
==================================================
```

### Validate System
```bash
python validate_system.py
```

Expected output:
```
✓ ALL VALIDATIONS PASSED - SYSTEM READY FOR PRODUCTION
```

---

## Using the Dashboard

### What You'll See

1. **Top Metrics** (4 cards)
   - 🚨 Total Danger Score
   - 👥 Estimated Injuries  
   - 🚑 Ambulance Deficit
   - 🆘 Rescue Deficit

2. **Risk Assessment Charts** (2 visualizations)
   - Disaster Severity by Zone (Red bar chart)
   - Deployment Priority by Zone (Orange bar chart)

3. **Resource Allocation Table**
   - Zone names
   - Priority scores
   - Ambulances needed vs allocated
   - Rescue teams needed vs allocated
   - Deficits (unmet demand)

4. **Coverage Comparison** (2 charts)
   - Ambulance allocation vs need
   - Rescue team allocation vs need

5. **System Controls** (Sidebar)
   - 🔄 Refresh button (get latest data)
   - 🚑 Ambulance slider (5-100)
   - 🆘 Rescue team slider (5-50)
   - 📊 Data mode toggle (Live API vs Synthetic)

---

## Understanding the Output

### ADSS (Disaster Severity Score)
```
0.0-0.3: Green  → Low risk, normal operations
0.3-0.6: Yellow → Moderate risk, increased readiness
0.6-0.8: Orange → High risk, emergency protocols active
0.8-1.0: Red    → Critical, full mobilization
```

### Priority Score
Higher = More urgent. Zones at top get resources first.

### Coverage %
```
80-100%: ✅ Adequate
50-80%:  ⚠️  Gaps exist
<50%:    🚨 Insufficient
```

### Deficit
Number of unmet resource needs after optimal allocation.

---

## How the System Works

### 1️⃣ Data Collection
- Fetches weather from WeatherAPI (optional)
- Falls back to synthetic if API unavailable
- Combines with demographic data

### 2️⃣ Risk Assessment
- Combines: Hazard (rainfall, flooding) + Vulnerability (population, poverty) + Exposure (facilities, roads)
- Outputs: ADSS score (0-1)

### 3️⃣ Demand Estimation
- ADSS × Population → Estimated injuries
- Injuries ÷ 10 → Ambulances needed
- ADSS × 5 → Rescue teams needed
- Population × 0.1 → Relief kits needed

### 4️⃣ Priority Ranking
- Factors: Disaster severity, population, medical infrastructure gap, road access
- Outputs: Priority score ranking each zone

### 5️⃣ Resource Allocation
- Distributes limited ambulances & rescue teams by priority
- Ensures no over-allocation
- Tracks deficits for each zone

---

## Configuration

### Basic Settings (config.py)

**Weights (should sum to 1.0):**
```python
HAZARD_WEIGHT = 0.5           # How much weather matters
VULNERABILITY_WEIGHT = 0.3    # How much population matters
EXPOSURE_WEIGHT = 0.2         # How much infrastructure matters
```

**Resource Calculations:**
```python
INJURY_FACTOR = 0.02          # Injuries per unit severity
AMBULANCE_DIVISOR = 10        # Injuries per ambulance
RESCUE_SCALING = 5            # Rescue teams per severity unit
RELIEF_FACTOR = 0.1           # Relief kits per capita
```

**System:**
```python
LOG_LEVEL = "INFO"            # "DEBUG" for detailed logs
API_TIMEOUT = 10              # Seconds to wait for weather data
API_RETRY_COUNT = 2           # Times to retry if connection fails
```

---

## Getting More Data

### WeatherAPI Setup (Optional)

1. Get free API key: https://www.weatherapi.com
2. Create `.env` file:
   ```
   WEATHERAPI_KEY=your_key_here
   ```
3. Restart app - now uses real weather data

### Without API Key
System automatically uses realistic synthetic data - perfectly fine for training/demos.

---

## Troubleshooting

### "Module not found" error
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Dashboard won't open
```bash
# Check Python version (need 3.8+)
python --version

# Try different port
streamlit run app.py --server.port 8502
```

### Data looks wrong
```bash
# Check logs for details
# First, enable debug logging in config.py:
LOG_LEVEL = "DEBUG"

# Then run again to see detailed output
streamlit run app.py
```

### API not working
```bash
# Toggle "Use Synthetic Data" in sidebar
# System will use demo data instead
```

---

## Typical Workflow

```
1. Start dashboard
   streamlit run app.py
   
2. View initial analysis
   - Check ADSS scores
   - Review priority rankings
   
3. Adjust resources
   - Move ambulance slider
   - Move rescue team slider
   - Watch coverage % change
   
4. Check allocation
   - Review table
   - Note deficits
   
5. Refresh data
   - Click "🔄 Refresh Data" button
   - Analyze updated conditions
   
6. Export results (copy table manually if needed)
```

---

## Performance

| Operation | Time |
|-----------|------|
| App startup | 3-5 seconds |
| Data fetch (API) | 2-5 seconds |
| Data fetch (synthetic) | <1 second |
| Analysis pipeline | <500ms |
| Dashboard render | <1 second |
| Total end-to-end | <10 seconds |

---

## Testing the System

### Quick Validation
```bash
python validate_system.py
```

### Comprehensive Tests
```bash
python test_pipeline.py
```

### Manual Testing
```bash
# Test API with synthetic data
streamlit run app.py

# Change slider values - watch updates
# Click refresh button - watch recalculation
# Toggle synthetic mode - verify fallback
```

---

## What's Inside Each File

| File | Purpose |
|------|---------|
| `app.py` | Streamlit dashboard |
| `config.py` | System configuration |
| `core/risk_engine.py` | Hazard assessment |
| `core/demand_estimator.py` | Resource forecasting |
| `core/priority_engine.py` | Zone prioritization |
| `core/allocation_engine.py` | Resource optimization |
| `data/weather_api.py` | Data collection |
| `data/synthetic_generator.py` | Demo data |
| `simulation/escalation_simulator.py` | Scenario planning |
| `utils/logger.py` | Logging system |
| `utils/normalization.py` | Data scaling |

---

## Key Concepts

### ADSS (Adaptive Disaster Severity Score)
Combines multiple factors into single 0-1 score:
- High rainfall → Higher ADSS
- Large population → Higher ADSS  
- Poor drainage → Higher ADSS
- Good hospitals → Lower ADSS

### Priority Score
Multifactor ranking considering:
- Which zones have worst disasters
- Which zones have most people
- Which zones have worst medical capacity
- Which zones are hardest to access

### Optimal Allocation
Distributes LIMITED resources to MAXIMIZE impact:
- Not first-come, first-served
- Not equal distribution
- But priority-weighted based on need & urgency

### Deficit Tracking
Shows what couldn't be met:
- Helps identify resource gaps
- Guides requests for help
- Shows where system is constrained

---

## Support

### Getting Help
1. Check documentation: `README.md`
2. See improvements: `IMPROVEMENTS.md`
3. Review examples: `test_pipeline.py`
4. Enable debug logs: Set `LOG_LEVEL = "DEBUG"`

### Reporting Issues
Note:
- What you did
- What you expected
- What happened instead
- Any error messages
- Enable `LOG_LEVEL = "DEBUG"` and share logs

---

## Next Steps

✅ **You're Ready!**

1. Try the system: `streamlit run app.py`
2. Adjust resources: Use sidebar sliders
3. Review allocation: Check the table
4. Plan scenarios: Toggle synthetic data
5. Validate quality: Run tests

For advanced features, see:
- `IMPROVEMENTS.md` - Configuration examples
- `README.md` - Complete documentation
- `CHANGELOG.md` - All improvements made

---

## Version Info

- **Current Version:** 2.0 (Production Ready)
- **Last Updated:** February 17, 2026
- **Status:** ✅ All tests passing
- **Production Ready:** YES

---

**Happy Analyzing! 🚀**

Questions? Check README.md or review the code comments.
