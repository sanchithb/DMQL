-- Give all GameMasters a 10% raise
UPDATE employees
SET hourly_rate = ROUND(hourly_rate * 1.10, 2)
WHERE role = 'GameMaster';