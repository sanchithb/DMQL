-- 10 recent bookings showing customer name and game name
SELECT
    b.booking_id,
    c.first_name || ' ' || c.last_name  AS customer_name,
    g.game_name,
    b.booking_date,
    b.num_players,
    b.status
FROM bookings b
JOIN customers c ON b.customer_id = c.customer_id
JOIN games    g ON b.game_id     = g.game_id
ORDER BY b.booking_date DESC
LIMIT 10;