-- Total revenue per game, sorted highest first
SELECT
    g.game_name,
    COUNT(p.payment_id) AS total_payments,
    SUM(p.amount) AS total_revenue,
    ROUND(AVG(p.amount), 2) AS avg_payment
FROM payments p
JOIN bookings b ON p.booking_id  = b.booking_id
JOIN games    g ON b.game_id     = g.game_id
WHERE p.payment_status = 'SUCCESS'
GROUP BY g.game_name
ORDER BY total_revenue DESC;