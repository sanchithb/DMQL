-- Games where players escape more than 50% of the time
SELECT
    g.game_name,
    g.difficulty_level,
    COUNT(gs.session_id) AS total_sessions,
    SUM(CASE WHEN gs.success = TRUE THEN 1 ELSE 0 END) AS successful_escapes,
    ROUND(
        100.0 * SUM(CASE WHEN gs.success = TRUE THEN 1 ELSE 0 END)
              / COUNT(gs.session_id), 1
    ) AS success_rate_pct
FROM game_sessions gs
JOIN games g ON gs.game_id = g.game_id
WHERE gs.success IS NOT NULL
GROUP BY g.game_id, g.game_name, g.difficulty_level
HAVING COUNT(gs.session_id) > 5
ORDER BY success_rate_pct DESC;