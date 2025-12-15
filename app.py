import streamlit as st
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv

# --------------------------------------------------
# 1. Streamlit config (MUST be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="🌍 Global Seismic Trends",
    layout="wide"
)

# --------------------------------------------------
# 2. Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# 3. MySQL Query Runner (SAFE)
# --------------------------------------------------
def run_query(query):
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "seismic_project"),
            port=int(os.getenv("DB_PORT", 3306))
        )

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    except Exception as e:
        st.error("❌ Database connection/query failed")
        st.code(str(e))
        return pd.DataFrame()

# --------------------------------------------------
# 4. Page Header
# --------------------------------------------------
st.title("🌍 Global Seismic Trends Dashboard")
st.markdown(
    """
    This dashboard displays **SQL-based analysis** of global earthquake data.
    Select a **topic** and **query** from the sidebar.
    """
)

# --------------------------------------------------
# 5. SQL Queries
# --------------------------------------------------
queries = {
    "Magnitude & Depth": {
        "Top 10 Strongest Earthquakes": """
            SELECT id, place, mag, country
            FROM earthquake
            ORDER BY mag DESC
            LIMIT 10;
        """,
        "Top 10 Deepest Earthquakes": """
            SELECT id, place, depth_km, country
            FROM earthquake
            ORDER BY depth_km DESC
            LIMIT 10;
        """,
        "Shallow & Strong (>7.5)": """
            SELECT id, place, mag, depth_km
            FROM earthquake
            WHERE depth_km < 50 AND mag > 7.5
            ORDER BY mag DESC;
        """,
        "Average Magnitude by Type": """
            SELECT magType, ROUND(AVG(mag),2) AS average_magnitude
            FROM earthquake
            GROUP BY magType
            ORDER BY average_magnitude DESC;
        """
    },

    "Time Analysis": {
        "Year with Most Earthquakes": """
            SELECT YEAR(time) AS year, COUNT(*) AS total
            FROM earthquake
            GROUP BY YEAR(time)
            ORDER BY total DESC
            LIMIT 1;
        """,
        "Month with the Highest Number of Earthquakes": """
               SELECT
                 month,
                 COUNT(*) AS earthquake_count
               FROM earthquake
               GROUP BY month
               ORDER BY earthquake_count DESC
               LIMIT 1;
          """,
        "Day of week with most earthquakes": """
            SELECT DAYNAME(time) AS day_of_week,
            COUNT(*) AS total_earthquakes
            FROM earthquake
            GROUP BY DAYNAME(time)
            ORDER BY total_earthquakes DESC
            LIMIT 1;
        """,
        "Earthquakes per Hour": """
            SELECT HOUR(time) AS hour_of_day, COUNT(*) AS total_earthquakes
            FROM earthquake
            GROUP BY HOUR(time)
            ORDER BY hour_of_day;
        """,
        "Most active reporting network (net)": """
            SELECT net,
            COUNT(*) AS total_reports
            FROM earthquake
            GROUP BY net
            ORDER BY total_reports DESC
            LIMIT 1;
        """
    },

    "Casualties & Economic Loss": {
        "Top 5 Highest Casualties": """
            SELECT place, mag, sig, country
            FROM earthquake
            ORDER BY sig DESC
            LIMIT 5;
        """,
        "Average economic loss by Alert Level": """
            SELECT
                CASE
                    WHEN mag >= 6 THEN 'Red'
                    WHEN mag >= 5 THEN 'Orange'
                    WHEN mag >= 4 THEN 'Yellow'
                    ELSE 'Green'
                END AS alert_level,
                COUNT(*) AS total_events
            FROM earthquake
            GROUP BY alert_level
            ORDER BY total_events DESC;
        """
    },

    "Event Type & Quality Metrics": {
        "Count of reviewed vs automatic earthquakes": """
            SELECT status, COUNT(*) AS total_events
            FROM earthquake
            GROUP BY status; 
        """,
        "Count by earthquake type": """
            SELECT type, COUNT(*) AS total_events
            FROM earthquake
            GROUP BY type
            ORDER BY total_events DESC;
        """,  
        "Number of earthquakes by 'types' column": """
            SELECT types, COUNT(*) AS total_events
            FROM earthquake
            GROUP BY types
            ORDER BY total_events DESC;
        """, 
        "Events with high station coverage (nst > threshold)": """
            SELECT id, place, mag, nst, time
            FROM earthquake
            WHERE nst > 50
            ORDER BY nst DESC;
        """
    },

    "Tsunamis & Alerts": {
        "Number of tsunamis triggered per year": """
            SELECT YEAR(time) AS year,
            COUNT(*) AS tsunami_count
            FROM earthquake
            WHERE tsunami = 1
            GROUP BY YEAR(time)
            ORDER BY year; 
        """, 
        "Count earthquakes by derived alert levels": """
            SELECT 
                CASE
                    WHEN mag >= 6 THEN 'red'
                    WHEN mag >= 5 THEN 'orange'
                    WHEN mag >= 4 THEN 'yellow'
                    ELSE 'green'
                END AS alert_level,
                COUNT(*) AS total_earthquakes
            FROM earthquake
            GROUP BY alert_level
            ORDER BY total_earthquakes DESC;
        """
    }, 

    "Seismic Pattern & Trends Analysis": {
        "Top 5 countries (Avg Mag - 5Y)": """
            SELECT 
                country, 
                AVG(mag) AS average_magnitude,
                COUNT(*) AS quake_count
            FROM earthquake
            WHERE time >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
            GROUP BY country
            HAVING quake_count > 5
            ORDER BY average_magnitude DESC
            LIMIT 5; 
        """,
        "Countries with shallow AND deep quakes (Same Month)": """
            SELECT 
                country,
                YEAR(time) AS year,
                MONTH(time) AS month
            FROM earthquake
            GROUP BY country, YEAR(time), MONTH(time)
            HAVING 
                SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) > 0
                AND
                SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) > 0;
        """,    
        "Year-over-year growth rate": """
            SELECT 
                y1.year,
                y1.total_quakes,
                y2.total_quakes AS previous_year_quakes,
                ROUND(
                    ((y1.total_quakes - y2.total_quakes) / y2.total_quakes) * 100,
                    2
                ) AS growth_rate_percentage
            FROM (
                SELECT YEAR(time) AS year, COUNT(*) AS total_quakes
                FROM earthquake
                GROUP BY YEAR(time)
            ) y1
            LEFT JOIN (
                SELECT YEAR(time) AS year, COUNT(*) AS total_quakes
                FROM earthquake
                GROUP BY YEAR(time)
            ) y2
            ON y1.year = y2.year + 1
            ORDER BY y1.year;
        """,
        "Top 3 Most Active Regions (Freq + Mag)": """
            SELECT 
                country, 
                COUNT(*) AS frequency, 
                ROUND(AVG(mag),2) AS avg_magnitude,
                ROUND(COUNT(*) * AVG(mag),2) AS seismic_activity_score
            FROM earthquake
            GROUP BY country
            ORDER BY seismic_activity_score DESC
            LIMIT 3;
        """
    },

    "Depth, Location & Distance-Based Analysis": {
        "Avg depth near Equator (+/- 5 deg)": """
            SELECT country,
            AVG(depth_km) AS avg_depth
            FROM earthquake
            WHERE latitude BETWEEN -5 AND 5
            GROUP BY country
            ORDER BY avg_depth;
        """,
        "Highest shallow-to-deep ratio": """
            SELECT country,
            SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_quakes,
            SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep_quakes,
            SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END), 0) AS shallow_deep_ratio
            FROM earthquake
            GROUP BY country
            ORDER BY shallow_deep_ratio DESC;
        """,
        "Mag Difference (Tsunami vs Non-Tsunami)": """
            SELECT 
            (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) AS avg_mag_tsunami,
            (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) AS avg_mag_no_tsunami,
            ( (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) -
            (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) ) AS magnitude_difference;
        """,
        "Low Reliability Events (Gap/RMS)": """
            SELECT id, place, mag, depth_km, gap, rms, time
            FROM earthquake
            WHERE gap IS NOT NULL AND rms IS NOT NULL
            ORDER BY gap DESC, rms DESC
            LIMIT 20;
        """,
        "Deep Quakes (>300km) by Country": """
            SELECT country AS region,
            COUNT(*) AS deep_focus_quakes
            FROM earthquake
            WHERE depth_km > 300
            GROUP BY country
            ORDER BY deep_focus_quakes DESC;
        """     
    }
}
# --------------------------------------------------
# 6. Sidebar Controls
# --------------------------------------------------
st.sidebar.header("🔍 Select Analysis")

topic = st.sidebar.selectbox(
    "Topic",
    list(queries.keys())
)

question = st.sidebar.selectbox(
    "Query",
    list(queries[topic].keys())
)

run = st.sidebar.button("▶ Run Query")

# --------------------------------------------------
# 7. Execute Query + Visualization
# --------------------------------------------------
if run:
    sql = queries[topic][question]

    st.subheader(f"{topic} → {question}")
    st.code(sql, language="sql")

    df = run_query(sql)

    if not df.empty:
        st.success(f"✅ Rows returned: {len(df)}")
        st.dataframe(df, use_container_width=True)

        # --------------------------------------------------
        # 8. Dynamic Visualization (Safe)
        # --------------------------------------------------
        st.subheader("📊 Visualization")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude="number").columns.tolist()

        if len(numeric_cols) == 0:
            st.info("No numeric columns available for visualization.")

        elif len(df) == 1:
            st.metric(
                label=numeric_cols[0],
                value=df[numeric_cols[0]].iloc[0]
            )

        else:
            if non_numeric_cols:
                x_col = non_numeric_cols[0]
            else:
                x_col = numeric_cols[0]

            y_col = numeric_cols[-1]

            chart_df = df.set_index(x_col)[y_col]
            st.bar_chart(chart_df)

    else:
        st.warning("⚠ No data returned")

