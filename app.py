import hashlib
import sqlite3
from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

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

    REPORTLAB_OK = True

except Exception:
    REPORTLAB_OK = False


# ============================================================
# CONFIGURATION
# ============================================================

DB = Path(__file__).with_name("hr_workforce.db")

st.set_page_config(
    page_title="HR Workforce Pro",
    page_icon="👥",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
    }

    .hero {
        padding: 26px 30px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #ff7a18,
            #e52e71
        );
        color: white;
        margin-bottom: 22px;
    }

    .hero strong {
        display: block;
        font-size: 38px;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .hero span {
        font-size: 17px;
    }

    .small {
        font-size: 13px;
        opacity: 0.75;
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
# PASSWORD HASHING
# ============================================================

def hp(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def conn():

    connection = sqlite3.connect(
        DB,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE QUERY HELPER
# ============================================================

def q(
    sql,
    params=(),
    fetch=False,
    many=False
):

    connection = conn()

    cursor = connection.cursor()

    if many:

        cursor.executemany(
            sql,
            params
        )

    else:

        cursor.execute(
            sql,
            params
        )

    output = None

    if fetch:

        output = [
            dict(row)
            for row in cursor.fetchall()
        ]

    connection.commit()

    connection.close()

    return output


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init():

    connection = conn()

    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS departments(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            dept_id INTEGER,
            designation TEXT,
            joining TEXT,
            status TEXT DEFAULT 'Active',
            manager TEXT,
            location TEXT,
            FOREIGN KEY(dept_id)
                REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            employee_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS performance(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            period TEXT,
            target REAL,
            achieved REAL,
            rating REAL,
            comments TEXT,
            UNIQUE(employee_id, period)
        );

        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            day TEXT,
            status TEXT,
            notes TEXT,
            UNIQUE(employee_id, day)
        );

        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            title TEXT,
            target REAL,
            actual REAL,
            due TEXT,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS leave_records(
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            type TEXT,
            start TEXT,
            end TEXT,
            days REAL,
            status TEXT,
            reason TEXT
        );
        """
    )


    # ========================================================
    # DEPARTMENTS
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

        cursor.execute(
            """
            INSERT OR IGNORE INTO departments(name)
            VALUES(?)
            """,
            (department,)
        )


    # ========================================================
    # EMPLOYEES
    # ========================================================

    employee_count = cursor.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]


    if employee_count == 0:

        department_map = {
            row["name"]: row["id"]
            for row in cursor.execute(
                """
                SELECT id,name
                FROM departments
                """
            ).fetchall()
        }


        employee_rows = [

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


        cursor.executemany(
            """
            INSERT INTO employees(
                code,
                name,
                email,
                phone,
                dept_id,
                designation,
                joining,
                status,
                manager,
                location
            )
            VALUES(
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            employee_rows
        )


    # ========================================================
    # EMPLOYEE MAP
    # ========================================================

    employee_map = {
        row["code"]: row["id"]
        for row in cursor.execute(
            """
            SELECT id,code
            FROM employees
            """
        ).fetchall()
    }


    # ========================================================
    # USERS
    # ========================================================

    users = [

        (
            "admin",
            hp("admin@123"),
            "HR Admin",
            None,
        ),

        (
            "employee",
            hp("employee@123"),
            "Employee",
            employee_map["EMP001"],
        ),
    ]


    for user in users:

        cursor.execute(
            """
            INSERT OR IGNORE INTO users(
                username,
                password_hash,
                role,
                employee_id
            )
            VALUES(
                ?,
                ?,
                ?,
                ?
            )
            """,
            user
        )


    # ========================================================
    # PERFORMANCE DEMO DATA
    # ========================================================

    performance_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM performance
        """
    ).fetchone()[0]


    if performance_count == 0:

        performance_values = {

            1: [92, 108, 105],

            2: [115, 130, 126],

            3: [88, 96, 103],

            4: [94, 91, 97],

            5: [72, 81, 76],

            6: [102, 98, 104],

            7: [110, 107, 111],

            8: [95, 99, 101],
        }


        performance_rows = []


        for employee_id, achievements in performance_values.items():

            for index, achieved in enumerate(
                achievements,
                start=1
            ):

                target = (
                    200
                    if employee_id == 5
                    else 100
                )


                rating = (
                    4.0
                    if achieved >= 90
                    else 3.0
                )


                performance_rows.append(
                    (
                        employee_id,
                        f"2026-0{index}",
                        target,
                        achieved,
                        rating,
                        "Demo performance record",
                    )
                )


        cursor.executemany(
            """
            INSERT INTO performance(
                employee_id,
                period,
                target,
                achieved,
                rating,
                comments
            )
            VALUES(
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            performance_rows
        )


    # ========================================================
    # ATTENDANCE DEMO DATA
    # ========================================================

    attendance_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM attendance
        """
    ).fetchone()[0]


    if attendance_count == 0:

        attendance_rows = []


        for employee_id in range(1, 9):

            for day_number in range(1, 11):

                if (
                    employee_id + day_number
                ) % 7 == 0:

                    status = "Work From Home"

                else:

                    status = "Present"


                attendance_rows.append(
                    (
                        employee_id,
                        f"2026-03-{day_number:02d}",
                        status,
                        "Demo record",
                    )
                )


        cursor.executemany(
            """
            INSERT INTO attendance(
                employee_id,
                day,
                status,
                notes
            )
            VALUES(
                ?,
                ?,
                ?,
                ?
            )
            """,
            attendance_rows
        )


    connection.commit()

    connection.close()


# ============================================================
# EMPLOYEE DATAFRAME
# ============================================================

def edf():

    return pd.read_sql_query(
        """
        SELECT

            e.code AS "Employee Code",

            e.name AS "Employee",

            e.email AS "Email",

            e.phone AS "Phone",

            d.name AS "Department",

            e.designation AS "Designation",

            e.joining AS "Joining Date",

            e.status AS "Status",

            e.manager AS "Manager",

            e.location AS "Location"

        FROM employees e

        LEFT JOIN departments d
            ON e.dept_id = d.id

        ORDER BY e.id
        """,
        conn()
    )


# ============================================================
# PERFORMANCE DATAFRAME
# ============================================================

def performance():

    return pd.read_sql_query(
        """
        SELECT

            e.code AS "Employee Code",

            e.name AS "Employee",

            d.name AS "Department",

            p.period AS "Period",

            p.target AS "Target",

            p.achieved AS "Achieved",

            ROUND(
                CASE
                    WHEN p.target > 0
                    THEN (
                        p.achieved
                        * 100.0
                        / p.target
                    )
                    ELSE 0
                END,
                2
            ) AS "Achievement %",

            CASE
                WHEN p.achieved >= p.target
                THEN 'YES'
                ELSE 'NO'
            END AS "Target Reach",

            p.rating AS "Rating",

            p.comments AS "Comments"

        FROM performance p

        JOIN employees e
            ON p.employee_id = e.id

        LEFT JOIN departments d
            ON e.dept_id = d.id

        ORDER BY
            p.period DESC,
            p.achieved DESC
        """,
        conn()
    )


# ============================================================
# ATTENDANCE DATAFRAME
# ============================================================

def attendance():

    return pd.read_sql_query(
        """
        SELECT

            e.code AS "Employee Code",

            e.name AS "Employee",

            d.name AS "Department",

            a.day AS "Date",

            a.status AS "Status",

            a.notes AS "Notes"

        FROM attendance a

        JOIN employees e
            ON a.employee_id = e.id

        LEFT JOIN departments d
            ON e.dept_id = d.id

        ORDER BY
            a.day DESC
        """,
        conn()
    )


# ============================================================
# GOALS DATAFRAME
# ============================================================

def goals():

    return pd.read_sql_query(
        """
        SELECT

            e.code AS "Employee Code",

            e.name AS "Employee",

            g.title AS "Goal",

            g.target AS "Target",

            g.actual AS "Actual",

            ROUND(
                CASE
                    WHEN g.target > 0
                    THEN (
                        g.actual
                        * 100.0
                        / g.target
                    )
                    ELSE 0
                END,
                2
            ) AS "Progress %",

            g.due AS "Due Date",

            g.status AS "Status"

        FROM goals g

        JOIN employees e
            ON g.employee_id = e.id

        ORDER BY
            g.due
        """,
        conn()
    )


# ============================================================
# PDF GENERATOR
# ============================================================

def pdf(title, dataframe):

    if not REPORTLAB_OK:

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


    story = [

        Paragraph(
            title,
            styles["Title"]
        ),

        Spacer(
            1,
            10
        ),
    ]


    pdf_data = [

        list(dataframe.columns)

    ]


    pdf_data.extend(

        dataframe
        .fillna("")
        .astype(str)
        .values
        .tolist()

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
                    colors.HexColor(
                        "#243447"
                    ),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.grey,
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
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

def login():

    # FIXED HTML
    # No visible <h1> / <p> tags.

    st.markdown(
        """
        <div class="hero">

            <strong>
                HR Workforce Pro
            </strong>

            <span>
                Employee Management •
                Performance •
                Attendance •
                Goals •
                HR Analytics
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


    _, center, _ = st.columns(
        [1, 1.2, 1]
    )


    with center:

        st.subheader(
            "🔐 Secure Login"
        )


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

            result = q(
                """
                SELECT *
                FROM users
                WHERE username = ?
                AND password_hash = ?
                """,
                (
                    username.strip(),
                    hp(password)
                ),
                fetch=True
            )


            if result:

                st.session_state.update(

                    auth=True,

                    user=result[0]["username"],

                    role=result[0]["role"],

                    eid=result[0]["employee_id"],
                )


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
# PERFORMANCE PAGE
# ============================================================

def performance_page():

    st.title(
        "📊 Performance Management"
    )


    dataframe = performance()


    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )


    employees = q(
        """
        SELECT
            id,
            code,
            name
        FROM employees
        ORDER BY name
        """,
        fetch=True
    )


    st.subheader(
        "➕ Add / Update Performance"
    )


    with st.form(
        "performance_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['code']} — {x['name']}"
                for x in employees
            ]
        )


        col1, col2, col3 = st.columns(3)


        period = col1.text_input(
            "Period",
            "2026-04"
        )


        target = col2.number_input(
            "Target",
            0.0,
            10000000.0,
            100.0
        )


        achieved = col3.number_input(
            "Achieved",
            0.0,
            10000000.0,
            0.0
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


        if st.form_submit_button(
            "Save Performance",
            type="primary"
        ):

            selected_employee = next(

                employee

                for employee in employees

                if (
                    f"{employee['code']} — "
                    f"{employee['name']}"
                )
                == employee_label

            )


            q(
                """
                INSERT INTO performance(
                    employee_id,
                    period,
                    target,
                    achieved,
                    rating,
                    comments
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )

                ON CONFLICT(
                    employee_id,
                    period
                )

                DO UPDATE SET

                    target =
                        excluded.target,

                    achieved =
                        excluded.achieved,

                    rating =
                        excluded.rating,

                    comments =
                        excluded.comments
                """,
                (
                    selected_employee["id"],
                    period,
                    target,
                    achieved,
                    rating,
                    comments,
                )
            )


            st.success(
                "Performance saved."
            )


            st.rerun()


# ============================================================
# ATTENDANCE PAGE
# ============================================================

def attendance_page():

    st.title(
        "📅 Attendance Management"
    )


    st.dataframe(
        attendance(),
        use_container_width=True,
        hide_index=True
    )


    employees = q(
        """
        SELECT
            id,
            code,
            name
        FROM employees
        ORDER BY name
        """,
        fetch=True
    )


    with st.form(
        "attendance_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['code']} — {x['name']}"
                for x in employees
            ]
        )


        attendance_date = st.date_input(
            "Date",
            date.today()
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

            selected_employee = next(

                employee

                for employee in employees

                if (
                    f"{employee['code']} — "
                    f"{employee['name']}"
                )
                == employee_label

            )


            q(
                """
                INSERT INTO attendance(
                    employee_id,
                    day,
                    status,
                    notes
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?
                )

                ON CONFLICT(
                    employee_id,
                    day
                )

                DO UPDATE SET

                    status =
                        excluded.status,

                    notes =
                        excluded.notes
                """,
                (
                    selected_employee["id"],
                    attendance_date.isoformat(),
                    status,
                    notes,
                )
            )


            st.success(
                "Attendance saved."
            )


            st.rerun()


# ============================================================
# GOALS PAGE
# ============================================================

def goals_page():

    st.title(
        "🎯 Goals & Target Tracking"
    )


    st.dataframe(
        goals(),
        use_container_width=True,
        hide_index=True
    )


    employees = q(
        """
        SELECT
            id,
            code,
            name
        FROM employees
        ORDER BY name
        """,
        fetch=True
    )


    with st.form(
        "goal_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['code']} — {x['name']}"
                for x in employees
            ]
        )


        title = st.text_input(
            "Goal title"
        )


        col1, col2, col3 = st.columns(3)


        target = col1.number_input(
            "Target value",
            0.0,
            10000000.0,
            100.0
        )


        actual = col2.number_input(
            "Actual value",
            0.0,
            10000000.0,
            0.0
        )


        due = col3.date_input(
            "Due date",
            date.today()
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

            selected_employee = next(

                employee

                for employee in employees

                if (
                    f"{employee['code']} — "
                    f"{employee['name']}"
                )
                == employee_label

            )


            q(
                """
                INSERT INTO goals(
                    employee_id,
                    title,
                    target,
                    actual,
                    due,
                    status
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    selected_employee["id"],
                    title,
                    target,
                    actual,
                    due.isoformat(),
                    status,
                )
            )


            st.success(
                "Goal created."
            )


            st.rerun()


# ============================================================
# LEAVE PAGE
# ============================================================

def leave_page():

    st.title(
        "📝 Leave Records"
    )


    dataframe = pd.read_sql_query(
        """
        SELECT

            e.code AS "Employee Code",

            e.name AS "Employee",

            l.type AS "Leave Type",

            l.start AS "Start",

            l.end AS "End",

            l.days AS "Days",

            l.status AS "Status",

            l.reason AS "Reason"

        FROM leave_records l

        JOIN employees e
            ON l.employee_id = e.id

        ORDER BY
            l.start DESC
        """,
        conn()
    )


    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )


    employees = q(
        """
        SELECT
            id,
            code,
            name
        FROM employees
        ORDER BY name
        """,
        fetch=True
    )


    with st.form(
        "leave_form"
    ):

        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['code']} — {x['name']}"
                for x in employees
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


        col1, col2 = st.columns(2)


        start = col1.date_input(
            "Start",
            date.today()
        )


        end = col2.date_input(
            "End",
            date.today()
        )


        reason = st.text_area(
            "Reason"
        )


        if st.form_submit_button(
            "Submit Leave",
            type="primary"
        ):

            if end < start:

                st.error(
                    "End date cannot be before start date."
                )

                return


            selected_employee = next(

                employee

                for employee in employees

                if (
                    f"{employee['code']} — "
                    f"{employee['name']}"
                )
                == employee_label

            )


            days = (
                end - start
            ).days + 1


            q(
                """
                INSERT INTO leave_records(
                    employee_id,
                    type,
                    start,
                    end,
                    days,
                    status,
                    reason
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    selected_employee["id"],
                    leave_type,
                    start.isoformat(),
                    end.isoformat(),
                    days,
                    "Pending",
                    reason,
                )
            )


            st.success(
                "Leave submitted."
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
            edf(),

        "Performance Report":
            performance(),

        "Attendance Report":
            attendance(),

        "Goals Report":
            goals(),
    }


    report_name = st.selectbox(
        "Report",
        list(report_options.keys())
    )


    dataframe = report_options[
        report_name
    ]


    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )


    csv_data = dataframe.to_csv(
        index=False
    ).encode()


    st.download_button(
        "⬇️ Download CSV",
        csv_data,
        report_name
        .lower()
        .replace(" ", "_")
        + ".csv",
        "text/csv"
    )


    if REPORTLAB_OK:

        pdf_data = pdf(
            report_name,
            dataframe
        )


        st.download_button(
            "📄 Download PDF",
            pdf_data,
            report_name
            .lower()
            .replace(" ", "_")
            + ".pdf",
            "application/pdf"
        )


# ============================================================
# HR OVERVIEW
# ============================================================

def overview():

    employees = edf()

    performance_data = performance()

    attendance_data = attendance()


    st.markdown(
        """
        <div class="hero">

            <strong>
                HR Workforce &amp;
                Performance Management
            </strong>

            <span>
                Workforce insights for HR review,
                development and operational visibility.
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


    active_employees = int(
        (
            employees["Status"]
            == "Active"
        ).sum()
    )


    average_achievement = (
        performance_data[
            "Achievement %"
        ].mean()
        if len(performance_data)
        else 0
    )


    attendance_rate = (
        attendance_data[
            "Status"
        ]
        .isin(
            [
                "Present",
                "Work From Home"
            ]
        )
        .mean()
        * 100
        if len(attendance_data)
        else 0
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Active Employees",
        active_employees
    )


    col2.metric(
        "Performance Records",
        len(performance_data)
    )


    col3.metric(
        "Avg Achievement",
        f"{average_achievement:.1f}%"
    )


    col4.metric(
        "Attendance Rate",
        f"{attendance_rate:.1f}%"
    )


    st.subheader(
        "📈 Performance Trend"
    )


    if len(performance_data):

        trend = (
            performance_data
            .groupby("Period")[
                "Achievement %"
            ]
            .mean()
        )


        st.line_chart(
            trend
        )


    st.subheader(
        "🏆 Department Snapshot"
    )


    if len(performance_data):

        department_summary = (

            performance_data

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
        "This application is decision-support software; "
        "HR should use human review for employment decisions."
    )


# ============================================================
# EMPLOYEE MANAGEMENT
# ============================================================

def employees():

    st.title(
        "👥 Employee Management"
    )


    dataframe = edf()


    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )


    with st.expander(
        "➕ Add Employee"
    ):

        departments = q(
            """
            SELECT *
            FROM departments
            ORDER BY name
            """,
            fetch=True
        )


        with st.form(
            "add_employee"
        ):

            col1, col2 = st.columns(2)


            code = col1.text_input(
                "Employee Code"
            )


            name = col2.text_input(
                "Full Name"
            )


            email = col1.text_input(
                "Email"
            )


            phone = col2.text_input(
                "Phone"
            )


            department = col1.selectbox(
                "Department",
                [
                    item["name"]
                    for item in departments
                ]
            )


            designation = col2.text_input(
                "Designation"
            )


            joining = col1.date_input(
                "Joining Date",
                date.today()
            )


            manager = col2.text_input(
                "Manager"
            )


            location = col1.text_input(
                "Location"
            )


            submitted = st.form_submit_button(
                "Create Employee",
                type="primary"
            )


            if submitted:

                try:

                    department_id = next(

                        item["id"]

                        for item in departments

                        if item["name"]
                        == department

                    )


                    q(
                        """
                        INSERT INTO employees(
                            code,
                            name,
                            email,
                            phone,
                            dept_id,
                            designation,
                            joining,
                            manager,
                            location
                        )
                        VALUES(
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?
                        )
                        """,
                        (
                            code,
                            name,
                            email,
                            phone,
                            department_id,
                            designation,
                            joining.isoformat(),
                            manager,
                            location,
                        )
                    )


                    st.success(
                        "Employee created."
                    )


                    st.rerun()


                except Exception as error:

                    st.error(
                        str(error)
                    )


# ============================================================
# EMPLOYEE DASHBOARD
# ============================================================

def employee_view():

    employee_id = (
        st.session_state.eid
    )


    employee = q(
        """
        SELECT

            e.*,

            d.name AS dept

        FROM employees e

        LEFT JOIN departments d
            ON e.dept_id = d.id

        WHERE e.id = ?
        """,
        (employee_id,),
        fetch=True
    )[0]


    performance_data = performance()


    performance_data = performance_data[
        performance_data[
            "Employee Code"
        ]
        == employee["code"]
    ]


    attendance_data = attendance()


    attendance_data = attendance_data[
        attendance_data[
            "Employee Code"
        ]
        == employee["code"]
    ]


    st.markdown(
        f"""
        <div class="hero">

            <strong>
                Welcome, {employee["name"]}
            </strong>

            <span>
                {employee["designation"]}
                •
                {employee["dept"]}
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Performance Records",
        len(performance_data)
    )


    col2.metric(
        "Avg Achievement",
        (
            f"{performance_data['Achievement %'].mean():.1f}%"
            if len(performance_data)
            else "0%"
        )
    )


    col3.metric(
        "Attendance Rate",
        (
            f"{attendance_data.Status.isin(['Present','Work From Home']).mean()*100:.1f}%"
            if len(attendance_data)
            else "0%"
        )
    )


    st.dataframe(
        performance_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.get(
        "auth"
    ):

        login()

        return


    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    st.sidebar.title(
        "👥 HR Workforce Pro"
    )


    st.sidebar.caption(
        f"Signed in as **{st.session_state.user}**"
    )


    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()


    # ========================================================
    # HR ADMIN
    # ========================================================

    if (
        st.session_state.role
        == "HR Admin"
    ):

        page = st.sidebar.radio(
            "Navigation",
            [
                "🏠 HR Overview",
                "👥 Employees",
                "📊 Performance",
                "📅 Attendance",
                "🎯 Goals",
                "📝 Leave Records",
                "📄 Reports",
            ]
        )


        if page == "🏠 HR Overview":

            overview()


        elif page == "👥 Employees":

            employees()


        elif page == "📊 Performance":

            performance_page()


        elif page == "📅 Attendance":

            attendance_page()


        elif page == "🎯 Goals":

            goals_page()


        elif page == "📝 Leave Records":

            leave_page()


        elif page == "📄 Reports":

            reports()


    # ========================================================
    # EMPLOYEE
    # ========================================================

    else:

        page = st.sidebar.radio(
            "Navigation",
            [
                "🏠 My Overview",
                "📊 My Performance",
                "📅 My Attendance",
                "🎯 My Goals",
                "📄 My Report",
            ]
        )


        employee_view()


        employee_id = (
            st.session_state.eid
        )


        employee_code = q(
            """
            SELECT code
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
            fetch=True
        )[0]["code"]


        if page == "📊 My Performance":

            dataframe = performance()

            dataframe = dataframe[
                dataframe[
                    "Employee Code"
                ]
                == employee_code
            ]

            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True
            )


        elif page == "📅 My Attendance":

            dataframe = attendance()

            dataframe = dataframe[
                dataframe[
                    "Employee Code"
                ]
                == employee_code
            ]

            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True
            )


        elif page == "🎯 My Goals":

            dataframe = goals()

            dataframe = dataframe[
                dataframe[
                    "Employee Code"
                ]
                == employee_code
            ]

            st.dataframe(
                dataframe,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# START APPLICATION
# ============================================================

init()

main()
