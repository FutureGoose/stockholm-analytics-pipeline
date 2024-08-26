WITH weather_data AS
(SELECT modified_timestamp,
        JSON_EXTRACT_SCALAR(data, '$.time') AS temp_time,
        EXTRACT(HOUR FROM PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', CONCAT(JSON_EXTRACT_SCALAR(data, '$.time'), ':00'))) AS hour,
        EXTRACT(MONTH FROM PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', CONCAT(JSON_EXTRACT_SCALAR(data, '$.time'), ':00'))) AS month,
        CAST(JSON_EXTRACT_SCALAR(data, '$.humidity') AS FLOAT64) AS humidity,
        CAST(JSON_EXTRACT_SCALAR(data, '$.temp_c') AS FLOAT64) AS temp,
        CAST(JSON_EXTRACT_SCALAR(data, '$.pressure_mb') AS FLOAT64) AS pressure,
   FROM `team-god.weather_data.raw_weatherapp`
  WHERE 1=1 -- Needed for qualify
QUALIFY ROW_NUMBER() OVER (PARTITION BY temp_time ORDER BY modified_timestamp DESC) = 1
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
       ) AS temp_target,
       LAG(temp, 1) OVER (
       ORDER BY temp_time
       ) AS temp_lag_1,
       LAG(temp, 3) OVER (
       ORDER BY temp_time
       ) AS temp_lag_3
  FROM weather_data
ORDER BY temp_time DESC
LIMIT 24;


