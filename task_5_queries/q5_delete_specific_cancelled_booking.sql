-- Delete a specific cancelled booking
DELETE FROM bookings
WHERE booking_id = 10
  AND status = 'CANCELLED';