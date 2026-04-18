-- Find customers who spent more than the average payment amount
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    SUM(p.amount) AS total_spent
FROM customers c
JOIN bookings b  ON c.customer_id = b.customer_id
JOIN payments p  ON b.booking_id  = p.booking_id
WHERE p.payment_status = 'SUCCESS'
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
HAVING SUM(p.amount) > (
    SELECT AVG(amount)
    FROM payments
    WHERE payment_status = 'SUCCESS'
)
ORDER BY total_spent DESC;