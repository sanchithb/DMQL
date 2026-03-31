-- Procedure: Create a booking
CREATE OR REPLACE PROCEDURE make_booking(
    p_customer_id  INT,
    p_game_id      INT,
    p_date         DATE,
    p_num_players  INT,
    p_amount       NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_booking_id INT;
BEGIN
    -- Insert the booking
    INSERT INTO bookings (customer_id, game_id, booking_date, num_players, status)
    VALUES (p_customer_id, p_game_id, p_date, p_num_players, 'CONFIRMED')
    RETURNING booking_id INTO v_booking_id;

    -- Insert the payment record
    INSERT INTO payments (booking_id, amount, payment_method, payment_status)
    VALUES (v_booking_id, p_amount, 'Online', 'PENDING');

    RAISE NOTICE 'Booking created with ID: %', v_booking_id;
END;
$$;

-- How to call it
-- CALL make_booking(1, 2, CURRENT_DATE + 3, 3, 75.00);