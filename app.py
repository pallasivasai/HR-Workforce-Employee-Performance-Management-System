import hashlib
import sqlite3
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# HR WORKFORCE PRO
# Employee Management & Performance Management System
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hr_workforce.db"

st.set_page_config(
    page_title="HR Workforce Pro",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 28px 30px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #ff7a18 0%,
            #e52e71 100%
        );
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        font-size: 38px;
        margin: 0 0 8px 0;
        font-weight: 700;
    }

    .hero p {
        font-size: 17px;
        margin: 0;
        opacity: 0.95;
    }

    [data-testid="stMetricValue"] {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# PASSWORD HASH
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database():

    conn = get_connection()
    cur = conn.cursor()

    # --------------------------------------------------------
    # Departments
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
    )

    # --------------------------------------------------------
    # Employees
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            department_id INTEGER,
            designation TEXT,
            joining_date TEXT,
            employment_status TEXT DEFAULT 'Active',
            manager TEXT,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(department_id)
                REFERENCES departments(id)
        )
        """
    )

    # --------------------------------------------------------
    # Users
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY(employee_id)
                REFERENCES employees(id)
        )
        """
    )

    # --------------------------------------------------------
    # Attendance
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            UNIQUE(employee_id, attendance_date),
            FOREIGN KEY(employee_id)
                REFERENCES employees(id)
        )
        """
    )

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            target REAL DEFAULT 0,
            achieved REAL DEFAULT 0,
            rating REAL DEFAULT 0,
            comments TEXT,
            UNIQUE(employee_id, period),
            FOREIGN KEY(employee_id)
                REFERENCES employees(id)
        )
        """
    )

    # --------------------------------------------------------
    # Goals
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            goal_title TEXT NOT NULL,
            target_value REAL DEFAULT 0,
            actual_value REAL DEFAULT 0,
            due_date TEXT,
            status TEXT DEFAULT 'In Progress',
            FOREIGN KEY(employee_id)
                REFERENCES employees(id)
        )
        """
    )

    # --------------------------------------------------------
    # Leave Records
    # --------------------------------------------------------

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leave_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            reason TEXT,
            FOREIGN KEY(employee_id)
                REFERENCES employees(id)
        )
        """
    )

    # ========================================================
    # DEFAULT DEPARTMENTS
    # ========================================================

    departments = [
        "Engineering",
        "Sales & Marketing",
        "Human Resources",
        "Finance",
        "Operations",
        "IT Support",
    ]

    for department in departments:

        cur.execute(
            """
            INSERT OR IGNORE INTO departments(name)
            VALUES (?)
            """,
            (department,)
        )

    # ========================================================
    # DEMO EMPLOYEES
    # ========================================================

    employee_count = cur.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    if employee_count == 0:

        department_map = {
            row["name"]: row["id"]
            for row in cur.execute(
                "SELECT id, name FROM departments"
            ).fetchall()
        }

        employees = [

            (
                "EMP001",
                "Arun Kumar",
                "arun@example.com",
                "9876543210",
                department_map["Engineering"],
                "Software Engineer",
                "2024-04-15",
                "Active",
                "Team Lead",
                "Hyderabad",
            ),

            (
                "EMP002",
                "Priya Sharma",
                "priya@example.com",
                "9876543211",
                department_map["Sales & Marketing"],
                "Marketing Executive",
                "2024-06-10",
                "Active",
                "Sales Manager",
                "Bengaluru",
            ),

            (
                "EMP003",
                "Rahul Reddy",
                "rahul@example.com",
                "9876543212",
                department_map["Engineering"],
                "Python Developer",
                "2025-01-06",
                "Active",
                "Engineering Manager",
                "Hyderabad",
            ),

            (
                "EMP004",
                "Sneha Rao",
                "sneha@example.com",
                "9876543213",
                department_map["Human Resources"],
                "HR Executive",
                "2024-08-19",
                "Active",
                "HR Manager",
                "Vijayawada",
            ),

            (
                "EMP005",
                "Ramu Marketing",
                "ramu@example.com",
                "9876543214",
                department_map["Sales & Marketing"],
                "Marketing Executive",
                "2025-03-03",
                "Active",
                "Sales Manager",
                "Vijayawada",
            ),

            (
                "EMP006",
                "Kiran Kumar",
                "kiran@example.com",
                "9876543215",
                department_map["Finance"],
                "Finance Analyst",
                "2023-11-20",
                "Active",
                "Finance Manager",
                "Chennai",
            ),

            (
                "EMP007",
                "Anjali Devi",
                "anjali@example.com",
                "9876543216",
                department_map["Operations"],
                "Operations Executive",
                "2024-02-12",
                "Active",
                "Operations Manager",
                "Hyderabad",
            ),

            (
                "EMP008",
                "Vikram Singh",
                "vikram@example.com",
                "9876543217",
                department_map["IT Support"],
                "IT Support Engineer",
                "2025-05-26",
                "Active",
                "IT Manager",
                "Bengaluru",
            ),
        ]

        cur.executemany(
            """
            INSERT INTO employees(
                employee_code,
                full_name,
                email,
                phone,
                department_id,
                designation,
                joining_date,
                employment_status,
                manager,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            employees
        )

    # ========================================================
    # USER ACCOUNTS
    # ========================================================

    employee_map = {
        row["employee_code"]: row["id"]
        for row in cur.execute(
            """
            SELECT id, employee_code
            FROM employees
            """
        ).fetchall()
    }

    # HR Admin
    cur.execute(
        """
        INSERT OR IGNORE INTO users(
            username,
            password_hash,
            role,
            employee_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "admin",
            hash_password("admin@123"),
            "HR Admin",
            None,
        )
    )

    # Employee
    cur.execute(
        """
        INSERT OR IGNORE INTO users(
            username,
            password_hash,
            role,
            employee_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "employee",
            hash_password("employee@123"),
            "Employee",
            employee_map.get("EMP001"),
        )
    )

    # ========================================================
    # PERFORMANCE DATA
    # ========================================================

    performance_count = cur.execute(
        "SELECT COUNT(*) FROM performance"
    ).fetchone()[0]

    if performance_count == 0:

        performance_data = [

            ("EMP001", "2026-01", 100, 92, 4.0, "Strong start"),
            ("EMP001", "2026-02", 100, 108, 4.5, "Exceeded target"),
            ("EMP001", "2026-03", 100, 105, 4.5, "Consistent delivery"),

            ("EMP002", "2026-01", 120, 115, 4.0, "Near target"),
            ("EMP002", "2026-02", 120, 130, 4.5, "Above target"),
            ("EMP002", "2026-03", 120, 126, 4.5, "Strong month"),

            ("EMP003", "2026-01", 100, 88, 3.5, "Improvement opportunity"),
            ("EMP003", "2026-02", 100, 96, 4.0, "Improving"),
            ("EMP003", "2026-03", 100, 103, 4.0, "Target reached"),

            ("EMP004", "2026-01", 90, 94, 4.0, "Good"),
            ("EMP004", "2026-02", 90, 91, 4.0, "Good"),
            ("EMP004", "2026-03", 90, 97, 4.5, "Excellent"),

            ("EMP005", "2026-01", 200, 72, 2.5, "Below target"),
            ("EMP005", "2026-02", 200, 81, 3.0, "Improving"),
            ("EMP005", "2026-03", 200, 76, 2.5, "Needs review"),

            ("EMP006", "2026-01", 100, 102, 4.0, "Target reached"),
            ("EMP006", "2026-02", 100, 98, 4.0, "Near target"),
            ("EMP006", "2026-03", 100, 104, 4.5, "Target reached"),

            ("EMP007", "2026-01", 100, 110, 4.5, "Excellent"),
            ("EMP007", "2026-02", 100, 107, 4.5, "Excellent"),
            ("EMP007", "2026-03", 100, 111, 4.5, "Excellent"),

            ("EMP008", "2026-01", 100, 95, 3.5, "Good"),
            ("EMP008", "2026-02", 100, 99, 4.0, "Good"),
            ("EMP008", "2026-03", 100, 101, 4.0, "Target reached"),
        ]

        cur.executemany(
            """
            INSERT INTO performance(
                employee_id,
                period,
                target,
                achieved,
                rating,
                comments
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    employee_map[code],
                    period,
                    target,
                    achieved,
                    rating,
                    comments,
                )
                for code, period, target, achieved, rating, comments
                in performance_data
            ]
        )

    # ========================================================
    # ATTENDANCE DATA
    # ========================================================

    attendance_count = cur.execute(
        "SELECT COUNT(*) FROM attendance"
    ).fetchone()[0]

    if attendance_count == 0:

        for code, employee_id in employee_map.items():

            for day in range(1, 11):

                if (day + employee_id) % 7 == 0:
                    status = "Work From Home"
                else:
                    status = "Present"

                cur.execute(
                    """
                    INSERT INTO attendance(
                        employee_id,
                        attendance_date,
                        status,
                        notes
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        employee_id,
                        f"2026-03-{day:02d}",
                        status,
                        "Demo record",
                    )
                )

    conn.commit()
    conn.close()


# ============================================================
# DATA FUNCTIONS
# ============================================================

def employee_data():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            e.id,
            e.employee_code AS "Employee Code",
            e.full_name AS "Employee",
            e.email AS "Email",
            e.phone AS "Phone",
            d.name AS "Department",
            e.designation AS "Designation",
            e.joining_date AS "Joining Date",
            e.employment_status AS "Status",
            e.manager AS "Manager",
            e.location AS "Location"

        FROM employees e

        LEFT JOIN departments d
            ON e.department_id = d.id

        ORDER BY e.id
        """,
        conn
    )

    conn.close()

    return df


def performance_data():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT

            p.id,

            e.employee_code AS "Employee Code",

            e.full_name AS "Employee",

            d.name AS "Department",

            p.period AS "Period",

            p.target AS "Target",

            p.achieved AS "Achieved",

            CASE
                WHEN p.target > 0
                THEN ROUND(
                    (p.achieved / p.target) * 100,
                    2
                )
                ELSE 0
            END AS "Achievement %",

            CASE
                WHEN p.target > 0
                     AND p.achieved >= p.target
                THEN 'YES'
                ELSE 'NO'
            END AS "Target Reach",

            p.rating AS "Rating",

            p.comments AS "Comments"

        FROM performance p

        JOIN employees e
            ON p.employee_id = e.id

        LEFT JOIN departments d
            ON e.department_id = d.id

        ORDER BY
            p.period DESC,
            p.achieved DESC
        """,
        conn
    )

    conn.close()

    return df


def attendance_data():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT

            a.id,

            e.employee_code AS "Employee Code",

            e.full_name AS "Employee",

            d.name AS "Department",

            a.attendance_date AS "Date",

            a.status AS "Status",

            a.notes AS "Notes"

        FROM attendance a

        JOIN employees e
            ON a.employee_id = e.id

        LEFT JOIN departments d
            ON e.department_id = d.id

        ORDER BY
            a.attendance_date DESC
        """,
        conn
    )

    conn.close()

    return df


def goals_data():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT

            g.id,

            e.employee_code AS "Employee Code",

            e.full_name AS "Employee",

            g.goal_title AS "Goal",

            g.target_value AS "Target",

            g.actual_value AS "Actual",

            CASE
                WHEN g.target_value > 0
                THEN ROUND(
                    (g.actual_value / g.target_value) * 100,
                    2
                )
                ELSE 0
            END AS "Progress %",

            g.due_date AS "Due Date",

            g.status AS "Status"

        FROM goals g

        JOIN employees e
            ON g.employee_id = e.id

        ORDER BY
            g.due_date
        """,
        conn
    )

    conn.close()

    return df


# ============================================================
# PDF
# ============================================================

def create_pdf(title, dataframe):

    try:

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

    except ImportError:

        return None

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    pdf_df = dataframe.copy()

    pdf_df = pdf_df.head(40)

    pdf_data = [
        list(pdf_df.columns)
    ]

    pdf_data.extend(
        pdf_df.fillna("").astype(str).values.tolist()
    )

    table = Table(
        pdf_data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#243447")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return buffer.getvalue()


# ============================================================
# LOGIN
# ============================================================

def login_screen():

    st.markdown(
        """
        <div class="hero">

            <h1>
                HR Workforce Pro
            </h1>

            <p>
                Employee Management • Performance • Attendance • Goals • HR Analytics
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1, 1.2, 1]
    )

    with center:

        st.subheader("🔐 Secure Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            conn = get_connection()

            user = conn.execute(
                """
                SELECT *
                FROM users
                WHERE username = ?
                  AND password_hash = ?
                """,
                (
                    username.strip(),
                    hash_password(password)
                )
            ).fetchone()

            conn.close()

            if user:

                st.session_state.authenticated = True

                st.session_state.username = user["username"]

                st.session_state.role = user["role"]

                st.session_state.employee_id = user["employee_id"]

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

        st.info(
            """
            **HR Admin**

            Username: `admin`

            Password: `admin@123`

            ---

            **Employee**

            Username: `employee`

            Password: `employee@123`
            """
        )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    st.sidebar.title(
        "👥 HR Workforce Pro"
    )

    st.sidebar.caption(
        f"Logged in as **{st.session_state.username}**"
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        for key in [
            "authenticated",
            "username",
            "role",
            "employee_id",
        ]:

            st.session_state.pop(
                key,
                None
            )

        st.rerun()


# ============================================================
# HR OVERVIEW
# ============================================================

def hr_overview():

    st.markdown(
        """
        <div class="hero">

            <h1>
                HR Workforce & Performance Management
            </h1>

            <p>
                Workforce insights, employee performance,
                attendance and goal tracking.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    employees = employee_data()

    performance = performance_data()

    attendance = attendance_data()

    active_employees = int(
        (
            employees["Status"] == "Active"
        ).sum()
    )

    average_achievement = (
        performance["Achievement %"].mean()
        if len(performance)
        else 0
    )

    target_reached = int(
        (
            performance["Target Reach"] == "YES"
        ).sum()
    )

    attendance_rate = (
        attendance["Status"]
        .isin(
            [
                "Present",
                "Work From Home"
            ]
        )
        .mean()
        * 100
        if len(attendance)
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Active Employees",
        active_employees
    )

    c2.metric(
        "Performance Records",
        len(performance)
    )

    c3.metric(
        "Avg Achievement",
        f"{average_achievement:.1f}%"
    )

    c4.metric(
        "Attendance Rate",
        f"{attendance_rate:.1f}%"
    )

    st.subheader(
        "📈 Performance Trend"
    )

    if len(performance):

        trend = (
            performance
            .groupby("Period")["Achievement %"]
            .mean()
            .reset_index()
        )

        trend["Achievement %"] = trend[
            "Achievement %"
        ].round(2)

        st.line_chart(
            trend.set_index("Period")
        )

    st.subheader(
        "🏆 Department Performance"
    )

    if len(performance):

        department_summary = (
            performance
            .groupby("Department")
            .agg(
                Employees=(
                    "Employee",
                    "nunique"
                ),

                Avg_Achievement=(
                    "Achievement %",
                    "mean"
                ),

                Target_Reached=(
                    "Target Reach",
                    lambda x:
                    (x == "YES").sum()
                ),
            )
            .reset_index()
        )

        department_summary[
            "Avg_Achievement"
        ] = department_summary[
            "Avg_Achievement"
        ].round(1)

        st.dataframe(
            department_summary,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "Performance analytics are intended to support HR review and employee development."
    )


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def employee_management():

    st.title(
        "👥 Employee Management"
    )

    tab1, tab2 = st.tabs(
        [
            "Employee Directory",
            "Add Employee"
        ]
    )

    with tab1:

        df = employee_data()

        search = st.text_input(
            "Search employee, code or department"
        )

        if search:

            mask = (
                df.astype(str)
                .apply(
                    lambda column:
                    column.str.contains(
                        search,
                        case=False,
                        na=False
                    )
                )
                .any(axis=1)
            )

            df = df[mask]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if len(df):

            selected_code = st.selectbox(
                "Select employee",
                df["Employee Code"].tolist()
            )

            new_status = st.selectbox(
                "Employment Status",
                [
                    "Active",
                    "Inactive",
                    "On Leave"
                ]
            )

            if st.button(
                "Update Status"
            ):

                conn = get_connection()

                conn.execute(
                    """
                    UPDATE employees
                    SET employment_status = ?
                    WHERE employee_code = ?
                    """,
                    (
                        new_status,
                        selected_code
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    "Employee status updated."
                )

                st.rerun()

    with tab2:

        departments = get_connection().execute(
            """
            SELECT id, name
            FROM departments
            ORDER BY name
            """
        ).fetchall()

        with st.form(
            "add_employee"
        ):

            c1, c2 = st.columns(2)

            employee_code = c1.text_input(
                "Employee Code",
                placeholder="EMP009"
            )

            full_name = c2.text_input(
                "Full Name"
            )

            email = c1.text_input(
                "Email"
            )

            phone = c2.text_input(
                "Phone"
            )

            department_name = c1.selectbox(
                "Department",
                [
                    row["name"]
                    for row in departments
                ]
            )

            designation = c2.text_input(
                "Designation"
            )

            joining_date = c1.date_input(
                "Joining Date",
                value=date.today()
            )

            manager = c2.text_input(
                "Manager"
            )

            location = c1.text_input(
                "Location"
            )

            submitted = st.form_submit_button(
                "Create Employee",
                type="primary"
            )

            if submitted:

                if not employee_code.strip():
                    st.error(
                        "Employee Code is required."
                    )
                    return

                if not full_name.strip():
                    st.error(
                        "Full Name is required."
                    )
                    return

                conn = get_connection()

                department_id = next(
                    row["id"]
                    for row in departments
                    if row["name"] == department_name
                )

                try:

                    conn.execute(
                        """
                        INSERT INTO employees(
                            employee_code,
                            full_name,
                            email,
                            phone,
                            department_id,
                            designation,
                            joining_date,
                            employment_status,
                            manager,
                            location
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            employee_code.strip(),
                            full_name.strip(),
                            email.strip(),
                            phone,
                            department_id,
                            designation,
                            joining_date.isoformat(),
                            "Active",
                            manager,
                            location,
                        )
                    )

                    conn.commit()

                    st.success(
                        "Employee created successfully."
                    )

                except sqlite3.IntegrityError as error:

                    st.error(
                        f"Employee could not be created: {error}"
                    )

                finally:

                    conn.close()


# ============================================================
# PERFORMANCE MANAGEMENT
# ============================================================

def performance_management():

    st.title(
        "📊 Performance Management"
    )

    df = performance_data()

    col1, col2 = st.columns(2)

    period_filter = col1.selectbox(
        "Period",
        [
            "All"
        ]
        +
        sorted(
            df["Period"].unique().tolist(),
            reverse=True
        )
    )

    employee_filter = col2.selectbox(
        "Employee",
        [
            "All"
        ]
        +
        sorted(
            df["Employee"].unique().tolist()
        )
    )

    filtered = df.copy()

    if period_filter != "All":

        filtered = filtered[
            filtered["Period"] == period_filter
        ]

    if employee_filter != "All":

        filtered = filtered[
            filtered["Employee"]
            == employee_filter
        ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Records",
        len(filtered)
    )

    c2.metric(
        "Average Achievement",
        (
            f"{filtered['Achievement %'].mean():.1f}%"
            if len(filtered)
            else "0%"
        )
    )

    c3.metric(
        "Target Reached",
        int(
            (
                filtered["Target Reach"]
                == "YES"
            ).sum()
        )
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "➕ Add / Update Performance"
    )

    conn = get_connection()

    employees = conn.execute(
        """
        SELECT
            id,
            employee_code,
            full_name
        FROM employees
        ORDER BY full_name
        """
    ).fetchall()

    conn.close()

    with st.form(
        "performance_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{row['employee_code']} — {row['full_name']}"
                for row in employees
            ]
        )

        c1, c2, c3 = st.columns(3)

        period = c1.text_input(
            "Period",
            value=datetime.now().strftime("%Y-%m")
        )

        target = c2.number_input(
            "Target",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        achieved = c3.number_input(
            "Achieved",
            min_value=0.0,
            value=0.0,
            step=10.0
        )

        rating = st.slider(
            "Rating",
            0.0,
            5.0,
            3.0,
            0.5
        )

        comments = st.text_area(
            "Comments"
        )

        save = st.form_submit_button(
            "Save Performance",
            type="primary"
        )

        if save:

            selected = next(
                row
                for row in employees
                if (
                    f"{row['employee_code']} — "
                    f"{row['full_name']}"
                    == employee_label
                )
            )

            conn = get_connection()

            conn.execute(
                """
                INSERT INTO performance(
                    employee_id,
                    period,
                    target,
                    achieved,
                    rating,
                    comments
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(
                    employee_id,
                    period
                )

                DO UPDATE SET

                    target = excluded.target,

                    achieved = excluded.achieved,

                    rating = excluded.rating,

                    comments = excluded.comments
                """,
                (
                    selected["id"],
                    period.strip(),
                    target,
                    achieved,
                    rating,
                    comments,
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Performance saved successfully."
            )

            st.rerun()


# ============================================================
# ATTENDANCE
# ============================================================

def attendance_management():

    st.title(
        "📅 Attendance Management"
    )

    df = attendance_data()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    conn = get_connection()

    employees = conn.execute(
        """
        SELECT
            id,
            employee_code,
            full_name
        FROM employees
        ORDER BY full_name
        """
    ).fetchall()

    conn.close()

    with st.form(
        "attendance_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{row['employee_code']} — {row['full_name']}"
                for row in employees
            ]
        )

        attendance_date = st.date_input(
            "Date",
            value=date.today()
        )

        status = st.selectbox(
            "Status",
            [
                "Present",
                "Absent",
                "Work From Home",
                "Leave"
            ]
        )

        notes = st.text_input(
            "Notes"
        )

        if st.form_submit_button(
            "Save Attendance",
            type="primary"
        ):

            selected = next(
                row
                for row in employees
                if (
                    f"{row['employee_code']} — "
                    f"{row['full_name']}"
                    == employee_label
                )
            )

            conn = get_connection()

            conn.execute(
                """
                INSERT INTO attendance(
                    employee_id,
                    attendance_date,
                    status,
                    notes
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    employee_id,
                    attendance_date
                )

                DO UPDATE SET

                    status = excluded.status,

                    notes = excluded.notes
                """,
                (
                    selected["id"],
                    attendance_date.isoformat(),
                    status,
                    notes,
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Attendance saved."
            )

            st.rerun()


# ============================================================
# GOALS
# ============================================================

def goals_management():

    st.title(
        "🎯 Goals & Target Tracking"
    )

    df = goals_data()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    conn = get_connection()

    employees = conn.execute(
        """
        SELECT
            id,
            employee_code,
            full_name
        FROM employees
        ORDER BY full_name
        """
    ).fetchall()

    conn.close()

    with st.form(
        "goal_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{row['employee_code']} — {row['full_name']}"
                for row in employees
            ]
        )

        goal_title = st.text_input(
            "Goal Title"
        )

        c1, c2, c3 = st.columns(3)

        target_value = c1.number_input(
            "Target",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        actual_value = c2.number_input(
            "Actual",
            min_value=0.0,
            value=0.0,
            step=10.0
        )

        due_date = c3.date_input(
            "Due Date",
            value=date.today()
        )

        status = st.selectbox(
            "Status",
            [
                "Not Started",
                "In Progress",
                "Completed",
                "On Hold"
            ]
        )

        if st.form_submit_button(
            "Create Goal",
            type="primary"
        ):

            selected = next(
                row
                for row in employees
                if (
                    f"{row['employee_code']} — "
                    f"{row['full_name']}"
                    == employee_label
                )
            )

            conn = get_connection()

            conn.execute(
                """
                INSERT INTO goals(
                    employee_id,
                    goal_title,
                    target_value,
                    actual_value,
                    due_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    selected["id"],
                    goal_title,
                    target_value,
                    actual_value,
                    due_date.isoformat(),
                    status,
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Goal created successfully."
            )

            st.rerun()


# ============================================================
# LEAVE
# ============================================================

def leave_management():

    st.title(
        "📝 Leave Records"
    )

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT

            l.id,

            e.employee_code AS "Employee Code",

            e.full_name AS "Employee",

            l.leave_type AS "Leave Type",

            l.start_date AS "Start",

            l.end_date AS "End",

            l.days AS "Days",

            l.status AS "Status",

            l.reason AS "Reason"

        FROM leave_records l

        JOIN employees e
            ON l.employee_id = e.id

        ORDER BY
            l.start_date DESC
        """,
        conn
    )

    employees = conn.execute(
        """
        SELECT
            id,
            employee_code,
            full_name
        FROM employees
        ORDER BY full_name
        """
    ).fetchall()

    conn.close()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    with st.form(
        "leave_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{row['employee_code']} — {row['full_name']}"
                for row in employees
            ]
        )

        leave_type = st.selectbox(
            "Leave Type",
            [
                "Casual Leave",
                "Sick Leave",
                "Earned Leave",
                "Work From Home",
                "Other"
            ]
        )

        c1, c2 = st.columns(2)

        start_date = c1.date_input(
            "Start Date",
            value=date.today()
        )

        end_date = c2.date_input(
            "End Date",
            value=date.today()
        )

        reason = st.text_area(
            "Reason"
        )

        if st.form_submit_button(
            "Submit Leave",
            type="primary"
        ):

            if end_date < start_date:

                st.error(
                    "End date cannot be before start date."
                )

                return

            selected = next(
                row
                for row in employees
                if (
                    f"{row['employee_code']} — "
                    f"{row['full_name']}"
                    == employee_label
                )
            )

            days = (
                end_date - start_date
            ).days + 1

            conn = get_connection()

            conn.execute(
                """
                INSERT INTO leave_records(
                    employee_id,
                    leave_type,
                    start_date,
                    end_date,
                    days,
                    status,
                    reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    selected["id"],
                    leave_type,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    days,
                    "Pending",
                    reason,
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Leave record submitted."
            )

            st.rerun()


# ============================================================
# REPORTS
# ============================================================

def reports():

    st.title(
        "📄 HR Reports"
    )

    report_options = {

        "Employee Directory":
            employee_data(),

        "Performance Report":
            performance_data(),

        "Attendance Report":
            attendance_data(),

        "Goals Report":
            goals_data(),
    }

    selected_report = st.selectbox(
        "Select Report",
        list(report_options.keys())
    )

    df = report_options[
        selected_report
    ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download CSV",
        csv_data,
        file_name=(
            selected_report
            .lower()
            .replace(" ", "_")
            + ".csv"
        ),
        mime="text/csv",
    )

    pdf_data = create_pdf(
        selected_report,
        df
    )

    if pdf_data:

        st.download_button(
            "📄 Download PDF",
            pdf_data,
            file_name=(
                selected_report
                .lower()
                .replace(" ", "_")
                + ".pdf"
            ),
            mime="application/pdf",
        )


# ============================================================
# EMPLOYEE VIEW
# ============================================================

def employee_overview():

    employee_id = (
        st.session_state.employee_id
    )

    conn = get_connection()

    employee = conn.execute(
        """
        SELECT

            e.*,

            d.name AS department

        FROM employees e

        LEFT JOIN departments d
            ON e.department_id = d.id

        WHERE e.id = ?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    performance = performance_data()

    attendance = attendance_data()

    performance = performance[
        performance["Employee Code"]
        == employee["employee_code"]
    ]

    attendance = attendance[
        attendance["Employee Code"]
        == employee["employee_code"]
    ]

    st.markdown(
        f"""
        <div class="hero">

            <h1>
                Welcome, {employee["full_name"]}
            </h1>

            <p>
                {employee["designation"]}
                •
                {employee["department"]}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Performance Records",
        len(performance)
    )

    c2.metric(
        "Average Achievement",
        (
            f"{performance['Achievement %'].mean():.1f}%"
            if len(performance)
            else "0%"
        )
    )

    c3.metric(
        "Attendance Rate",
        (
            f"{attendance['Status'].isin(['Present','Work From Home']).mean()*100:.1f}%"
            if len(attendance)
            else "0%"
        )
    )

    st.subheader(
        "📊 Recent Performance"
    )

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )


def employee_performance():

    employee_id = (
        st.session_state.employee_id
    )

    conn = get_connection()

    employee = conn.execute(
        """
        SELECT employee_code
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    df = performance_data()

    df = df[
        df["Employee Code"]
        == employee["employee_code"]
    ]

    st.title(
        "📊 My Performance"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    if len(df):

        st.line_chart(
            df.set_index("Period")[
                "Achievement %"
            ]
        )


def employee_attendance():

    employee_id = (
        st.session_state.employee_id
    )

    conn = get_connection()

    employee = conn.execute(
        """
        SELECT employee_code
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    df = attendance_data()

    df = df[
        df["Employee Code"]
        == employee["employee_code"]
    ]

    st.title(
        "📅 My Attendance"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def employee_goals():

    employee_id = (
        st.session_state.employee_id
    )

    conn = get_connection()

    employee = conn.execute(
        """
        SELECT employee_code
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    df = goals_data()

    df = df[
        df["Employee Code"]
        == employee["employee_code"]
    ]

    st.title(
        "🎯 My Goals"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def employee_report():

    employee_id = (
        st.session_state.employee_id
    )

    conn = get_connection()

    employee = conn.execute(
        """
        SELECT employee_code
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    ).fetchone()

    conn.close()

    df = performance_data()

    df = df[
        df["Employee Code"]
        == employee["employee_code"]
    ]

    st.title(
        "📄 My Performance Report"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    pdf_data = create_pdf(
        "Employee Performance Report",
        df
    )

    if pdf_data:

        st.download_button(
            "📄 Download PDF",
            pdf_data,
            file_name=(
                f"{employee['employee_code']}"
                "_performance_report.pdf"
            ),
            mime="application/pdf"
        )


# ============================================================
# HR ADMIN NAVIGATION
# ============================================================

def admin_dashboard():

    sidebar()

    pages = [
        "🏠 HR Overview",
        "👥 Employees",
        "📊 Performance",
        "📅 Attendance",
        "🎯 Goals",
        "📝 Leave Records",
        "📄 Reports",
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        pages
    )

    if selected_page == "🏠 HR Overview":

        hr_overview()

    elif selected_page == "👥 Employees":

        employee_management()

    elif selected_page == "📊 Performance":

        performance_management()

    elif selected_page == "📅 Attendance":

        attendance_management()

    elif selected_page == "🎯 Goals":

        goals_management()

    elif selected_page == "📝 Leave Records":

        leave_management()

    elif selected_page == "📄 Reports":

        reports()


# ============================================================
# EMPLOYEE NAVIGATION
# ============================================================

def employee_dashboard():

    sidebar()

    pages = [
        "🏠 My Overview",
        "📊 My Performance",
        "📅 My Attendance",
        "🎯 My Goals",
        "📄 My Report",
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        pages
    )

    if selected_page == "🏠 My Overview":

        employee_overview()

    elif selected_page == "📊 My Performance":

        employee_performance()

    elif selected_page == "📅 My Attendance":

        employee_attendance()

    elif selected_page == "🎯 My Goals":

        employee_goals()

    elif selected_page == "📄 My Report":

        employee_report()


# ============================================================
# MAIN
# ============================================================

init_database()

if not st.session_state.get(
    "authenticated",
    False
):

    login_screen()

else:

    if (
        st.session_state.role
        == "HR Admin"
    ):

        admin_dashboard()

    else:

        employee_dashboard()
