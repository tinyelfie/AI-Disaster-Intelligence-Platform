# Dataset Report: AI Disaster Intelligence Platform

This report provides a detailed overview of the four core datasets included in the AI Disaster Intelligence Platform, located within the `data/raw/` directory. These datasets offer a comprehensive view of global disasters, combining meteorological data, historical disaster impact metrics, real-time social media sentiment, and visual imagery for automated detection.

## 1. Daily Global Capitals Weather Data
**Location:** `data/raw/weather/Daily Global Capitals Weather Data/`
**Files:** `history_latest.csv`, `history.parquet`, `capitals_clean.parquet`

This dataset provides daily meteorological measurements for capital cities worldwide. It serves as the baseline environmental and climatic context for analyzing disaster events.

### Key Features (Schema)
* **Location Data:** `country`, `country_alpha2`, `capital`, `lat`, `lon`
* **Temperature Metrics (°C):** `temp_min_c`, `temp_max_c`, `temp_mean_c_approx`, `app_temp_min_c`, `app_temp_max_c`
* **Precipitation (mm):** `precip_mm`, `rain_mm`, `snow_mm`
* **Wind Conditions (km/h):** `windspeed_10m_max_kmh`, `windgusts_10m_max_kmh`, `wind_dir_dom_deg`
* **Solar Radiation & Daylight:** `sunshine_duration_s`, `daylight_duration_s`, `shortwave_radiation_MJ_m2`

### Potential Use Cases
* **Climatic Baseline Modeling:** Establishing normal weather patterns to identify extreme deviations that precede or accompany natural disasters.
* **Predictive Weather Analytics:** Correlating extreme temperatures, heavy rainfall, or high wind gusts with the likelihood of specific disaster types (e.g., floods, wildfires, hurricanes).

## 2. Disaster & Emergency Response Dataset
**Location:** `data/raw/weather/Disaster & Emergency Response Dataset/`
**File:** `global_disaster_events.csv`

This dataset logs historical global disaster events, quantifying their severity, human impact, economic toll, and the efficiency of the emergency response. 

### Key Features (Schema)
* **Event Metadata:** `date`, `country`, `latitude`, `longitude`, `disaster_type` (e.g., Earthquake, Flood, Wildfire, Extreme Heat, Tornado, Storm Surge, Hurricane)
* **Impact Metrics:** `severity_index`, `casualties`, `economic_loss_usd`
* **Response & Recovery:** `response_time_hours`, `aid_amount_usd`, `response_efficiency_score`, `recovery_days`

### Potential Use Cases
* **Risk Assessment & Vulnerability Mapping:** Identifying geographical regions most susceptible to specific types of disasters and assessing historical human/economic losses.
* **Emergency Response Optimization:** Analyzing `response_time_hours` and `aid_amount_usd` against the `response_efficiency_score` to model optimal resource allocation during crises.

## 3. Disaster Tweets
**Location:** `data/raw/tweets/Disaster Tweets/`
**File:** `disaster_tweets.csv`

This dataset captures social media activity (Twitter/X) surrounding disaster events. It provides crowdsourced, real-time ground-truth information, public sentiment, and situational awareness.

### Key Features (Schema)
* **User Info:** `Name`, `UserName`, `Verified`
* **Tweet Metadata:** `Timestamp`, `Tweet ID`, `Tweet Link`
* **Content & Categorization:** `Tweets` (text content), `Tags` (hashtags used), `Disaster` (categorization of the tweet)
* **Engagement Metrics:** `Comments`, `Retweets`, `Likes`, `Impressions`

### Potential Use Cases
* **Real-time Event Detection:** Using Natural Language Processing (NLP) on tweet text and timestamps to detect early signals of unfolding disasters before official reports are released.
* **Sentiment Analysis & Public Needs Assessment:** Analyzing tweets to gauge public panic, identifying urgent needs (e.g., trapped individuals, supply shortages), and tracking the spread of misinformation during crises.

## 4. Cyclone, Wildfire, Flood, and Earthquake Image Database
**Location:** `data/raw/satellite/Cyclone_Wildfire_Flood_Earthquake_Database/`

This dataset consists of images collected for computer vision and image classification tasks related to disasters. It is organized into distinct classes representing different disaster types.

### Key Features
* **Classes:** Four directories categorizing images by disaster type (`Cyclone`, `Earthquake`, `Flood`, `Wildfire`).
* **Format:** Primarily unstructured image data (e.g., `.jpg`) sourced from the internet, varying in resolution and noise.

### Potential Use Cases
* **Automated Visual Detection:** Training convolutional neural networks (CNNs) to automatically detect disasters from visual feeds (e.g., satellite imagery, drone footage, or surveillance cameras).
* **Early Warning Systems:** Deploying computer vision models along riverbeds for flood detection, or using park ranger cameras for early wildfire spotting.
* **Media Triage:** Assisting news agencies or emergency services in rapidly sorting and verifying user-submitted photos or video archives.

## Cross-Dataset Synergies
The true power of the AI Disaster Intelligence Platform lies in combining these four datasets:
1. **Multi-Modal Early Warning System:** Correlating severe weather forecasts (**Weather Data**) with automated visual detection from cameras/satellites (**Image Database**) to trigger faster, more accurate alarms before disaster strikes.
2. **Real-time Impact Validation:** Using crowdsourced **Disaster Tweets** alongside visual evidence (**Image Database**) to validate the ground-level impact of severe weather anomalies, providing immediate context to the structured **Disaster Events** data.
3. **Comprehensive Post-Mortem Analysis:** Evaluating the full lifecycle of a disaster—from the climatic conditions leading up to it, the visual extent of the damage, the public's real-time reaction, to the final economic/human toll and the effectiveness of the emergency response.
