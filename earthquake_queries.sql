SHOW DATABASES;
USE seismic_project;
show tables;
select count(*) from earthquake;

-- ==============================
-- Magnitude & Depth
-- ==============================

-- 1. Top 10 strongest earthquakes
SELECT id, place, mag
FROM earthquake
ORDER BY mag DESC
LIMIT 10;

-- 2. Top 10 deepest earthquakes
SELECT *
FROM earthquake
ORDER BY depth_km DESC
LIMIT 10;

-- 3. Shallow earthquakes < 50 km and mag > 7.5.
SELECT id, place, mag, depth_km
FROM earthquake
WHERE depth_km < 50 AND mag > 7.5
ORDER BY mag DESC;

-- 5. Average magnitude per magnitude type 
SELECT magType,
       AVG(mag) AS average_magnitude
FROM earthquake
GROUP BY magType
ORDER BY average_magnitude DESC;

-- =====================
-- Time Analysis
-- =====================

-- 6. Year with most earthquakes
SELECT YEAR(time) AS year, COUNT(*) AS total
FROM earthquake
GROUP BY YEAR(time)
ORDER BY total DESC
LIMIT 1;

-- 7.  Month with the Highest Number of Earthquakes 
SELECT
    month,
    COUNT(*) AS earthquake_count
FROM earthquake
GROUP BY month
ORDER BY earthquake_count DESC
LIMIT 1;

-- 8. Day of week with most earthquakes
SELECT DAYNAME(time) AS day_of_week,
       COUNT(*) AS total_earthquakes
FROM earthquake
GROUP BY DAYNAME(time)
ORDER BY total_earthquakes DESC
LIMIT 1;

-- 9. Count of earthquakes per hour of day
SELECT HOUR(time) AS hour_of_day,
       COUNT(*) AS total_earthquakes
FROM earthquake
GROUP BY HOUR(time)
ORDER BY hour_of_day;


-- 10. Most active reporting network (net)
SELECT net,
       COUNT(*) AS total_reports
FROM earthquake
GROUP BY net
ORDER BY total_reports DESC
LIMIT 1;

-- =================================
-- Casualties & Economic Loss
-- =================================

-- 11. Top 5 places with highest casualties.
SELECT 
    place, 
    mag, 
    sig as impact_score, 
    country
FROM earthquake
ORDER BY sig DESC 
LIMIT 5;

-- 13. Average economic loss by alert level.
SELECT 
    CASE 
        WHEN mag >= 7.0 THEN 'Red (High Alert)'
        WHEN mag >= 5.5 THEN 'Orange (Moderate)'
        WHEN mag >= 4.0 THEN 'Yellow (Low)'
        ELSE 'Green (Minor)'
    END AS derived_alert_level,
    
    AVG(sig) AS average_impact_score
FROM earthquake
GROUP BY derived_alert_level
ORDER BY average_impact_score DESC;

-- ===============================
-- Event Type & Quality Metrics
-- ===============================

-- 14. Count of reviewed vs automatic earthquakes
SELECT status, COUNT(*) AS total_events
FROM earthquake
GROUP BY status; 

-- 15.  Count by earthquake type
SELECT type, COUNT(*) AS total_events
FROM earthquake
GROUP BY type
ORDER BY total_events DESC;  

-- 16. Number of earthquakes by 'types' column
SELECT types, COUNT(*) AS total_events
FROM earthquake
GROUP BY types
ORDER BY total_events DESC; 

-- 18. Events with high station coverage (nst > threshold)
SELECT id, place, mag, nst, time
FROM earthquake
WHERE nst > 50
ORDER BY nst DESC;

-- ==============================
-- Tsunamis & Alerts
-- ==============================
 
-- 19. Number of tsunamis triggered per year
SELECT YEAR(time) AS year,
       COUNT(*) AS tsunami_count
FROM earthquake
WHERE tsunami = 1
GROUP BY YEAR(time)
ORDER BY year; 

-- 20. Count earthquakes by derived alert levels (using magnitude)
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

-- ==========================================
-- Seismic Pattern & Trends Analysis
-- ==========================================

-- 21. top 5 countries with the highest average magnitude of earthquakes in the past 5 years
SELECT 
    country, 
    AVG(mag) AS average_magnitude,
    COUNT(*) AS quake_count
FROM earthquake
WHERE time >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)   -- 5-year filter
GROUP BY country
HAVING quake_count > 5
ORDER BY average_magnitude DESC
LIMIT 5;

-- 22. countries that have experienced both shallow and deep earthquakes within the same month
SELECT 
    country,
    YEAR(time) AS year,
    MONTH(time) AS month
FROM earthquake
GROUP BY country, YEAR(time), MONTH(time)
HAVING 
    SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) > 0   -- shallow present
    AND
    SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) > 0; -- deep present
    
-- 23. year-over-year growth rate in the total number of earthquakes.
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

-- 24. the 3 most seismically active regions by combining both frequency and average magnitude
SELECT 
    country, 
    COUNT(*) AS frequency, 
    ROUND(AVG(mag),2) AS avg_magnitude,
    ROUND(COUNT(*) * AVG(mag),2) AS seismic_activity_score
FROM earthquake
GROUP BY country
ORDER BY seismic_activity_score DESC
LIMIT 3;

-- ============================================
-- Depth, Location & Distance-Based  Analysis
-- ============================================

-- 25.Average depth for each country within ±5° latitude of the equator
SELECT country,
       AVG(depth_km) AS avg_depth
FROM earthquake
WHERE latitude BETWEEN -5 AND 5
GROUP BY country
ORDER BY avg_depth;

-- 26. Countries with the highest shallow-to-deep earthquake ratio
SELECT country,
       SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_quakes,
       SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep_quakes,
       SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) /
       NULLIF(SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END), 0) AS shallow_deep_ratio
FROM earthquake
GROUP BY country
ORDER BY shallow_deep_ratio DESC;

-- 27. Difference in average magnitude between tsunami and non-tsunami events
SELECT 
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) 
      AS avg_mag_tsunami,
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0)
      AS avg_mag_no_tsunami,
    ( (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) -
      (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) )
      AS magnitude_difference;

-- 28. Events with lowest data reliability (highest gap and rms)
SELECT id, place, mag, depth_km, gap, rms, time
FROM earthquake
WHERE gap IS NOT NULL AND rms IS NOT NULL
ORDER BY gap DESC, rms DESC
LIMIT 20;

-- 30. Deep-focus earthquakes (>300 km) grouped by country (treated as region)
SELECT country AS region,
       COUNT(*) AS deep_focus_quakes
FROM earthquake
WHERE depth_km > 300
GROUP BY country
ORDER BY deep_focus_quakes DESC;






