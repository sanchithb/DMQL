EXPLAIN ANALYZE
SELECT 
    b.booking_id,
    b.booking_date,
    c.first_name || ' ' || c.last_name AS customer_name,
    g.game_name
FROM bookings b
JOIN customers c ON b.customer_id = c.customer_id
JOIN games g ON b.game_id = g.game_id;