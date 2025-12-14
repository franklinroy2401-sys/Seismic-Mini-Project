# DS_Global_Seismic_Trends

## Project Description
This project analyzes global earthquake data using MySQL, Python, and Streamlit.  
It provides insights into earthquake magnitude, depth, casualties, and time trends.  
An interactive dashboard allows users to explore earthquake data using multiple filters such as country, year, magnitude, and depth.

## Tech Stack
- Python
- Pandas
- MySQL
- Streamlit

## Python Analysis
- File: `earthquake_analysis.py`
- Purpose: Clean and prepare earthquake data using Pandas and Regex, then load into MySQL

# DS_Global_Seismic_Trends

## Project Description
This project performs an end-to-end analysis of global earthquake data using Python, MySQL, and Streamlit.  
The goal is to identify seismic patterns based on magnitude, depth, time trends, country, and tsunami occurrence, and present the insights through an interactive dashboard.

---

## Tech Stack
- Python
- Pandas
- MySQL
- Streamlit
- Regex

---

## Dataset Overview
The dataset contains global earthquake records collected from seismic monitoring sources.

### Original Columns (Before Cleaning)
id, ids, sources, time, updated, latitude, longitude, depth_km, place, locationSource, mag, magType, magError, magNst, magSource, nst, dmin, rms, gap, depthError, sig, status, net, type, types, tsunami

---

## Project Workflow

### 1. Python Analysis (Data Cleaning & Preparation)
- **File:** `earthquake_analysis.py`
- Loaded earthquake data using Pandas
- Handled missing and inconsistent values
- Extracted `country` from the `place` column using Regex
- Created derived features:
  - `country`
  - `depth_category` (Shallow / Intermediate / Deep)
  - `magnitude_category` (Minor / Moderate / Strong / Major)
- Loaded the cleaned data into MySQL for analysis

---

### 2. Database & SQL Analysis
- **Database Name:** `seismic_project`
- **Table Name:** `earthquake`
- **File:** `earthquake_queries.sql`
- Performed SQL queries to analyze:
  - Strongest earthquakes by magnitude
  - Deepest earthquakes by depth
  - Shallow earthquakes with high magnitude
  - Year-wise earthquake trends
  - Tsunami-related earthquake events
  - Country-wise earthquake distribution

---

### 3. Streamlit Dashboard
- **File:** `app.py`
- Built an interactive dashboard to visualize earthquake data
- Implemented filters for:
  - Country
  - Year
  - Magnitude
  - Depth
- Displayed insights using tables and charts

---

## Features
- Magnitude and depth-based earthquake analysis
- Time-based earthquake analysis and trends
- Casualties and economic loss analysis
- Event type and seismic quality metrics analysis
- Tsunami-related earthquake and alert analysis
- Seismic pattern and trend analysis
- Depth, location, and distance-based earthquake analysis



---

## How to Run the Project
1. Create a MySQL database named `seismic_project`
2. Execute the SQL file:
   ```sql
SOURCE earthquake_queries.sql;
pip install -r requirements.txt
streamlit run app.py

