-- Procedure: Cancel a booking by ID
CREATE OR REPLACE PROCEDURE cancel_booking(p_booking_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE bookings
    SET status = 'CANCELLED'
    WHERE booking_id = p_booking_id
      AND status = 'CONFIRMED';

    IF NOT FOUND THEN
        RAISE NOTICE 'No active booking found with ID: %', p_booking_id;
    ELSE
        RAISE NOTICE 'Booking % has been cancelled.', p_booking_id;
    END IF;
END;
$$;

-- How to call it:
-- CALL cancel_booking(802);