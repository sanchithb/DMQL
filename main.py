"""
Escape Room ERP - FastAPI Backend
CSE 4/560 – DMQL Project
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import psycopg2.extras
from typing import Optional, List
import os
from datetime import datetime, date
from pydantic import BaseModel


app = FastAPI(title="Escape Room ERP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DB Connection ───────────────────────────────────────────────────────────

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "escape_room_erp",
    "user": "postgres",
    "password": "Sanchith@11",
}


def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn


def query(sql: str, params=None, fetchall=True):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetchall:
                result = cur.fetchall()
            else:
                result = cur.fetchone()
            conn.commit()
            return [dict(r) for r in result] if fetchall else (dict(result) if result else None)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute(sql: str, params=None):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            conn.commit()
            try:
                return dict(cur.fetchone())
            except:
                return {"affected": cur.rowcount}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# ─── Pydantic Models ──────────────────────────────────────────────────────────


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployeeCreate(BaseModel):
    name: str
    role: str
    hourly_rate: float
    hire_date: str


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    hourly_rate: Optional[float] = None


class GameCreate(BaseModel):
    game_name: str
    difficulty_level: int
    duration_minutes: int
    max_players: int


class RoomCreate(BaseModel):
    room_name: str
    capacity: int
    game_id: int


class BookingCreate(BaseModel):
    customer_id: int
    booking_date: str
    num_players: int
    game_id: int


class BookingStatusUpdate(BaseModel):
    status: str


class SessionCreate(BaseModel):
    booking_id: int
    game_id: int
    room_id: int
    start_time: str
    end_time: str
    success: Optional[bool] = None


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_method: str
    payment_status: str


class ClueCreate(BaseModel):
    game_id: int
    clue_text: str
    time_penalty: int


class SalaryCreate(BaseModel):
    employee_id: int
    month: str
    total_hours: int


class LeaveCreate(BaseModel):
    employee_id: int
    start_date: str
    end_date: str
    reason: Optional[str] = None


class CustomQuery(BaseModel):
    sql: str

# ─── Health ──────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}

# ─── CUSTOMERS ───────────────────────────────────────────────────────────────


@app.get("/customers")
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = "customer_id",
    order: str = "asc"
):
    offset = (page - 1) * limit
    where = ""
    params = []
    if search:
        where = "WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s"
        params = [f"%{search}%", f"%{search}%", f"%{search}%"]

    allowed_sorts = ["customer_id", "first_name",
                     "last_name", "email", "created_at"]
    sort_col = sort_by if sort_by in allowed_sorts else "customer_id"
    order_dir = "DESC" if order.lower() == "desc" else "ASC"

    total = query(
        f"SELECT COUNT(*) as cnt FROM customers {where}", params or None, fetchall=False)
    rows = query(
        f"SELECT * FROM customers {where} ORDER BY {sort_col} {order_dir} LIMIT %s OFFSET %s",
        (params or []) + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    row = query("SELECT * FROM customers WHERE customer_id = %s",
                [customer_id], fetchall=False)
    if not row:
        raise HTTPException(404, "Customer not found")
    return row


@app.post("/customers", status_code=201)
def create_customer(c: CustomerCreate):
    return execute(
        "INSERT INTO customers (first_name, last_name, email, phone, created_at) VALUES (%s,%s,%s,%s,NOW()) RETURNING *",
        [c.first_name, c.last_name, c.email, c.phone]
    )


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, c: CustomerUpdate):
    fields = {k: v for k, v in c.dict().items() if v is not None}
    if not fields:
        raise HTTPException(400, "No fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    return execute(
        f"UPDATE customers SET {set_clause} WHERE customer_id = %s RETURNING *",
        list(fields.values()) + [customer_id]
    )


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    return execute("DELETE FROM customers WHERE customer_id = %s", [customer_id])

# ─── EMPLOYEES ───────────────────────────────────────────────────────────────


@app.get("/employees")
def list_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None
):
    offset = (page - 1) * limit
    conditions, params = [], []
    if search:
        conditions.append("name ILIKE %s")
        params.append(f"%{search}%")
    if role:
        conditions.append("role = %s")
        params.append(role)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = query(
        f"SELECT COUNT(*) as cnt FROM employees {where}", params or None, fetchall=False)
    rows = query(
        f"SELECT * FROM employees {where} ORDER BY employee_id ASC LIMIT %s OFFSET %s",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    row = query("SELECT * FROM employees WHERE employee_id = %s",
                [employee_id], fetchall=False)
    if not row:
        raise HTTPException(404, "Employee not found")
    return row


@app.post("/employees", status_code=201)
def create_employee(e: EmployeeCreate):
    return execute(
        "INSERT INTO employees (name, role, hourly_rate, hire_date) VALUES (%s,%s,%s,%s) RETURNING *",
        [e.name, e.role, e.hourly_rate, e.hire_date]
    )


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, e: EmployeeUpdate):
    fields = {k: v for k, v in e.dict().items() if v is not None}
    if not fields:
        raise HTTPException(400, "No fields to update")
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    return execute(
        f"UPDATE employees SET {set_clause} WHERE employee_id = %s RETURNING *",
        list(fields.values()) + [employee_id]
    )


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    return execute("DELETE FROM employees WHERE employee_id = %s", [employee_id])

# ─── GAMES ───────────────────────────────────────────────────────────────────


@app.get("/games")
def list_games(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    difficulty: Optional[int] = None
):
    offset = (page - 1) * limit
    where, params = "", []
    if difficulty:
        where = "WHERE difficulty_level = %s"
        params = [difficulty]
    total = query(
        f"SELECT COUNT(*) as cnt FROM games {where}", params or None, fetchall=False)
    rows = query(
        f"SELECT * FROM games {where} ORDER BY game_id ASC LIMIT %s OFFSET %s",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/games", status_code=201)
def create_game(g: GameCreate):
    return execute(
        "INSERT INTO games (game_name, difficulty_level, duration_minutes, max_players) VALUES (%s,%s,%s,%s) RETURNING *",
        [g.game_name, g.difficulty_level, g.duration_minutes, g.max_players]
    )


@app.put("/games/{game_id}")
def update_game(game_id: int, g: GameCreate):
    return execute(
        "UPDATE games SET game_name=%s, difficulty_level=%s, duration_minutes=%s, max_players=%s WHERE game_id=%s RETURNING *",
        [g.game_name, g.difficulty_level, g.duration_minutes, g.max_players, game_id]
    )


@app.delete("/games/{game_id}")
def delete_game(game_id: int):
    return execute("DELETE FROM games WHERE game_id = %s", [game_id])

# ─── ROOMS ───────────────────────────────────────────────────────────────────


@app.get("/rooms")
def list_rooms(page: int = Query(1, ge=1), limit: int = Query(20)):
    offset = (page - 1) * limit
    total = query("SELECT COUNT(*) as cnt FROM rooms", fetchall=False)
    rows = query(
        "SELECT r.*, g.game_name FROM rooms r JOIN games g ON r.game_id = g.game_id ORDER BY r.room_id LIMIT %s OFFSET %s",
        [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/rooms", status_code=201)
def create_room(r: RoomCreate):
    return execute(
        "INSERT INTO rooms (room_name, capacity, game_id) VALUES (%s,%s,%s) RETURNING *",
        [r.room_name, r.capacity, r.game_id]
    )


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    return execute("DELETE FROM rooms WHERE room_id = %s", [room_id])

# ─── BOOKINGS ────────────────────────────────────────────────────────────────


@app.get("/bookings")
def list_bookings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    game_id: Optional[int] = None
):
    offset = (page - 1) * limit
    conditions, params = [], []
    if status:
        conditions.append("b.status = %s")
        params.append(status)
    if customer_id:
        conditions.append("b.customer_id = %s")
        params.append(customer_id)
    if from_date:
        conditions.append("b.booking_date >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("b.booking_date <= %s")
        params.append(to_date)
    if game_id:
        conditions.append("b.game_id = %s")
        params.append(game_id)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = query(
        f"SELECT COUNT(*) as cnt FROM bookings b {where}", params or None, fetchall=False
    )
    rows = query(
        f"""SELECT b.*, c.first_name || ' ' || c.last_name AS customer_name,
               g.game_name
        FROM bookings b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN games g ON b.game_id = g.game_id
        {where}
        ORDER BY b.booking_date DESC LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    row = query(
        """SELECT b.*, c.first_name || ' ' || c.last_name AS customer_name, g.game_name
           FROM bookings b
           JOIN customers c ON b.customer_id = c.customer_id
           JOIN games g ON b.game_id = g.game_id
           WHERE b.booking_id = %s""",
        [booking_id], fetchall=False
    )
    if not row:
        raise HTTPException(404, "Booking not found")
    return row


@app.post("/bookings", status_code=201)
def create_booking(b: BookingCreate):
    return execute(
        "INSERT INTO bookings (customer_id, booking_date, num_players, status, game_id) VALUES (%s,%s,%s,'CONFIRMED',%s) RETURNING *",
        [b.customer_id, b.booking_date, b.num_players, b.game_id]
    )


@app.patch("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, body: BookingStatusUpdate):
    allowed = ["CONFIRMED", "CANCELLED", "COMPLETED"]
    if body.status not in allowed:
        raise HTTPException(400, f"Status must be one of {allowed}")
    return execute(
        "UPDATE bookings SET status = %s WHERE booking_id = %s RETURNING *",
        [body.status, booking_id]
    )


@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    return execute("DELETE FROM bookings WHERE booking_id = %s", [booking_id])

# ─── SESSIONS ────────────────────────────────────────────────────────────────


@app.get("/sessions")
def list_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    game_id: Optional[int] = None,
    success: Optional[bool] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    offset = (page - 1) * limit
    conditions, params = [], []
    if game_id:
        conditions.append("gs.game_id = %s")
        params.append(game_id)
    if success is not None:
        conditions.append("gs.success = %s")
        params.append(success)
    if from_date:
        conditions.append("gs.start_time >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("gs.start_time <= %s")
        params.append(to_date)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = query(
        f"SELECT COUNT(*) as cnt FROM game_sessions gs {where}", params or None, fetchall=False)
    rows = query(
        f"""SELECT gs.*, g.game_name, r.room_name,
               EXTRACT(EPOCH FROM (gs.end_time - gs.start_time))/60 AS duration_actual_minutes
        FROM game_sessions gs
        JOIN games g ON gs.game_id = g.game_id
        JOIN rooms r ON gs.room_id = r.room_id
        {where}
        ORDER BY gs.start_time DESC LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/sessions", status_code=201)
def create_session(s: SessionCreate):
    return execute(
        "INSERT INTO game_sessions (booking_id, game_id, room_id, start_time, end_time, success) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
        [s.booking_id, s.game_id, s.room_id, s.start_time, s.end_time, s.success]
    )

# ─── PAYMENTS ────────────────────────────────────────────────────────────────


@app.get("/payments")
def list_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    method: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    offset = (page - 1) * limit
    conditions, params = [], []
    if status:
        conditions.append("p.payment_status = %s")
        params.append(status)
    if method:
        conditions.append("p.payment_method = %s")
        params.append(method)
    if from_date:
        conditions.append("p.payment_time >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("p.payment_time <= %s")
        params.append(to_date)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = query(
        f"SELECT COUNT(*) as cnt FROM payments p {where}", params or None, fetchall=False)
    rows = query(
        f"""SELECT p.*, b.customer_id, c.first_name || ' ' || c.last_name AS customer_name,
               g.game_name
        FROM payments p
        JOIN bookings b ON p.booking_id = b.booking_id
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN games g ON b.game_id = g.game_id
        {where}
        ORDER BY p.payment_time DESC LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/payments", status_code=201)
def create_payment(p: PaymentCreate):
    return execute(
        "INSERT INTO payments (booking_id, amount, payment_method, payment_status, payment_time) VALUES (%s,%s,%s,%s,NOW()) RETURNING *",
        [p.booking_id, p.amount, p.payment_method, p.payment_status]
    )

# ─── CLUES ───────────────────────────────────────────────────────────────────


@app.get("/clues")
def list_clues(page: int = Query(1, ge=1), limit: int = Query(20), game_id: Optional[int] = None):
    offset = (page - 1) * limit
    where, params = "", []
    if game_id:
        where = "WHERE c.game_id = %s"
        params = [game_id]
    total = query(
        f"SELECT COUNT(*) as cnt FROM clues c {where}", params or None, fetchall=False)
    rows = query(
        f"""SELECT c.*, g.game_name FROM clues c
        JOIN games g ON c.game_id = g.game_id
        {where} ORDER BY c.clue_id LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/clues", status_code=201)
def create_clue(c: ClueCreate):
    return execute(
        "INSERT INTO clues (game_id, clue_text, time_penalty) VALUES (%s,%s,%s) RETURNING *",
        [c.game_id, c.clue_text, c.time_penalty]
    )


@app.delete("/clues/{clue_id}")
def delete_clue(clue_id: int):
    return execute("DELETE FROM clues WHERE clue_id = %s", [clue_id])

# ─── SALARIES ────────────────────────────────────────────────────────────────


@app.get("/salaries")
def list_salaries(
    page: int = Query(1, ge=1),
    limit: int = Query(20),
    employee_id: Optional[int] = None,
    month: Optional[str] = None
):
    offset = (page - 1) * limit
    conditions, params = [], []
    if employee_id:
        conditions.append("s.employee_id = %s")
        params.append(employee_id)
    if month:
        conditions.append("TO_CHAR(s.month, 'YYYY-MM') = %s")
        params.append(month)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    total = query(
        f"SELECT COUNT(*) as cnt FROM salaries s {where}", params or None, fetchall=False)
    rows = query(
        f"""SELECT s.*, e.name AS employee_name, e.role FROM salaries s
        JOIN employees e ON s.employee_id = e.employee_id
        {where} ORDER BY s.month DESC LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/salaries", status_code=201)
def create_salary(s: SalaryCreate):
    # total_pay = hours * hourly_rate
    emp = query("SELECT hourly_rate FROM employees WHERE employee_id = %s", [
                s.employee_id], fetchall=False)
    if not emp:
        raise HTTPException(404, "Employee not found")
    total_pay = s.total_hours * float(emp["hourly_rate"])
    return execute(
        "INSERT INTO salaries (employee_id, month, total_hours, total_pay) VALUES (%s,%s,%s,%s) RETURNING *",
        [s.employee_id, s.month, s.total_hours, total_pay]
    )

# ─── LEAVES ──────────────────────────────────────────────────────────────────


@app.get("/leaves")
def list_leaves(
    page: int = Query(1, ge=1),
    limit: int = Query(20),
    employee_id: Optional[int] = None
):
    offset = (page - 1) * limit
    where, params = "", []
    if employee_id:
        where = "WHERE l.employee_id = %s"
        params = [employee_id]
    total = query(
        f"SELECT COUNT(*) as cnt FROM employee_leaves l {where}", params or None, fetchall=False)
    rows = query(
        f"""SELECT l.*, e.name AS employee_name FROM employee_leaves l
        JOIN employees e ON l.employee_id = e.employee_id
        {where} ORDER BY l.start_date DESC LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    return {"data": rows, "total": total["cnt"], "page": page, "limit": limit}


@app.post("/leaves", status_code=201)
def create_leave(l: LeaveCreate):
    return execute(
        "INSERT INTO employee_leaves (employee_id, start_date, end_date, reason) VALUES (%s,%s,%s,%s) RETURNING *",
        [l.employee_id, l.start_date, l.end_date, l.reason]
    )


@app.delete("/leaves/{leave_id}")
def delete_leave(leave_id: int):
    return execute("DELETE FROM employee_leaves WHERE leave_id = %s", [leave_id])

# ─── ANALYTICS / REPORTS ─────────────────────────────────────────────────────


@app.get("/analytics/dashboard")
def dashboard_summary():
    total_revenue = query(
        "SELECT COALESCE(SUM(amount),0) AS total FROM payments WHERE payment_status='SUCCESS'",
        fetchall=False
    )
    total_bookings = query(
        "SELECT COUNT(*) as cnt FROM bookings", fetchall=False)
    active_customers = query(
        "SELECT COUNT(DISTINCT customer_id) as cnt FROM bookings WHERE status != 'CANCELLED'",
        fetchall=False
    )
    success_rate = query(
        "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE success=true) / NULLIF(COUNT(*),0), 1) AS rate FROM game_sessions",
        fetchall=False
    )
    recent_bookings = query(
        """SELECT b.booking_id, c.first_name || ' ' || c.last_name AS customer,
               g.game_name, b.booking_date, b.status
           FROM bookings b
           JOIN customers c ON b.customer_id = c.customer_id
           JOIN games g ON b.game_id = g.game_id
           ORDER BY b.booking_date DESC LIMIT 5"""
    )
    top_games = query(
        """SELECT g.game_name,
               COUNT(b.booking_id) AS total_bookings,
               ROUND(100.0 * COUNT(*) FILTER (WHERE gs.success=true) / NULLIF(COUNT(gs.session_id),0), 1) AS success_rate
           FROM games g
           LEFT JOIN bookings b ON g.game_id = b.game_id
           LEFT JOIN game_sessions gs ON b.booking_id = gs.booking_id
           GROUP BY g.game_id, g.game_name
           ORDER BY total_bookings DESC LIMIT 5"""
    )
    return {
        "total_revenue": float(total_revenue["total"]),
        "total_bookings": total_bookings["cnt"],
        "active_customers": active_customers["cnt"],
        "escape_success_rate": float(success_rate["rate"] or 0),
        "recent_bookings": recent_bookings,
        "top_games": top_games
    }


@app.get("/analytics/revenue")
def revenue_analytics(period: str = "monthly"):
    if period == "daily":
        sql = """
            SELECT TO_CHAR(payment_time::date, 'YYYY-MM-DD') AS label,
                   COALESCE(SUM(amount),0) AS revenue,
                   COUNT(*) AS transactions
            FROM payments WHERE payment_status='SUCCESS'
            AND payment_time >= NOW() - INTERVAL '30 days'
            GROUP BY payment_time::date ORDER BY label
        """
    elif period == "weekly":
        sql = """
            SELECT TO_CHAR(DATE_TRUNC('week', payment_time), 'YYYY-MM-DD') AS label,
                   COALESCE(SUM(amount),0) AS revenue,
                   COUNT(*) AS transactions
            FROM payments WHERE payment_status='SUCCESS'
            GROUP BY DATE_TRUNC('week', payment_time) ORDER BY label
        """
    else:
        sql = """
            SELECT TO_CHAR(DATE_TRUNC('month', payment_time), 'Mon YYYY') AS label,
                   COALESCE(SUM(amount),0) AS revenue,
                   COUNT(*) AS transactions
            FROM payments WHERE payment_status='SUCCESS'
            GROUP BY DATE_TRUNC('month', payment_time) ORDER BY DATE_TRUNC('month', payment_time)
        """
    return query(sql)


@app.get("/analytics/game-performance")
def game_performance():
    return query("""
        SELECT g.game_name, g.difficulty_level,
               COUNT(gs.session_id) AS total_sessions,
               COUNT(*) FILTER (WHERE gs.success=true) AS successful,
               ROUND(100.0 * COUNT(*) FILTER (WHERE gs.success=true) / NULLIF(COUNT(gs.session_id),0), 1) AS success_rate,
               ROUND(AVG(EXTRACT(EPOCH FROM (gs.end_time - gs.start_time))/60), 1) AS avg_duration_mins,
               COUNT(sc.clue_id) AS total_clues_used
        FROM games g
        LEFT JOIN game_sessions gs ON g.game_id = gs.game_id
        LEFT JOIN session_clues sc ON gs.session_id = sc.session_id
        GROUP BY g.game_id, g.game_name, g.difficulty_level
        ORDER BY total_sessions DESC
    """)


@app.get("/analytics/employee-performance")
def employee_performance():
    return query("""
        SELECT e.name, e.role,
               COUNT(se.session_id) AS sessions_conducted,
               COALESCE(SUM(s.total_pay), 0) AS total_salary_paid,
               COALESCE(SUM(s.total_hours), 0) AS total_hours,
               COUNT(l.leave_id) AS leave_days
        FROM employees e
        LEFT JOIN session_employees se ON e.employee_id = se.employee_id
        LEFT JOIN salaries s ON e.employee_id = s.employee_id
        LEFT JOIN employee_leaves l ON e.employee_id = l.employee_id
        GROUP BY e.employee_id, e.name, e.role
        ORDER BY sessions_conducted DESC
    """)


@app.get("/analytics/booking-trends")
def booking_trends():
    return query("""
        SELECT TO_CHAR(booking_date, 'Dy') AS day_of_week,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE status='CONFIRMED') AS confirmed,
               COUNT(*) FILTER (WHERE status='CANCELLED') AS cancelled,
               COUNT(*) FILTER (WHERE status='COMPLETED') AS completed
        FROM bookings
        GROUP BY day_of_week, EXTRACT(DOW FROM booking_date)
        ORDER BY EXTRACT(DOW FROM booking_date)
    """)


@app.get("/analytics/payment-breakdown")
def payment_breakdown():
    by_method = query("""
        SELECT payment_method, COUNT(*) AS count,
               COALESCE(SUM(amount),0) AS total
        FROM payments WHERE payment_status='SUCCESS'
        GROUP BY payment_method ORDER BY total DESC
    """)
    by_status = query("""
        SELECT payment_status, COUNT(*) AS count,
               COALESCE(SUM(amount),0) AS total
        FROM payments GROUP BY payment_status
    """)
    return {"by_method": by_method, "by_status": by_status}


@app.get("/analytics/customer-insights")
def customer_insights():
    # Top customers by spend
    top_spenders = query("""
        SELECT c.first_name || ' ' || c.last_name AS name,
               COUNT(b.booking_id) AS bookings,
               COALESCE(SUM(p.amount),0) AS total_spent
        FROM customers c
        LEFT JOIN bookings b ON c.customer_id = b.customer_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id AND p.payment_status='SUCCESS'
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY total_spent DESC LIMIT 10
    """)
    # Retention: customers with >1 booking
    retention = query("""
        SELECT
            COUNT(*) FILTER (WHERE booking_count = 1) AS one_time,
            COUNT(*) FILTER (WHERE booking_count BETWEEN 2 AND 4) AS returning,
            COUNT(*) FILTER (WHERE booking_count >= 5) AS loyal
        FROM (
            SELECT customer_id, COUNT(*) AS booking_count FROM bookings GROUP BY customer_id
        ) sub
    """, fetchall=False)
    return {"top_spenders": top_spenders, "retention": retention}


@app.get("/analytics/clue-usage")
def clue_usage():
    return query("""
        SELECT g.game_name, cl.clue_text, cl.time_penalty,
               COUNT(sc.session_id) AS times_used
        FROM clues cl
        JOIN games g ON cl.game_id = g.game_id
        LEFT JOIN session_clues sc ON cl.clue_id = sc.clue_id
        GROUP BY g.game_name, cl.clue_id, cl.clue_text, cl.time_penalty
        ORDER BY times_used DESC LIMIT 20
    """)

# ─── CUSTOM QUERY PLAYGROUND ─────────────────────────────────────────────────


SAFE_KEYWORDS = ["select", "with", "explain"]
UNSAFE_KEYWORDS = ["drop", "delete", "update", "insert",
                   "truncate", "alter", "create", "grant", "revoke"]


@app.post("/query/execute")
def execute_custom_query(body: CustomQuery):
    sql_lower = body.sql.strip().lower()
    for kw in UNSAFE_KEYWORDS:
        if kw in sql_lower:
            raise HTTPException(
                403, f"Query contains forbidden keyword: '{kw}'. Only SELECT queries allowed.")
    if not any(sql_lower.startswith(kw) for kw in SAFE_KEYWORDS):
        raise HTTPException(
            403, "Only SELECT / WITH / EXPLAIN queries are permitted.")
    try:
        result = query(body.sql)
        return {"data": result, "rows": len(result)}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.get("/query/schema")
def get_schema():
    tables = query("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name
    """)
    schema = {}
    for t in tables:
        name = t["table_name"]
        cols = query("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, [name])
        schema[name] = cols
    return schema

# ─── LOOKUP LISTS ─────────────────────────────────────────────────────────────


@app.get("/lookup/games")
def lookup_games():
    return query("SELECT game_id, game_name FROM games ORDER BY game_name")


@app.get("/lookup/rooms")
def lookup_rooms():
    return query("SELECT room_id, room_name, capacity FROM rooms ORDER BY room_name")


@app.get("/lookup/employees")
def lookup_employees():
    return query("SELECT employee_id, name, role FROM employees ORDER BY name")


@app.get("/lookup/customers")
def lookup_customers():
    return query("SELECT customer_id, first_name || ' ' || last_name AS name, email FROM customers ORDER BY first_name")
