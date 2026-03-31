-- Sessions with employee names, game, and room, multiple Join query
SELECT
    gs.session_id,
    g.game_name,
    r.room_name,
    gs.start_time,
    gs.success,
    STRING_AGG(e.name, ', ')  AS assigned_staff
FROM game_sessions gs
JOIN games             g  ON gs.game_id    = g.game_id
JOIN rooms             r  ON gs.room_id    = r.room_id
JOIN session_employees se ON gs.session_id = se.session_id
JOIN employees         e  ON se.employee_id = e.employee_id
GROUP BY gs.session_id, g.game_name, r.room_name, gs.start_time, gs.success
ORDER BY gs.start_time DESC
LIMIT 15;