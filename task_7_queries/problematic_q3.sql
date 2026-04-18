-- filtering on a timestamp column with no index
EXPLAIN ANALYZE
SELECT 
    gs.session_id,
    gs.start_time,
    gs.end_time,
    gs.success
FROM game_sessions gs
WHERE gs.start_time >= '2024-01-01'
  AND gs.start_time <  '2025-01-01';