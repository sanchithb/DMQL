-- using a subquery inside SELECT instead of a JOIN
EXPLAIN ANALYZE
SELECT 
    b.booking_id,
    b.booking_date,
    (SELECT c.first_name || ' ' || c.last_name 
     FROM customers c 
     WHERE c.customer_id = b.customer_id) AS customer_name,
    (SELECT g.game_name 
     FROM games g 
     WHERE g.game_id = b.game_id) AS game_name
FROM bookings b;