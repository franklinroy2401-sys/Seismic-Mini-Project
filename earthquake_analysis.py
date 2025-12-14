# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import sqlalchemy
import mysql.connector
import streamlit as st

print("All packages are working!")




# %%
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def download_earthquake_data(start_year, end_year, min_magnitude=2.5):
    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    # 1. Setup Date Range
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    current_date = start_date

    all_records = []

    print(f"--- Starting Download ({start_year}-{end_year}) ---")

    # 2. Loop through months
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        if month_end > end_date:
            month_end = end_date

        str_start = current_date.strftime("%Y-%m-%d")
        str_end = month_end.strftime("%Y-%m-%d")

        params = {
            "format": "geojson",
            "starttime": str_start,
            "endtime": str_end,
            "minmagnitude": min_magnitude
        }

        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])

                for feature in features:
                    props = feature["properties"]
                    geom = feature["geometry"]
                    coords = geom["coordinates"] if geom else [None, None, None]

                    # --- FIXING THE TIME HERE ---
                    # 1. Get raw milliseconds
                    raw_time = props.get("time")
                    raw_updated = props.get("updated")

                    # 2. Convert to Datetime Object (Handling Milliseconds)
                    # We use unit='ms' because USGS gives milliseconds
                    dt_time = pd.to_datetime(raw_time, unit='ms')
                    dt_updated = pd.to_datetime(raw_updated, unit='ms')

                    record = {
                        "id": feature["id"],
                        "ids": props.get("ids"),
                        "sources": props.get("sources"),

                        # Save the readable datetime immediately
                        "time": dt_time,
                        "updated": dt_updated,

                        # --- CREATE DERIVED COLUMNS NOW ---
                        "year": dt_time.year,
                        "month": dt_time.month,
                        "day": dt_time.day,
                        "day_of_week": dt_time.day_name(),
                        # ----------------------------------

                        "latitude": coords[1] if coords else None,
                        "longitude": coords[0] if coords else None,
                        "depth_km": coords[2] if coords else None,
                        "place": props.get("place"),
                        "locationSource": props.get("locationSource"),
                        "mag": props.get("mag"),
                        "magType": props.get("magType"),
                        "magError": props.get("magError"),
                        "magNst": props.get("magNst"),
                        "magSource": props.get("magSource"),
                        "nst": props.get("nst"),
                        "dmin": props.get("dmin"),
                        "rms": props.get("rms"),
                        "gap": props.get("gap"),
                        "depthError": props.get("depthError"),
                        "sig": props.get("sig"),
                        "status": props.get("status"),
                        "net": props.get("net"),
                        "type": props.get("type"),
                        "types": props.get("types"),
                        "tsunami": props.get("tsunami")
                    }
                    all_records.append(record)
                
                print(f"Success: {str_start} to {str_end} | Records: {len(features)}")
            else:
                print(f"Failed: {str_start} (Status {response.status_code})")

        except Exception as e:
            print(f"Error: {str_start} - {e}")

        current_date = next_month
        time.sleep(0.5)

    df = pd.DataFrame(all_records)
    return df

# --- EXECUTION ---
START_YEAR = 2020
END_YEAR = 2025
MIN_MAG = 2.5

df_raw = download_earthquake_data(START_YEAR, END_YEAR, MIN_MAG)

output_filename = "earthquake_data_raw_25_updated.csv"
df_raw.to_csv(output_filename, index=False)

print(f"\nDownload Complete.")
print(f"Total Rows: {len(df_raw)}")
print(f"File saved as: {output_filename}")

# %%
# ============================================================
# STEP 1: Load and check the missing values in the Data
# ============================================================
# 1. Load the raw data
df_raw = pd.read_csv("earthquake_data_raw_25_updated.csv")
df_raw

#2. calculate missing values per column
# isnull() check for empty spots, sum() counts them
missing_counts = df_raw.isnull().sum()
missing_counts

# 3. Filter to show only columns that have missing Data
missing_data = missing_counts[missing_counts >0]
missing_data







# %%
# =========================================
# Step 2: Handle Empty Variables
# =========================================
rms = df_raw['rms'].median()
df_raw['rms'] = df_raw['rms'].fillna(rms)

# Fill the Missing Numeric values with 0
missing_cols = ['magError', 'depthError', 'nst', 'dmin', 'gap', 'magNst']
for cols in missing_cols:
  df_raw[cols] = df_raw[cols].fillna(0)

# Handle Text Field with Unknown
text_cols = ['magSource', 'locationSource', 'net', 'type', 'place', 'magType']
for cols in text_cols:
  df_raw[cols] = df_raw[cols].fillna("Unknown")

check_cols = ['magError', 'magType', 'depthError', 'rms', 'gap', 'nst', 'dmin', 'magNst']
result = df_raw[check_cols].isnull().sum()

result

# %%
from numpy import place
# ==========================================
# Step 3: Extract "Country" (using Regex)
# ==========================================
def extract_country_name(place_text):
    # If the text is missing, return unknown
   if pd.isna(place_text):
      return "Unknown"

   # Regex Explanation:
   # ,         -> look for a comma
   # \s*       -> Followed by any amount of whutespace
   # ([^,]+)$  ->Capture everything that is Not a comma, until the end of the string ($)
   match = re.search(r',\s*([^,]+)$', str(place_text))

   if match:
      return match.group(1) # return the captured country name
   else:
      return place_text # If no comma found, Return the Original text

# Apply this function to every row in the 'place' comma
df_raw['country'] = df_raw['place'].apply(extract_country_name)
df_raw


# %%
# ================================================
# Step 5: Create Categories (depth & Magnitude)
# ================================================

# Logic for Depth: If depth > 70km it is "Deep", otherwise "shallow"
def get_depth_category(depth):
  if depth > 70:
    return "Deep"
  else:
    return "shallow"
# Logic for Magnitude: Categorizing how strong it is
def get_mag_category(mag):
  if mag >= 7.0:
    return "Destructive"
  elif mag >= 6.0:
    return "Strong"
  elif mag >= 4.5:
    return "Moderate"
  else:
    return "Minor"

# Apply these functions to create new columns
df_raw['depth_category'] = df_raw['depth_km'].apply(get_depth_category)
df_raw['magnitude_category'] = df_raw['mag'].apply(get_mag_category)
df_raw.head(10)


# %%
# ===================================
# Final Save the Update Datest
# ===================================

# Save to a new csv file
df_raw.to_csv("earthquake_data_cleaned_25_updated.csv", index=False)

print(f"Final Data Size: {df_raw.shape}")
print("New file saved as: 'earthquake_data_cleaned_25_updated.csv'")


# %%
new_data=pd.read_csv('earthquake_data_cleaned_25_updated.csv')
new_data.head(10)


# %%
import pandas as pd
from sqlalchemy import create_engine

# 1. Load your cleaned dataset
df = pd.read_csv("earthquake_data_cleaned_25_updated.csv")
print("Data Loaded. Rows:", len(df))

# 2. MySQL Connection Details
db_user = 'root'
db_password = 'RoyFrank'
db_host = 'localhost'        # <-- updated
db_port = '3306'
db_name = 'seismic_project'

# 3. Create the connection engine
connection_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_str)

try:
    print("Connecting to MySQL...")

    # 4. Upload Data into table 'earthquake'
    df.to_sql(
        'earthquake',
        con=engine,
        if_exists='replace',   # replaces if table already exists
        index=False
    )

    print("SUCCESS: Data uploaded to table 'earthquake'!")

except Exception as e:
    print("Error:", e)



