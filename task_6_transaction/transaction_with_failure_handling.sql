-- create the booking 
INSERT INTO bookings (customer_id, game_id, booking_date, num_players, status)
VALUES (3, 1, CURRENT_DATE + 7, 4, 'CONFIRMED');

-- Transaction with failure handling
DO $$
DECLARE
    v_booking_id INT;
BEGIN
   
    SELECT MAX(booking_id) INTO v_booking_id FROM bookings;
    
    RAISE NOTICE 'Processing booking ID: %', v_booking_id;

    -- Attempt to create session with invalid room
    INSERT INTO game_sessions (booking_id, game_id, room_id, start_time, end_time)
    VALUES (
        v_booking_id,
        1,
        9999,   -- invalid room, causes failure
        NOW() + INTERVAL '7 days',
        NOW() + INTERVAL '7 days' + INTERVAL '60 minutes'
    );

    -- Payment on success (never reached)
    INSERT INTO payments (booking_id, amount, payment_method, payment_status)
    VALUES (v_booking_id, 85.00, 'Card', 'SUCCESS');

    RAISE NOTICE 'Transaction completed successfully!';

EXCEPTION
    WHEN OTHERS THEN
        -- Failure caught — log failed payment which fires the trigger
        RAISE NOTICE 'Transaction failed: %', SQLERRM;
        RAISE NOTICE 'Logging failed payment — trigger will cancel the booking...';

        INSERT INTO payments (booking_id, amount, payment_method, payment_status)
        VALUES (v_booking_id, 85.00, 'Card', 'FAILED');
        -- trigger fires here → booking automatically set to CANCELLED

END;
$$;

-- Verify results
SELECT
    b.booking_id,
    b.status        AS booking_status,
    p.payment_status,
    p.amount
FROM bookings b
JOIN payments p ON b.booking_id = p.booking_id
ORDER BY b.booking_id DESC
LIMIT 1;