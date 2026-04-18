-- Function: Return all bookings for a given customer
CREATE OR REPLACE FUNCTION get_customer_history(p_customer_id INT)
RETURNS TABLE (
    booking_id    INT,
    game_name     TEXT,
    booking_date  DATE,
    num_players   INT,
    status        TEXT,
    amount_paid   NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.booking_id,
        g.game_name,
        b.booking_date,
        b.num_players,
        b.status,
        COALESCE(p.amount, 0)
    FROM bookings b
    JOIN games    g ON b.game_id    = g.game_id
    LEFT JOIN payments p ON b.booking_id = p.booking_id
                         AND p.payment_status = 'SUCCESS'
    WHERE b.customer_id = p_customer_id
    ORDER BY b.booking_date DESC;
END;
$$;

-- How to call it:
SELECT * FROM get_customer_history(1);