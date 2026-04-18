-- searching bookings by customer with no index
EXPLAIN ANALYZE
SELECT b.booking_id, b.booking_date, b.status, b.num_players
FROM bookings b
WHERE b.customer_id = 42;