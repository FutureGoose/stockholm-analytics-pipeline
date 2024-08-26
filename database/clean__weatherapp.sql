WITH weather_data AS
(SELECT modified_timestamp,
        JSON_EXTRACT_SCALAR(data, '$.time') AS temp_time,
        EXTRACT(HOUR FROM PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', CONCAT(JSON_EXTRACT_SCALAR(data, '$.time'), ':00'))) AS hour,
        EXTRACT(MONTH FROM PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', CONCAT(JSON_EXTRACT_SCALAR(data, '$.time'), ':00'))) AS month,
        CAST(JSON_EXTRACT_SCALAR(data, '$.humidity') AS FLOAT64) AS humidity,
        CAST(JSON_EXTRACT_SCALAR(data, '$.temp_c') AS FLOAT64) AS temp,
        CAST(JSON_EXTRACT_SCALAR(data, '$.pressure_mb') AS FLOAT64) AS pressure,
   FROM `team-god.weather_data.raw_weatherapp`
  WHERE 1=1
QUALIFY ROW_NUMBER() OVER (PARTITION BY temp_time ORDER BY modified_timestamp DESC) = 1 -- Gives only the most recent row for each unique temp_time
ORDER BY temp_time ASC)

SELECT temp_time,
       hour,
       month,
       temp,
       pressure,
       humidity,
       MAX(temp) OVER (
       ORDER BY temp_time
       ROWS BETWEEN 1 FOLLOWING AND 23 FOLLOWING
       ) AS temp_target, -- Returns max temp next 24 hours
       LAG(temp, 1) OVER (
       ORDER BY temp_time
       ) AS temp_lag_1, -- Returns temperature 1 hour ago 
       LAG(temp, 3) OVER (
       ORDER BY temp_time
       ) AS temp_lag_3 -- Returns temperature 3 hours ago
  FROM weather_data
ORDER BY temp_time DESC
LIMIT 24;


