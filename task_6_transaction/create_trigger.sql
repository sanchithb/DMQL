-- trigger function
CREATE OR REPLACE FUNCTION handle_failed_payment()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- When a payment fails, automatically cancel the linked booking
    IF NEW.payment_status = 'FAILED' THEN
        UPDATE bookings
        SET status = 'CANCELLED'
        WHERE booking_id = NEW.booking_id;

        RAISE NOTICE 'Payment failed for booking %. Booking has been automatically cancelled.', NEW.booking_id;
    END IF;

    RETURN NEW;
END;
$$;

-- Attach the trigger to the payments table
CREATE OR REPLACE TRIGGER trg_failed_payment
AFTER INSERT OR UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION handle_failed_payment();