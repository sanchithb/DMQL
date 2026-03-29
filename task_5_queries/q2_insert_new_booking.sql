-- Insert a booking for the customer added in q1 
INSERT INTO bookings (customer_id, booking_date, num_players, status, game_id)
VALUES (
    (SELECT customer_id FROM customers WHERE email = 'ishaq.test@gmail.com'),
    CURRENT_DATE + INTERVAL '7 days',
    4,
    'CONFIRMED',
    1
);