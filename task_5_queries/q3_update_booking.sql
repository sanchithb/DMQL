-- Update a confirmed booking as completed
UPDATE bookings
SET status = 'COMPLETED'
WHERE booking_id = 5
  AND status = 'CONFIRMED';