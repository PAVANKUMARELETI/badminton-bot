# Software Requirements Specification (SRS)
## Badminton Wind Predictor System

**Version:** 1.0  
**Date:** November 15, 2025  
**Project:** Badminton Wind Forecasting & Decision Support System  
**Repository:** PAVANKUMARELETI/badminton-bot

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [System Requirements](#5-system-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Data Requirements](#7-data-requirements)
8. [Appendices](#8-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for the Badminton Wind Predictor system. The system is designed to help badminton players make informed decisions about outdoor play by forecasting wind conditions and providing BWF-compliant safety recommendations.

### 1.2 Scope
The Badminton Wind Predictor is a production-ready machine learning system that:
- Predicts wind speed for 1h, 3h, and 6h horizons using LSTM neural networks
- Provides real-time wind condition assessment via Telegram bot interface
- Complies with Badminton World Federation (BWF) wind safety standards
- Automatically collects and logs weather data for model improvement
- Deploys on cloud infrastructure with CI/CD automation

**In Scope:**
- Real-time weather data retrieval via OpenWeatherMap API
- LSTM-based wind speed forecasting
- Telegram bot interface for user interaction
- Automated data collection and storage
- BWF-compliant decision logic
- Cloud deployment on Railway.app
- Continuous Integration/Continuous Deployment (CI/CD)

**Out of Scope:**
- Mobile native applications (iOS/Android)
- Indoor court recommendations
- Weather data for sports other than badminton
- Paid subscription features
- Multi-language support (English only)

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| BWF | Badminton World Federation - International governing body for badminton |
| LSTM | Long Short-Term Memory - Type of recurrent neural network |
| API | Application Programming Interface |
| CI/CD | Continuous Integration/Continuous Deployment |
| m/s | Meters per second (wind speed unit) |
| km/h | Kilometers per hour (wind speed unit) |
| Q90 | 90th percentile (statistical measure for wind gusts) |
| ML | Machine Learning |
| SRS | Software Requirements Specification |

### 1.4 References
- BWF AirBadminton Official Guidelines: https://airbadminton.bwf.sport/
- OpenWeatherMap API Documentation: https://openweathermap.org/api
- Python Telegram Bot Documentation: https://python-telegram-bot.org/
- TensorFlow/Keras Documentation: https://www.tensorflow.org/

### 1.5 Overview
The remainder of this document provides:
- Overall system description and context
- Detailed functional requirements for each system component
- Interface specifications for external systems
- Performance, security, and reliability requirements
- Data management and storage specifications

---

## 2. Overall Description

### 2.1 Product Perspective
The Badminton Wind Predictor is a standalone cloud-based system with the following major components:

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Telegram   │  │   WhatsApp   │  │   Web UI     │  │
│  │     Bot      │  │     Bot      │  │  (Future)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Application Logic Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Decision    │  │  Weather     │  │  Forecast    │  │
│  │   Engine     │  │  Fetcher     │  │   Engine     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Data Processing Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Feature    │  │    LSTM      │  │    Data      │  │
│  │ Engineering  │  │    Model     │  │   Logger     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   External Services                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ OpenWeather  │  │   Telegram   │  │    Sentry    │  │
│  │     API      │  │     API      │  │  (Monitoring)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Product Functions
The system performs the following primary functions:

1. **Real-Time Weather Assessment**
   - Fetches current weather data from OpenWeatherMap API
   - Evaluates wind conditions against BWF safety standards
   - Provides immediate play/don't play recommendations

2. **Wind Speed Forecasting**
   - Predicts wind speed for 1h, 3h, and 6h ahead
   - Uses LSTM neural network trained on historical data
   - Generates probabilistic forecasts (median and 90th percentile)

3. **User Interaction**
   - Telegram bot interface with command-based interaction
   - Interactive buttons for quick actions
   - Location-based weather queries

4. **Data Collection**
   - Automatic hourly weather logging
   - CSV-based storage for model retraining
   - 30-day data collection cycles

5. **Decision Support**
   - BWF-compliant threshold evaluation
   - Clear explanations of decisions
   - Safety margin recommendations

### 2.3 User Classes and Characteristics

#### 2.3.1 Primary Users: Badminton Players
- **Expertise:** Non-technical, recreational to competitive players
- **Usage Frequency:** 1-5 times per week
- **Primary Goal:** Quick decision on whether to play outdoors
- **Technical Skills:** Basic smartphone/Telegram usage

#### 2.3.2 Secondary Users: System Administrators
- **Expertise:** Technical, software development background
- **Usage Frequency:** Weekly monitoring, monthly updates
- **Primary Goal:** System maintenance and optimization
- **Technical Skills:** Python, ML, DevOps

#### 2.3.3 Tertiary Users: Data Scientists
- **Expertise:** ML/AI specialists
- **Usage Frequency:** Occasional, for model improvements
- **Primary Goal:** Enhance forecasting accuracy
- **Technical Skills:** Advanced ML, data analysis

### 2.4 Operating Environment

**Production Environment:**
- **Platform:** Railway.app cloud hosting
- **Operating System:** Ubuntu Linux (containerized)
- **Python Version:** 3.10
- **Database:** CSV files (filesystem-based)
- **External APIs:** OpenWeatherMap, Telegram Bot API

**Development Environment:**
- **OS:** Windows 10/11, macOS, Linux
- **IDE:** VS Code, PyCharm
- **Version Control:** Git/GitHub
- **CI/CD:** GitHub Actions

### 2.5 Design and Implementation Constraints

1. **BWF Compliance:** Must adhere to official BWF wind speed recommendations
   - Maximum wind speed: 3.33 m/s (12 km/h)
   - Maximum gusts: 5.0 m/s (18 km/h)

2. **Cost Constraints:** Monthly operational cost must stay under $5 USD
   - Limited to Railway.app free tier resources
   - Optimized for minimal RAM/CPU usage

3. **API Rate Limits:**
   - OpenWeatherMap: 60 calls/minute, 1,000,000 calls/month (free tier)
   - Telegram Bot API: No specific limit, but rate-limited by design

4. **Technology Stack:**
   - Must use TensorFlow 2.16+ for model compatibility
   - Python 3.10 for Railway deployment compatibility
   - No database server (file-based storage only)

5. **Deployment:**
   - Must support auto-deployment from GitHub
   - Single-instance deployment (no load balancing)
   - No HTTP endpoints (polling-based bot only)

### 2.6 Assumptions and Dependencies

**Assumptions:**
- Users have active internet connection
- Users have Telegram installed and account created
- Weather API services remain available and reliable
- BWF standards remain unchanged

**Dependencies:**
- OpenWeatherMap API availability and accuracy
- Telegram Bot API uptime
- Railway.app platform stability
- Python package ecosystem (TensorFlow, pandas, etc.)

---

## 3. System Features

### 3.1 Real-Time Weather Checking (NOW Mode)

**Priority:** High  
**Risk:** Low

#### 3.1.1 Description
Users can query current wind conditions for their location and receive immediate play/don't play recommendations.

#### 3.1.2 Functional Requirements

**FR-NOW-001:** System shall fetch current weather data from OpenWeatherMap API when user sends `/now` command.

**FR-NOW-002:** System shall display the following information:
- Current timestamp (IST timezone)
- Location name and coordinates
- Wind speed in m/s and km/h
- Wind gust speed in m/s and km/h
- Temperature in Celsius
- Humidity percentage
- Atmospheric pressure in hPa

**FR-NOW-003:** System shall evaluate wind conditions using BWF thresholds:
- PLAY if: wind ≤ 3.33 m/s AND gusts ≤ 5.0 m/s
- DON'T PLAY if: wind > 3.33 m/s OR gusts > 5.0 m/s

**FR-NOW-004:** System shall display visual indicators:
- ✅ checkmark for PLAY decision
- ❌ cross mark for DON'T PLAY decision
- Color-coded message formatting

**FR-NOW-005:** System shall provide BWF threshold reference:
- "Safe thresholds: Wind < 3.33 m/s | Gusts < 5.0 m/s"

**FR-NOW-006:** System shall include interactive buttons:
- 🔄 Refresh (re-fetch current weather)
- 📊 See Forecast (switch to forecast mode)
- 🏠 Main Menu (return to start)

#### 3.1.3 Performance Requirements
- API response time: < 2 seconds
- Bot response time: < 5 seconds total
- Weather data freshness: ≤ 10 minutes old

### 3.2 Wind Forecasting (FORECAST Mode)

**Priority:** High  
**Risk:** Medium

#### 3.2.1 Description
Users can request ML-powered wind forecasts for 1h, 3h, and 6h ahead using LSTM model predictions.

#### 3.2.2 Functional Requirements

**FR-FORECAST-001:** System shall accept `/forecast` command from users.

**FR-FORECAST-002:** System shall fetch hourly forecast data for next 6 hours from OpenWeatherMap API.

**FR-FORECAST-003:** System shall preprocess forecast data:
- Extract wind speed, temperature, pressure, humidity
- Build feature matrix with rolling statistics
- Normalize features using saved scaler parameters

**FR-FORECAST-004:** System shall load pre-trained LSTM model from disk.

**FR-FORECAST-005:** System shall generate predictions for three horizons:
- 1 hour ahead
- 3 hours ahead
- 6 hours ahead

**FR-FORECAST-006:** System shall compute probabilistic forecasts:
- Median forecast (50th percentile)
- 90th percentile forecast (for gust estimation)

**FR-FORECAST-007:** System shall make play decision based on:
- PLAY if: median ≤ 3.33 m/s AND Q90 ≤ 5.0 m/s (for all horizons)
- DON'T PLAY if: median > 3.33 m/s OR Q90 > 5.0 m/s (for any horizon)

**FR-FORECAST-008:** System shall display forecast table with:
- Horizon (1h, 3h, 6h)
- Median wind speed
- Q90 wind speed (gust estimate)
- Visual indicators for each horizon

**FR-FORECAST-009:** System shall provide "Next good time" suggestion if current conditions are unsafe.

#### 3.2.3 Performance Requirements
- Model loading time: < 3 seconds
- Inference time: < 1 second
- Total response time: < 8 seconds

### 3.3 Location Management

**Priority:** Medium  
**Risk:** Low

#### 3.3.1 Description
Users can set their preferred location for weather queries.

#### 3.3.2 Functional Requirements

**FR-LOC-001:** System shall use default location: IIIT Lucknow (26.7984°N, 81.0241°E).

**FR-LOC-002:** System shall accept `/location <city_name>` command to change location.

**FR-LOC-003:** System shall parse location using OpenWeatherMap Geocoding API:
- Convert city name to coordinates
- Return city name, coordinates, country code

**FR-LOC-004:** System shall display current location in `/start` message.

**FR-LOC-005:** System shall persist location preference per user session.

**FR-LOC-006:** System shall display location in format: "City Name (XX.XXXX°N, YY.YYYY°E)"

**FR-LOC-007:** System shall handle location parsing errors:
- Display "Unknown Location" if city not found
- Suggest checking spelling
- Maintain previous valid location

### 3.4 Automatic Data Collection

**Priority:** High  
**Risk:** Low

#### 3.4.1 Description
System automatically logs weather data every hour for model retraining purposes.

#### 3.4.2 Functional Requirements

**FR-DATA-001:** System shall schedule background job to run every 3600 seconds (1 hour).

**FR-DATA-002:** System shall fetch current weather data during each scheduled run.

**FR-DATA-003:** System shall store data in CSV format with fields:
- timestamp (ISO 8601 format)
- location (string)
- latitude (float, 4 decimals)
- longitude (float, 4 decimals)
- temperature_c (float)
- humidity_percent (int)
- pressure_hpa (float)
- wind_m_s (float)
- wind_gust_m_s (float)
- data_source (string: "live")

**FR-DATA-004:** System shall create one CSV file per day:
- Filename format: `weather_YYYY-MM-DD.csv`
- Location: `data/logged_weather/`

**FR-DATA-005:** System shall append to existing file if date matches, create new file if new day.

**FR-DATA-006:** System shall log success/failure of each collection attempt.

**FR-DATA-007:** System shall continue collection even if API fails (skip that hour).

#### 3.4.3 Performance Requirements
- Logging operation: < 500ms
- Storage per record: ~150 bytes
- Monthly storage: ~110 KB (720 records)

### 3.5 LSTM Model Training

**Priority:** Medium  
**Risk:** Medium

#### 3.5.1 Description
System provides capability to train LSTM models on collected weather data.

#### 3.5.2 Functional Requirements

**FR-MODEL-001:** System shall accept training command: `python -m src.cli.train`

**FR-MODEL-002:** System shall support model types:
- LSTM (primary)
- Baseline (mean predictor, for comparison)

**FR-MODEL-003:** System shall preprocess training data:
- Build feature matrix with 24-hour lookback
- Compute rolling mean, rolling std
- Normalize using StandardScaler

**FR-MODEL-004:** System shall split data:
- 80% training
- 20% validation

**FR-MODEL-005:** System shall build LSTM architecture:
- Input: (sequence_length=24, n_features)
- LSTM layers: 2 layers with 32 units each
- Dropout: 0.2
- Output: 3 neurons (for 1h, 3h, 6h predictions)

**FR-MODEL-006:** System shall train with:
- Optimizer: Adam
- Loss: Mean Squared Error (MSE)
- Metrics: MAE, RMSE
- Early stopping: patience=10 epochs
- Max epochs: 100

**FR-MODEL-007:** System shall save trained model:
- Format: Keras HDF5 (.keras)
- Location: `experiments/YYYYMMDD_HHMMSS/model.keras`
- Also save to: `experiments/latest/model.keras`

**FR-MODEL-008:** System shall save training metadata:
- Training history (loss curves)
- Scaler parameters (mean, std)
- Feature column names
- Timestamp of training

**FR-MODEL-009:** System shall generate evaluation plots:
- Training/validation loss curves
- Prediction vs actual scatter plots
- Residual plots

#### 3.5.3 Performance Requirements
- Training time: < 5 minutes on sample data (2000 records)
- Model size: < 2 MB
- Inference latency: < 100ms per prediction

### 3.6 User Interface Commands

**Priority:** High  
**Risk:** Low

#### 3.6.1 Description
Telegram bot provides command-based interface for user interaction.

#### 3.6.2 Functional Requirements

**FR-UI-001:** System shall respond to `/start` command with:
- Welcome message
- Current location
- BWF threshold information
- Main menu keyboard

**FR-UI-002:** System shall respond to `/help` command with:
- List of available commands
- Usage examples
- BWF standards explanation
- Back to menu button

**FR-UI-003:** System shall respond to `/now` command (see Section 3.1).

**FR-UI-004:** System shall respond to `/forecast` command (see Section 3.2).

**FR-UI-005:** System shall respond to `/location <city>` command (see Section 3.3).

**FR-UI-006:** System shall provide inline keyboard buttons:
- "🌤️ Check Now" → triggers /now
- "📊 Get Forecast" → triggers /forecast
- "❓ Help" → triggers /help
- "📍 Location" → shows location instructions

**FR-UI-007:** System shall handle unknown commands:
- Display "Unknown command" message
- Suggest using /help
- Show main menu

**FR-UI-008:** System shall use Markdown formatting for:
- Bold headers
- Code blocks for thresholds
- Emoji indicators

### 3.7 Error Tracking and Monitoring

**Priority:** Medium  
**Risk:** Low

#### 3.7.1 Description
System integrates with Sentry for error tracking and monitoring.

#### 3.7.2 Functional Requirements

**FR-MONITOR-001:** System shall initialize Sentry SDK if `SENTRY_DSN` environment variable is set.

**FR-MONITOR-002:** System shall capture and report:
- Python exceptions
- API errors (weather, Telegram)
- Model loading failures
- Data logging errors

**FR-MONITOR-003:** System shall include context in error reports:
- User ID (hashed)
- Command that triggered error
- Timestamp
- Environment (production/development)

**FR-MONITOR-004:** System shall log warnings to console:
- Missing environment variables
- API rate limit warnings
- Model not found warnings

**FR-MONITOR-005:** System shall continue operation even if Sentry fails to initialize.

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Telegram Bot Interface

**UI-001:** Chat-based interface using Telegram messaging app

**UI-002:** Text command input format:
```
/command [optional_argument]
```

**UI-003:** Interactive button interface using InlineKeyboardMarkup:
- Button layout: Grid format (2 columns)
- Button labels: Emoji + text (e.g., "🌤️ Check Now")

**UI-004:** Message formatting:
- Headers: Bold, large font
- Data: Monospace for numerical values
- Status indicators: Emoji (✅, ❌, ⚠️)

**UI-005:** Response structure:
```
[DECISION INDICATOR]
📍 Location: City Name
🌐 Data Source: Live Weather Data
🕒 Current Time: HH:MM AM/PM IST

⛅ Current Weather Conditions:
✅ Wind Speed: X.X m/s (Y.Y km/h)
✅ Wind Gusts: X.X m/s (Y.Y km/h)
🌡️ Temperature: XX.X°C
💧 Humidity: XX%
📊 Pressure: XXXX hPa

[ACTION BUTTONS]
```

### 4.2 Hardware Interfaces
Not applicable. System is cloud-hosted with no direct hardware interfaces.

### 4.3 Software Interfaces

#### 4.3.1 OpenWeatherMap API

**API-OWM-001:** Base URL: `https://api.openweathermap.org/data/2.5/`

**API-OWM-002:** Endpoints used:
- Current weather: `GET /weather`
- Hourly forecast: `GET /forecast`
- Geocoding: `GET /geo/1.0/direct`

**API-OWM-003:** Authentication: API key in query parameter `appid`

**API-OWM-004:** Request parameters:
```
lat: float (latitude, -90 to 90)
lon: float (longitude, -180 to 180)
units: string (metric, imperial, standard)
appid: string (API key)
```

**API-OWM-005:** Response format: JSON

**API-OWM-006:** Rate limit: 60 calls/minute

**API-OWM-007:** Error handling:
- 401: Invalid API key
- 404: Location not found
- 429: Rate limit exceeded
- 5xx: Server error

#### 4.3.2 Telegram Bot API

**API-TG-001:** Base URL: `https://api.telegram.org/bot<token>/`

**API-TG-002:** Methods used:
- `getUpdates`: Long polling for new messages
- `sendMessage`: Send text responses
- `editMessageText`: Update existing messages
- `answerCallbackQuery`: Respond to button clicks

**API-TG-003:** Authentication: Bot token in URL path

**API-TG-004:** Update polling:
- Method: Long polling
- Timeout: 30 seconds
- Allowed updates: ["message", "callback_query"]

**API-TG-005:** Message formatting: Markdown parse mode

#### 4.3.3 Sentry Error Tracking

**API-SENTRY-001:** SDK: `sentry-sdk` Python package

**API-SENTRY-002:** Initialization parameters:
```python
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
    environment="production",
    release="badminton-bot@version"
)
```

**API-SENTRY-003:** Auto-capture: All unhandled exceptions

**API-SENTRY-004:** Manual capture: Custom error messages

### 4.4 Communication Interfaces

**COMM-001:** Protocol: HTTPS for all external API calls

**COMM-002:** Data format: JSON for API requests/responses

**COMM-003:** Encoding: UTF-8 for all text data

**COMM-004:** Network requirements: Internet connection required

---

## 5. System Requirements

### 5.1 Functional Requirements Summary

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-SYS-001 | System shall operate 24/7 without manual intervention | High | ✅ Implemented |
| FR-SYS-002 | System shall handle multiple concurrent users | Medium | ✅ Implemented |
| FR-SYS-003 | System shall persist across restarts (stateless bot) | High | ✅ Implemented |
| FR-SYS-004 | System shall auto-deploy on code changes | Medium | ✅ Implemented |
| FR-SYS-005 | System shall log all operations | High | ✅ Implemented |

### 5.2 Hardware Requirements

#### 5.2.1 Production Server (Railway.app)
- **CPU:** 1 vCPU (shared)
- **RAM:** 512 MB minimum, 1 GB recommended
- **Storage:** 1 GB for code, data, and model
- **Network:** Stable internet connection

#### 5.2.2 Development Environment
- **CPU:** 2+ cores recommended
- **RAM:** 4 GB minimum, 8 GB recommended
- **Storage:** 5 GB for development tools and data
- **GPU:** Optional, for faster model training

### 5.3 Software Requirements

#### 5.3.1 Production Environment
- **Operating System:** Ubuntu 20.04+ (Linux container)
- **Python:** 3.10.x
- **Package Manager:** pip 23.0+
- **Container Runtime:** Docker (managed by Railway)

#### 5.3.2 Core Dependencies
```
tensorflow==2.16.1
numpy==1.26.4
pandas==2.2.0
scikit-learn==1.5.0
python-telegram-bot[job-queue]==22.5
APScheduler==3.11.1
requests==2.32.5
python-dotenv==1.2.1
sentry-sdk==2.43.0
```

#### 5.3.3 Development Dependencies
```
pytest>=9.0.0
pytest-cov>=7.0.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
```

### 5.4 Database Requirements

**DB-001:** No relational database required

**DB-002:** File-based storage using CSV format:
- Location: `data/logged_weather/`
- Format: CSV with header row
- Encoding: UTF-8
- Delimiter: Comma

**DB-003:** Model storage:
- Format: Keras HDF5 (.keras files)
- Location: `experiments/*/model.keras`
- Size: < 2 MB per model

**DB-004:** Configuration storage:
- Format: JSON
- Files: `thresholds.json`, scaler parameters
- Location: `src/decision/`, experiment directories

---

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

**PERF-001:** API Response Time
- Current weather fetch: < 2 seconds
- Forecast fetch: < 3 seconds
- Model inference: < 1 second

**PERF-002:** Bot Response Time
- Simple commands (/start, /help): < 2 seconds
- Weather check (/now): < 5 seconds
- Forecast (/forecast): < 8 seconds

**PERF-003:** System Throughput
- Support: 100+ concurrent users
- Message handling: 10 messages/second minimum

**PERF-004:** Resource Utilization
- RAM usage: < 200 MB average
- CPU usage: < 5% average
- Storage growth: < 5 MB/month

**PERF-005:** Model Performance
- MAE (Mean Absolute Error): < 1.0 m/s
- RMSE (Root Mean Squared Error): < 1.5 m/s
- Training time: < 10 minutes on 10,000 samples

### 6.2 Safety Requirements

**SAFE-001:** The system shall apply safety margins to BWF thresholds:
- Never recommend play when wind > 3.33 m/s
- Never recommend play when gusts > 5.0 m/s

**SAFE-002:** The system shall display clear warnings when conditions are borderline:
- Wind between 3.0-3.33 m/s: Show warning message
- Include disclaimer: "Use your own judgment"

**SAFE-003:** The system shall prioritize safety over accuracy:
- If forecast uncertain, recommend "DON'T PLAY"
- Display confidence levels when available

**SAFE-004:** The system shall not store sensitive user data:
- No personal information collected
- No location tracking beyond session
- No message history retained

### 6.3 Security Requirements

**SEC-001:** API Key Protection
- Store keys in environment variables only
- Never commit keys to version control
- Rotate keys quarterly

**SEC-002:** Bot Token Security
- Use secure token storage (Railway secrets)
- Implement rate limiting to prevent abuse
- Monitor for unauthorized access

**SEC-003:** Data Privacy
- No user profiling or tracking
- Anonymize logs (hash user IDs)
- GDPR-compliant data handling

**SEC-004:** Code Security
- Run security scans in CI/CD (Bandit, Safety)
- Keep dependencies updated
- Use Dependabot for vulnerability alerts

**SEC-005:** Transport Security
- All API calls over HTTPS
- No plain HTTP communication
- Verify SSL certificates

### 6.4 Software Quality Attributes

#### 6.4.1 Reliability
**REL-001:** System uptime: 99% availability (excludes planned maintenance)

**REL-002:** Error recovery: Automatic restart on crash (max 10 retries)

**REL-003:** Data integrity: Validate all API responses before processing

**REL-004:** Fault tolerance: Continue operation if non-critical services fail

#### 6.4.2 Maintainability
**MAINT-001:** Code organization: Modular architecture with clear separation of concerns

**MAINT-002:** Documentation: Inline comments, docstrings, README files

**MAINT-003:** Code style: Follow PEP 8, enforced by Black and isort

**MAINT-004:** Testing: 30%+ code coverage, unit + integration tests

**MAINT-005:** Version control: Git with semantic commit messages

#### 6.4.3 Portability
**PORT-001:** Platform independence: Run on Windows, macOS, Linux

**PORT-002:** Deployment flexibility: Support multiple cloud platforms (Railway, Fly.io, Render)

**PORT-003:** Container support: Docker-compatible deployment

#### 6.4.4 Scalability
**SCALE-001:** Horizontal scaling: Support multiple bot instances (future)

**SCALE-002:** Data growth: Handle up to 100,000 weather records

**SCALE-003:** User growth: Support 1,000+ active users

#### 6.4.5 Usability
**USE-001:** Learning curve: New users can make queries within 1 minute

**USE-002:** Help accessibility: `/help` command always available

**USE-003:** Error messages: Clear, actionable error descriptions

**USE-004:** Response clarity: Use plain language, avoid technical jargon

### 6.5 Business Rules

**BIZ-001:** BWF Compliance
- System must adhere to BWF wind speed standards at all times
- Thresholds cannot be user-configurable (safety reasons)

**BIZ-002:** Cost Management
- Monthly operational cost must not exceed $5 USD
- Implement resource monitoring and auto-alerts

**BIZ-003:** API Usage
- OpenWeatherMap: Stay within free tier limits (1M calls/month)
- Implement caching to reduce API calls

**BIZ-004:** Data Retention
- Keep weather logs for minimum 30 days
- Archive data older than 90 days
- Delete data older than 1 year (optional)

**BIZ-005:** Model Updates
- Retrain model minimum every 30 days
- Validate new model before deployment
- Keep previous model as backup

---

## 7. Data Requirements

### 7.1 Logical Data Model

#### 7.1.1 Weather Data Record
```
WeatherRecord {
    timestamp: DateTime (ISO 8601)
    location: String
    latitude: Float (4 decimals)
    longitude: Float (4 decimals)
    temperature_c: Float
    humidity_percent: Integer (0-100)
    pressure_hpa: Float
    wind_m_s: Float (primary target variable)
    wind_gust_m_s: Float
    data_source: Enum("live", "forecast", "synthetic")
}
```

#### 7.1.2 Forecast Record
```
Forecast {
    horizon: Integer (1, 3, or 6 hours)
    median_wind: Float (m/s)
    q90_wind: Float (m/s)
    timestamp: DateTime
    location: String
    model_version: String
}
```

#### 7.1.3 Decision Record
```
Decision {
    can_play: Boolean
    reason: String
    wind_speed: Float
    wind_gust: Float
    threshold_median: Float (3.33 m/s)
    threshold_gust: Float (5.0 m/s)
    timestamp: DateTime
}
```

### 7.2 Data Dictionary

| Field Name | Data Type | Units | Range | Description |
|------------|-----------|-------|-------|-------------|
| timestamp | ISO 8601 String | - | Any valid datetime | When measurement was taken |
| location | String | - | - | Human-readable location name |
| latitude | Float | degrees | -90 to 90 | Latitude in decimal degrees |
| longitude | Float | degrees | -180 to 180 | Longitude in decimal degrees |
| temperature_c | Float | Celsius | -50 to 60 | Air temperature |
| humidity_percent | Integer | % | 0 to 100 | Relative humidity |
| pressure_hpa | Float | hPa | 900 to 1100 | Atmospheric pressure |
| wind_m_s | Float | m/s | 0 to 50 | Wind speed at 10m height |
| wind_gust_m_s | Float | m/s | 0 to 100 | Maximum wind gust speed |
| median_forecast | Float | m/s | 0 to 50 | 50th percentile forecast |
| q90_forecast | Float | m/s | 0 to 100 | 90th percentile forecast |

### 7.3 Data Flow Diagrams

#### 7.3.1 Current Weather Check Flow
```
User (/now) → Bot → Weather API → Response Parser → Decision Engine → Bot → User
                                       ↓
                                   Data Logger → CSV File
```

#### 7.3.2 Forecast Generation Flow
```
User (/forecast) → Bot → Weather API → Feature Engineering → LSTM Model → Decision Engine → Bot → User
                                                                ↑
                                                        Saved Model (.keras)
```

#### 7.3.3 Data Collection Flow
```
Scheduler (hourly) → Weather API → Response Parser → CSV Writer → data/logged_weather/
```

### 7.4 Data Storage

**STORAGE-001:** Format: CSV (Comma-Separated Values)

**STORAGE-002:** Directory structure:
```
data/
├── logged_weather/
│   ├── weather_2025-11-12.csv
│   ├── weather_2025-11-13.csv
│   └── ...
├── collected/
│   └── weather_observations.csv (legacy)
└── sample_station.csv (synthetic data for testing)
```

**STORAGE-003:** File naming convention:
- Daily logs: `weather_YYYY-MM-DD.csv`
- Archive: `weather_archive_YYYY-MM.tar.gz`

**STORAGE-004:** Backup strategy:
- Git version control for code
- Railway automatic backups for data
- Manual monthly archives recommended

---

## 8. Appendices

### 8.1 Appendix A: BWF Wind Speed Standards

Reference: docs/BWF_STANDARDS.md

**Maximum Wind Speed:** 12 km/h (3.33 m/s)  
**Optimal Range:** 6-12 km/h (1.67-3.33 m/s)  
**Gust Threshold (Bot):** 18 km/h (5.0 m/s)

Conversion formula:
- m/s to km/h: multiply by 3.6
- km/h to m/s: divide by 3.6

### 8.2 Appendix B: Project Structure

```
badminton-bot/
├── src/                          # Source code
│   ├── cli/                      # Command-line interfaces
│   │   ├── train.py              # Model training
│   │   └── infer.py              # Model inference
│   ├── data/                     # Data handling
│   │   ├── weather_api.py        # API connectors
│   │   ├── preprocess.py         # Feature engineering
│   │   ├── weather_logger.py     # Data logging
│   │   └── fetch.py              # Data fetching
│   ├── decision/                 # Decision logic
│   │   └── rules.py              # BWF threshold rules
│   ├── eval/                     # Model evaluation
│   │   ├── metrics.py            # Performance metrics
│   │   └── backtest.py           # Backtesting
│   ├── integrations/             # Bot interfaces
│   │   ├── telegram_bot_refactored.py  # Main bot (production)
│   │   ├── bot_formatters.py     # Message formatting
│   │   ├── bot_weather.py        # Weather data handling
│   │   ├── bot_keyboards.py      # UI keyboards
│   │   └── bot_location.py       # Location management
│   ├── models/                   # ML models
│   │   ├── lstm_model.py         # LSTM implementation
│   │   ├── baseline.py           # Baseline models
│   │   └── quantiles.py          # Quantile regression
│   ├── utils/                    # Utilities
│   │   └── io.py                 # I/O helpers
│   └── config.py                 # Central configuration
├── tests/                        # Test suites
│   ├── unit/                     # Unit tests
│   │   ├── test_bot_formatters.py
│   │   ├── test_bot_keyboards.py
│   │   ├── test_bot_location.py
│   │   └── test_bot_weather.py
│   ├── integration/              # Integration tests
│   │   ├── test_weather_api.py
│   │   ├── test_bwf_thresholds.py
│   │   └── test_final_integration.py
│   ├── test_decision.py          # Decision logic tests
│   ├── test_metrics.py           # Metrics tests
│   └── test_preprocess.py        # Preprocessing tests
├── scripts/                      # Utility scripts
│   ├── check_data_collection.py  # Data collection monitor
│   ├── quick_progress.py         # Progress checker
│   ├── estimate_railway_cost.py  # Cost estimator
│   └── pre_deploy_check.py       # Deployment validator
├── docs/                         # Documentation
│   ├── SRS.md                    # This document
│   ├── BWF_STANDARDS.md          # BWF compliance
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── PHASE_1_DATA_COLLECTION.md
│   ├── RAILWAY_COST_OPTIMIZATION.md
│   └── USER_GUIDE.md
├── data/                         # Data directory
│   └── logged_weather/           # Hourly weather logs
├── experiments/                  # ML experiments
│   └── latest/                   # Latest trained model
│       └── model.keras
├── .github/workflows/            # CI/CD pipelines
│   └── test.yml                  # Test automation
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project metadata
├── railway.toml                  # Railway config
└── README.md                     # Project overview
```

### 8.3 Appendix C: API Endpoints

#### OpenWeatherMap API

**Current Weather:**
```
GET https://api.openweathermap.org/data/2.5/weather
Parameters:
  - lat: float (required)
  - lon: float (required)
  - appid: string (required)
  - units: metric
```

**Hourly Forecast:**
```
GET https://api.openweathermap.org/data/2.5/forecast
Parameters:
  - lat: float (required)
  - lon: float (required)
  - appid: string (required)
  - units: metric
  - cnt: 40 (5-day forecast, 3-hour intervals)
```

**Geocoding:**
```
GET http://api.openweathermap.org/geo/1.0/direct
Parameters:
  - q: string (city name)
  - appid: string (required)
  - limit: 1
```

### 8.4 Appendix D: Telegram Bot Commands

| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| /start | None | Initialize bot, show main menu | `/start` |
| /help | None | Display usage instructions | `/help` |
| /now | None | Get current weather & decision | `/now` |
| /forecast | None | Get ML-powered forecast | `/forecast` |
| /location | city_name | Change location | `/location Delhi` |

### 8.5 Appendix E: Error Codes

| Code | Description | User Message | Recovery Action |
|------|-------------|--------------|-----------------|
| API-001 | Weather API unavailable | "Weather service temporarily unavailable" | Retry after 30s |
| API-002 | Invalid API key | "Configuration error. Please contact admin" | Check environment variables |
| API-003 | Rate limit exceeded | "Too many requests. Please try again later" | Wait 60s, implement backoff |
| MODEL-001 | Model file not found | "Forecast unavailable. Using current data only" | Use fallback to NOW mode |
| MODEL-002 | Model loading failed | "Forecast service error" | Check model file integrity |
| DATA-001 | Invalid location | "Location not found. Please check spelling" | Suggest nearby cities |
| BOT-001 | Telegram API error | "Message delivery failed. Retrying..." | Auto-retry 3 times |

### 8.6 Appendix F: Test Coverage

**Unit Tests (48 tests):**
- bot_formatters: 12 tests
- bot_keyboards: 8 tests
- bot_location: 14 tests
- bot_weather: 14 tests

**Integration Tests (32 tests):**
- Weather API integration: 8 tests
- BWF threshold compliance: 6 tests
- End-to-end forecast flow: 8 tests
- Bot command handling: 10 tests

**Code Coverage:** 30.43% (target: 40%)

### 8.7 Appendix G: Deployment Checklist

Pre-deployment:
- [ ] All tests passing
- [ ] Environment variables set
- [ ] Model file uploaded
- [ ] API keys validated
- [ ] Documentation updated

Post-deployment:
- [ ] Bot responding to /start
- [ ] Weather data fetching correctly
- [ ] Forecast generating predictions
- [ ] Data logging active
- [ ] Error tracking configured

### 8.8 Appendix H: Cost Breakdown (Railway.app)

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| RAM | 150 MB avg | $0.25 |
| CPU | <1% avg | $0.10 |
| Network | <1 GB | $0.00 (free tier) |
| Storage | <500 MB | $0.00 (free tier) |
| **Total** | | **~$0.50-$2.00** |

**Free Credit:** $5/month  
**Projected Usage:** 10-40% of free credit

### 8.9 Appendix I: Future Enhancements

**Phase 2 (Planned):**
- Mobile app (React Native)
- Web dashboard (Gradio/Streamlit)
- Multi-language support
- Historical data visualization
- Custom notification schedules

**Phase 3 (Future):**
- WhatsApp bot integration
- Advanced ML models (Transformer, GRU)
- Rain prediction
- Court recommendation system
- Social features (player matching)

### 8.10 Appendix J: Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1.0 | 2024-10-15 | Initial MVP release | Team |
| 0.2.0 | 2024-11-01 | BWF compliance update | Team |
| 0.3.0 | 2024-11-10 | Refactored architecture | Team |
| 1.0.0 | 2024-11-15 | Production release | Team |

---

## Document Approval

**Prepared By:** Development Team  
**Date:** November 15, 2025  
**Version:** 1.0  
**Status:** Approved

**Reviewed By:**
- [ ] Technical Lead
- [ ] Project Manager
- [ ] QA Team

**Approved By:**
- [ ] Product Owner
- [ ] Stakeholders

---

**End of Software Requirements Specification**
