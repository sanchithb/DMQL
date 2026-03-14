import argparse
import csv
import os
import random
from datetime import datetime, timedelta, date
from collections import defaultdict

try:
    from faker import Faker
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False

SEED = 42
random.seed(SEED)

if HAS_FAKER:
    fake = Faker()
    Faker.seed(SEED)

NUM_CUSTOMERS = 500
NUM_EMPLOYEES = 30
NUM_GAMES = 15
NUM_ROOMS = 20
NUM_BOOKINGS = 800
NUM_GAME_SESSIONS = 700
NUM_CLUES_PER_GAME = 5
NUM_SESSION_CLUES = 500
NUM_PAYMENTS = 800
NUM_SALARY_MONTHS = 4
NUM_EMPLOYEE_LEAVES = 40

BUSINESS_START = date(2024, 1, 1)
BUSINESS_END = date(2025, 12, 31)
DATA_GENERATION_DATE = date(2026, 3, 1) 

ROLES = ['GameMaster', 'Manager', 'Admin']
ROLE_WEIGHTS = [0.7, 0.2, 0.1]

GAME_NAMES = [
    "The Haunted Mansion", "Prison Break", "The Lost Temple",
    "Zombie Apocalypse", "The Mad Scientist", "Pirate's Cove",
    "The Bank Heist", "Alien Encounter", "The Enchanted Forest",
    "Sherlock's Study", "The Submarine", "Nightmare Asylum",
    "The Time Machine", "Cyber Attack", "The Pharaoh's Tomb"
]

ROOM_NAMES = [
    "Chamber A", "Chamber B", "Vault 1", "Vault 2", "Dungeon East",
    "Dungeon West", "Lab Alpha", "Lab Beta", "Deck One", "Deck Two",
    "Tower North", "Tower South", "Cellar", "Attic", "Gallery",
    "Bunker", "Observatory", "Crypt", "Greenhouse", "Archive"
]

BOOKING_STATUSES = ['CONFIRMED', 'CANCELLED', 'COMPLETED']
PAYMENT_METHODS = ['Card', 'Cash', 'Online']
PAYMENT_STATUSES = ['SUCCESS', 'FAILED', 'PENDING']

LEAVE_REASONS = [
    "Vacation", "Sick leave", "Family emergency", "Personal day",
    "Medical appointment", "Moving", "Wedding", "Bereavement",
    "Jury duty", "Mental health day", None
]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_datetime(start: date, end: date) -> datetime:
    d = random_date(start, end)
    hour = random.randint(9, 21)
    minute = random.choice([0, 15, 30, 45])
    return datetime(d.year, d.month, d.day, hour, minute, 0)


def generate_email(first_name: str, last_name: str, index: int) -> str:
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
    base = f"{first_name.lower()}.{last_name.lower()}"
    if index > 0:
        base += str(index)
    return f"{base}@{random.choice(domains)}"


def generate_phone() -> str:
    if random.random() < 0.15:
        return None
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"


def generate_clue_text(game_name: str, clue_num: int) -> str:
    clue_templates = [
        f"Look behind the painting on the north wall",
        f"The combination is hidden in the book on the shelf",
        f"Check under the carpet near the door",
        f"The key is inside the hollow statue",
        f"Decode the message written in UV ink on the map",
        f"The password is the year on the oldest photograph",
        f"Push the third brick from the left on the fireplace",
        f"The answer is written backwards on the mirror",
        f"Connect the colored wires in rainbow order",
        f"The final digit is the number of candles in the room",
        f"Rotate the globe to South America for the next clue",
        f"The morse code on the wall spells the exit code",
        f"Lift the floorboard under the rocking chair",
        f"The clock hands point to the locker combination",
        f"Arrange the chess pieces to match the painting",
    ]
    return random.choice(clue_templates)

def generate_all_data():
   
    data = {}

    customers = []
    used_emails = set()
    for i in range(1, NUM_CUSTOMERS + 1):
        if HAS_FAKER:
            first_name = fake.first_name()
            last_name = fake.last_name()
        else:
            first_name = f"FirstName{i}"
            last_name = f"LastName{i}"
        
        email = generate_email(first_name, last_name, i)
        while email in used_emails:
            email = generate_email(first_name, last_name, i + random.randint(1000, 9999))
        used_emails.add(email)
        
        phone = generate_phone()
        created_at = random_datetime(BUSINESS_START, BUSINESS_END)
        
        customers.append({
            'customer_id': i,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    data['customers'] = customers
    
    employees = []
    for i in range(1, NUM_EMPLOYEES + 1):
        if HAS_FAKER:
            name = fake.name()
        else:
            name = f"Employee {i}"
        
        role = random.choices(ROLES, weights=ROLE_WEIGHTS, k=1)[0]

        if role == 'Admin':
            hourly_rate = round(random.uniform(30.0, 50.0), 2)
        elif role == 'Manager':
            hourly_rate = round(random.uniform(25.0, 40.0), 2)
        else:  # GameMaster
            hourly_rate = round(random.uniform(15.0, 28.0), 2)
        
        hire_date = random_date(date(2022, 1, 1), date(2025, 6, 30))
        
        employees.append({
            'employee_id': i,
            'name': name,
            'role': role,
            'hourly_rate': hourly_rate,
            'hire_date': hire_date.strftime('%Y-%m-%d')
        })
    data['employees'] = employees

    games = []
    for i in range(1, NUM_GAMES + 1):
        games.append({
            'game_id': i,
            'game_name': GAME_NAMES[i - 1],
            'difficulty_level': random.randint(1, 5), 
            'duration_minutes': random.choice([30, 45, 60, 75, 90]),
            'max_players': random.randint(2, 8)      
        })
    data['games'] = games
    
    rooms = []
    for i in range(1, NUM_ROOMS + 1):
        rooms.append({
            'room_id': i,
            'room_name': ROOM_NAMES[i - 1],
            'capacity': random.randint(2, 10),
            'game_id': random.randint(1, NUM_GAMES) 
        })
    data['rooms'] = rooms
    
    bookings = []
    
    repeat_customers = random.sample(range(1, NUM_CUSTOMERS + 1), k=100)
    
    for i in range(1, NUM_BOOKINGS + 1):

        if random.random() < 0.3 and repeat_customers:
            customer_id = random.choice(repeat_customers)
        else:
            customer_id = random.randint(1, NUM_CUSTOMERS)
        
        booking_date = random_date(BUSINESS_START, BUSINESS_END)
        game_id = random.randint(1, NUM_GAMES)
        game_max = games[game_id - 1]['max_players']
        num_players = random.randint(1, game_max)

        if booking_date < date(2025, 11, 1):
            status = random.choices(
                BOOKING_STATUSES,
                weights=[0.05, 0.15, 0.80],
                k=1
            )[0]
        else:
            status = random.choices(
                BOOKING_STATUSES,
                weights=[0.50, 0.15, 0.35], 
                k=1
            )[0]
        
        bookings.append({
            'booking_id': i,
            'customer_id': customer_id,
            'booking_date': booking_date.strftime('%Y-%m-%d'),
            'num_players': num_players,
            'status': status,
            'game_id': game_id
        })
    data['bookings'] = bookings
    
    print("Generating Game Sessions...")
    game_sessions = []

    eligible_bookings = [
        b for b in bookings 
        if b['status'] in ('COMPLETED', 'CONFIRMED')
    ]
    random.shuffle(eligible_bookings)
    session_bookings = eligible_bookings[:NUM_GAME_SESSIONS]
    
    used_booking_ids = set()
    session_id = 0
    for b in session_bookings:
        if b['booking_id'] in used_booking_ids:
            continue
        used_booking_ids.add(b['booking_id'])
        
        session_id += 1
        game_id = b['game_id']
        game_duration = games[game_id - 1]['duration_minutes']

        matching_rooms = [r for r in rooms if r['game_id'] == game_id]
        if matching_rooms:
            room = random.choice(matching_rooms)
        else:
            room = random.choice(rooms)
        
        booking_dt = datetime.strptime(b['booking_date'], '%Y-%m-%d')
        start_hour = random.randint(9, 20)
        start_time = booking_dt.replace(hour=start_hour, minute=random.choice([0, 15, 30, 45]))

        actual_duration = game_duration + random.randint(-10, 15)
        actual_duration = max(10, actual_duration)
        end_time = start_time + timedelta(minutes=actual_duration) 

        if b['status'] == 'COMPLETED':
            success = random.choice([True, False])
        else:
            success = None  
        
        game_sessions.append({
            'session_id': session_id,
            'booking_id': b['booking_id'],
            'game_id': game_id,
            'room_id': room['room_id'],
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': success
        })
        
        if session_id >= NUM_GAME_SESSIONS:
            break
    
    data['game_sessions'] = game_sessions
    
    session_employees = []
    
    gamemaster_ids = [e['employee_id'] for e in employees if e['role'] == 'GameMaster']
    all_employee_ids = [e['employee_id'] for e in employees]
    
    used_pairs = set()
    for session in game_sessions:
        num_assigned = random.choices([1, 2], weights=[0.6, 0.4], k=1)[0]
        
        gm = random.choice(gamemaster_ids)
        pair = (session['session_id'], gm)
        if pair not in used_pairs:
            used_pairs.add(pair)
            session_employees.append({
                'session_id': session['session_id'],
                'employee_id': gm
            })
        
        if num_assigned == 2:
            second = random.choice(all_employee_ids)
            pair2 = (session['session_id'], second)
            if pair2 not in used_pairs:
                used_pairs.add(pair2)
                session_employees.append({
                    'session_id': session['session_id'],
                    'employee_id': second
                })
    
    data['session_employees'] = session_employees
    
    clues = []
    clue_id = 0
    for game in games:
        num_clues = random.randint(4, 6)
        for c in range(num_clues):
            clue_id += 1
            clues.append({
                'clue_id': clue_id,
                'game_id': game['game_id'],
                'clue_text': generate_clue_text(game['game_name'], c),
                'time_penalty': random.choice([0, 1, 2, 3, 5, 5, 10])
            })
    data['clues'] = clues
    
    game_clues = defaultdict(list)
    for clue in clues:
        game_clues[clue['game_id']].append(clue['clue_id'])
    
    session_clues = []
    used_session_clue_pairs = set()
    
    for session in game_sessions:
        available_clues = game_clues.get(session['game_id'], [])
        if not available_clues:
            continue
        
        num_used = random.choices([0, 1, 2, 3], weights=[0.3, 0.3, 0.25, 0.15], k=1)[0]
        num_used = min(num_used, len(available_clues))
        
        selected_clues = random.sample(available_clues, num_used)
        
        session_start = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
        session_end = datetime.strptime(session['end_time'], '%Y-%m-%d %H:%M:%S')
        
        for clue_id_val in selected_clues:
            pair = (session['session_id'], clue_id_val)
            if pair in used_session_clue_pairs:
                continue
            used_session_clue_pairs.add(pair)

            if random.random() < 0.9:
                offset_minutes = random.randint(5, max(6, int((session_end - session_start).total_seconds() / 60) - 5))
                used_at = session_start + timedelta(minutes=offset_minutes)
                used_at_str = used_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                used_at_str = None  
            
            session_clues.append({
                'session_id': session['session_id'],
                'clue_id': clue_id_val,
                'used_at': used_at_str
            })
    
    if len(session_clues) > NUM_SESSION_CLUES:
        session_clues = session_clues[:NUM_SESSION_CLUES]
    
    data['session_clues'] = session_clues

    payments = []

    game_prices = {}
    for game in games:
        base = 20 + (game['difficulty_level'] * 5) + (game['duration_minutes'] * 0.3)
        game_prices[game['game_id']] = round(base, 2)
    
    for i in range(1, NUM_PAYMENTS + 1):
        booking = bookings[i - 1] if i <= len(bookings) else random.choice(bookings)
        
        game_id = booking['game_id']
        num_players = booking['num_players']
        per_player_price = game_prices.get(game_id, 35.0)
        amount = round(per_player_price * num_players, 2) 
        amount = max(5.0, amount) 
        
        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=[0.50, 0.15, 0.35],
            k=1
        )[0]

        if booking['status'] == 'CANCELLED':
            payment_status = random.choices(
                PAYMENT_STATUSES,
                weights=[0.2, 0.5, 0.3],
                k=1
            )[0]
        elif booking['status'] == 'COMPLETED':
            payment_status = random.choices(
                PAYMENT_STATUSES,
                weights=[0.90, 0.05, 0.05],
                k=1
            )[0]
        else: 
            payment_status = random.choices(
                PAYMENT_STATUSES,
                weights=[0.60, 0.10, 0.30],
                k=1
            )[0]
        
        booking_dt = datetime.strptime(booking['booking_date'], '%Y-%m-%d')
        
        payment_offset = random.randint(0, 3)
        payment_time = booking_dt - timedelta(days=payment_offset)
        payment_time = payment_time.replace(
            hour=random.randint(8, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        payments.append({
            'payment_id': i,
            'booking_id': booking['booking_id'],
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'payment_time': payment_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    data['payments'] = payments
    
    salaries = []
    salary_id = 0
    salary_months = [
        date(2025, 9, 1), date(2025, 10, 1),
        date(2025, 11, 1), date(2025, 12, 1)
    ]
    
    used_salary_pairs = set()
    for emp in employees:
        for month in salary_months:
            pair = (emp['employee_id'], month.strftime('%Y-%m-%d'))
            if pair in used_salary_pairs:
                continue
            used_salary_pairs.add(pair)
            
            salary_id += 1
            total_hours = random.randint(80, 200)
            total_pay = round(total_hours * emp['hourly_rate'], 2)
            
            salaries.append({
                'salary_id': salary_id,
                'employee_id': emp['employee_id'],
                'month': month.strftime('%Y-%m-%d'),
                'total_hours': total_hours,
                'total_pay': total_pay
            })
    data['salaries'] = salaries
    
    print("Generating Employee Leaves...")
    employee_leaves = []
    for i in range(1, NUM_EMPLOYEE_LEAVES + 1):
        emp_id = random.randint(1, NUM_EMPLOYEES)
        start = random_date(date(2025, 1, 1), date(2025, 12, 15))
        duration = random.randint(1, 7)
        end = start + timedelta(days=duration)
        reason = random.choice(LEAVE_REASONS)
        
        employee_leaves.append({
            'leave_id': i,
            'employee_id': emp_id,
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'reason': reason
        })
    data['employee_leaves'] = employee_leaves
    
    return data

def sql_value(val):

    if val is None:
        return 'NULL'
    elif isinstance(val, bool):
        return 'TRUE' if val else 'FALSE'
    elif isinstance(val, (int, float)):
        return str(val)
    else:
        escaped = str(val).replace("'", "''")
        return f"'{escaped}'"


def export_sql(data, output_file='insert_data.sql'):

    table_order = [
        'customers', 'employees', 'games', 'rooms', 'bookings',
        'game_sessions', 'session_employees', 'clues', 'session_clues',
        'payments', 'salaries', 'employee_leaves'
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for table_name in table_order:
            records = data.get(table_name, [])
            if not records:
                continue
            
            f.write(f"-- {table_name} ({len(records)} rows)\n")
            
            columns = list(records[0].keys())
            col_str = ', '.join(columns)

            batch_size = 100
            for batch_start in range(0, len(records), batch_size):
                batch = records[batch_start:batch_start + batch_size]
                f.write(f"INSERT INTO {table_name} ({col_str}) VALUES\n")
                
                value_rows = []
                for record in batch:
                    vals = ', '.join(sql_value(record[col]) for col in columns)
                    value_rows.append(f"  ({vals})")
                
                f.write(',\n'.join(value_rows))
                f.write(';\n\n')
        
        f.write("Reset sequences to max ID + 1")
        sequence_tables = [
            ('customers', 'customer_id'),
            ('employees', 'employee_id'),
            ('games', 'game_id'),
            ('rooms', 'room_id'),
            ('bookings', 'booking_id'),
            ('game_sessions', 'session_id'),
            ('clues', 'clue_id'),
            ('payments', 'payment_id'),
            ('salaries', 'salary_id'),
            ('employee_leaves', 'leave_id'),
        ]
        for table, pk in sequence_tables:
            f.write(f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), "
                    f"(SELECT MAX({pk}) FROM {table}));\n")
    
    print(f"{output_file} generated")

def print_summary(data):
    total = 0
    print("\n" + "=" * 50)
    print("  DATA GENERATION SUMMARY")
    print("=" * 50)
    for table_name, records in data.items():
        count = len(records)
        total += count
        print(f"  {table_name:<25} {count:>6} rows")
    print("-" * 50)
    print(f"  {'TOTAL':<25} {total:>6} rows")
    print("=" * 50)
    
    if total >= 3000:
        print(f"Meets minimum 3,000 record requirement ({total} records)")
    else:
        print(f"Below 3,000 record minimum ({total} records)")

def main():
    parser = argparse.ArgumentParser(description='Generate Escape Room ERP data')
    parser.add_argument('--sql', action='store_true', help='Export as SQL INSERT file')
    parser.add_argument('--sql-file', default='insert_data.sql', help='SQL output file')
    
    args = parser.parse_args()

    if not HAS_FAKER:
        print("faker library not installed. Using basic name generation.")

    print("Generating Escape Room ERP data")
    data = generate_all_data()
    
    print_summary(data)
    
    if args.sql:
        print(f"Exporting SQL file to '{args.sql_file}'")
        export_sql(data, args.sql_file)
    
    print("Data generation complete.")
    
if __name__ == '__main__':
    main()
