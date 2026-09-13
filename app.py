
import hashlib
import sqlite3
from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

# Optional PDF support
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
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
# HR WORKFORCE PRO
# Uses the existing hr_workforce.db schema exactly.
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
# UI
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        .hero {
            padding: 28px 32px;
            border-radius: 18px;
            background: linear-gradient(135deg, #ff7a18, #e52e71);
            color: white;
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 38px;
            font-weight: 750;
            line-height: 1.15;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 17px;
            line-height: 1.5;
        }

        [data-testid="stMetricValue"] {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        .status-ok {
            color: #16803c;
            font-weight: 700;
        }

        .status-bad {
            color: #c62828;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def get_conn():
    if not DB_PATH.exists():
        st.error(
            "Database file 'hr_workforce.db' was not found. "
            "Upload it to the same GitHub repository as app.py."
        )
        st.stop()

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    return connection


def fetch_df(sql, params=()):
    connection = get_conn()
    try:
        return pd.read_sql_query(sql, connection, params=params)
    finally:
        connection.close()


def fetch_rows(sql, params=()):
    connection = get_conn()
    try:
        return [dict(row) for row in connection.execute(sql, params).fetchall()]
    finally:
        connection.close()


def execute(sql, params=()):
    connection = get_conn()
    try:
        cursor = connection.execute(sql, params)
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


# ============================================================
# PASSWORD
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# DATABASE VALIDATION
# ============================================================

def validate_database():
    required = {
        "departments",
        "employees",
        "users",
        "attendance",
        "performance",
        "goals",
        "leave_records",
    }

    connection = get_conn()
    try:
        actual = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        connection.close()

    missing = required - actual

    if missing:
        st.error(
            "The uploaded hr_workforce.db is missing these tables: "
            + ", ".join(sorted(missing))
        )
        st.stop()


# ============================================================
# HERO
# ============================================================

def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATA
# ============================================================

def employees_df():
    return fetch_df(
        """
        SELECT
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
        """
    )


def performance_df():
    return fetch_df(
        """
        SELECT
            e.employee_code AS "Employee Code",
            e.full_name AS "Employee",
            d.name AS "Department",
            p.period AS "Period",
            p.target AS "Target",
            p.achieved AS "Achieved",

            ROUND(
                CASE
                    WHEN COALESCE(p.target, 0) > 0
                    THEN p.achieved * 100.0 / p.target
                    ELSE 0
                END,
                2
            ) AS "Achievement %",

            CASE
                WHEN COALESCE(p.target, 0) > 0
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
        """
    )


def attendance_df():
    return fetch_df(
        """
        SELECT
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
        """
    )


def goals_df():
    return fetch_df(
        """
        SELECT
            e.employee_code AS "Employee Code",
            e.full_name AS "Employee",
            g.goal_title AS "Goal",
            g.target_value AS "Target",
            g.actual_value AS "Actual",

            ROUND(
                CASE
                    WHEN COALESCE(g.target_value, 0) > 0
                    THEN g.actual_value * 100.0 / g.target_value
                    ELSE 0
                END,
                2
            ) AS "Progress %",

            g.due_date AS "Due Date",
            g.status AS "Status"

        FROM goals g
        JOIN employees e
            ON g.employee_id = e.id

        ORDER BY
            g.due_date
        """
    )


def leave_df():
    return fetch_df(
        """
        SELECT
            e.employee_code AS "Employee Code",
            e.full_name AS "Employee",
            l.leave_type AS "Leave Type",
            l.start_date AS "Start Date",
            l.end_date AS "End Date",
            l.days AS "Days",
            l.status AS "Status",
            l.reason AS "Reason"

        FROM leave_records l
        JOIN employees e
            ON l.employee_id = e.id

        ORDER BY
            l.start_date DESC
        """
    )


# ============================================================
# PDF
# ============================================================

def create_pdf(title, dataframe):
    if not REPORTLAB_OK:
        return None

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )

    styles = getSampleStyleSheet()

    story = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 12),
    ]

    pdf_df = dataframe.head(100).copy()

    data = [list(pdf_df.columns)]
    data.extend(
        pdf_df.fillna("").astype(str).values.tolist()
    )

    table = Table(
        data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#243447"),
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
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
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
    hero(
        "HR Workforce Pro",
        "Employee Management • Performance • Attendance • Goals • HR Analytics",
    )

    _, center, _ = st.columns([1, 1.15, 1])

    with center:
        st.subheader("🔐 Secure Login")

        username = st.text_input(
            "Username",
            placeholder="Enter username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True,
        ):
            rows = fetch_rows(
                """
                SELECT *
                FROM users
                WHERE username = ?
                  AND password_hash = ?
                """,
                (
                    username.strip(),
                    hash_password(password),
                ),
            )

            if rows:
                user = rows[0]

                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.employee_id = user["employee_id"]

                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.info(
            """
**HR Admin**
- Username: `admin`
- Password: `admin@123`

**Employee**
- Username: `employee`
- Password: `employee@123`
            """
        )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():
    st.sidebar.title("👥 HR Workforce Pro")

    st.sidebar.caption(
        f"Signed in as **{st.session_state.username}**"
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "Logout",
        use_container_width=True,
    ):
        for key in [
            "authenticated",
            "username",
            "role",
            "employee_id",
        ]:
            st.session_state.pop(key, None)

        st.rerun()


# ============================================================
# HR OVERVIEW
# ============================================================

def hr_overview():
    hero(
        "HR Workforce & Performance Management",
        "Workforce insights, employee performance, attendance, goals and HR analytics.",
    )

    emp = employees_df()
    perf = performance_df()
    att = attendance_df()

    active = int(
        (emp["Status"].fillna("") == "Active").sum()
    )

    avg_achievement = (
        float(perf["Achievement %"].mean())
        if len(perf)
        else 0
    )

    target_reached = int(
        (perf["Target Reach"] == "YES").sum()
    )

    attendance_rate = (
        float(
            att["Status"]
            .isin(["Present", "Work From Home"])
            .mean()
            * 100
        )
        if len(att)
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Active Employees", active)
    c2.metric("Performance Records", len(perf))
    c3.metric("Avg Achievement", f"{avg_achievement:.1f}%")
    c4.metric("Attendance Rate", f"{attendance_rate:.1f}%")

    st.subheader("📈 Performance Trend")

    if len(perf):
        trend = (
            perf.groupby("Period")["Achievement %"]
            .mean()
            .round(2)
        )

        st.line_chart(trend)
    else:
        st.info("No performance records available.")

    st.subheader("🏆 Department Performance")

    if len(perf):
        summary = (
            perf.groupby("Department")
            .agg(
                Employees=("Employee", "nunique"),
                Avg_Achievement=("Achievement %", "mean"),
                Target_Reached=(
                    "Target Reach",
                    lambda x: int((x == "YES").sum()),
                ),
            )
            .reset_index()
        )

        summary["Avg_Achievement"] = summary[
            "Avg_Achievement"
        ].round(1)

        summary = summary.rename(
            columns={
                "Avg_Achievement": "Avg Achievement %",
                "Target_Reached": "Target Reached",
            }
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        f"Target-reached performance records: {target_reached}"
    )

    st.caption(
        "This dashboard supports HR review and development; employment decisions should include human review."
    )


# ============================================================
# EMPLOYEES
# ============================================================

def employee_management():
    st.title("👥 Employee Management")

    df = employees_df()

    search = st.text_input(
        "🔎 Search employee, code, email or department"
    )

    if search.strip():
        search_value = search.strip().lower()

        mask = (
            df.astype(str)
            .apply(
                lambda col: col.str.lower().str.contains(
                    search_value,
                    na=False,
                    regex=False,
                )
            )
            .any(axis=1)
        )

        df = df[mask]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    with st.expander("➕ Add Employee"):
        departments = fetch_rows(
            """
            SELECT id, name
            FROM departments
            ORDER BY name
            """
        )

        with st.form("add_employee"):
            c1, c2 = st.columns(2)

            employee_code = c1.text_input("Employee Code")
            full_name = c2.text_input("Full Name")

            email = c1.text_input("Email")
            phone = c2.text_input("Phone")

            department_name = c1.selectbox(
                "Department",
                [x["name"] for x in departments],
            )

            designation = c2.text_input("Designation")

            joining_date = c1.date_input(
                "Joining Date",
                value=date.today(),
            )

            manager = c2.text_input("Manager")
            location = c1.text_input("Location")

            submitted = st.form_submit_button(
                "Create Employee",
                type="primary",
            )

            if submitted:
                if not employee_code.strip():
                    st.error("Employee Code is required.")
                    return

                if not full_name.strip():
                    st.error("Full Name is required.")
                    return

                department_id = next(
                    x["id"]
                    for x in departments
                    if x["name"] == department_name
                )

                try:
                    execute(
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
                            phone.strip(),
                            department_id,
                            designation.strip(),
                            joining_date.isoformat(),
                            "Active",
                            manager.strip(),
                            location.strip(),
                        ),
                    )

                    st.success("Employee created successfully.")
                    st.rerun()

                except sqlite3.IntegrityError as error:
                    st.error(f"Could not create employee: {error}")


# ============================================================
# PERFORMANCE
# ============================================================

def performance_management():
    st.title("📊 Performance Management")

    df = performance_df()

    if len(df):
        c1, c2, c3 = st.columns(3)

        c1.metric("Records", len(df))
        c2.metric(
            "Average Achievement",
            f"{df['Achievement %'].mean():.1f}%"
        )
        c3.metric(
            "Target Reached",
            int((df["Target Reach"] == "YES").sum())
        )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("➕ Add / Update Performance")

    employee_list = fetch_rows(
        """
        SELECT id, employee_code, full_name
        FROM employees
        ORDER BY full_name
        """
    )

    with st.form("performance_form"):
        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['employee_code']} — {x['full_name']}"
                for x in employee_list
            ],
        )

        c1, c2, c3 = st.columns(3)

        period = c1.text_input(
            "Period",
            value="2026-04",
        )

        target = c2.number_input(
            "Target",
            min_value=0.0,
            value=100.0,
            step=10.0,
        )

        achieved = c3.number_input(
            "Achieved",
            min_value=0.0,
            value=0.0,
            step=10.0,
        )

        rating = st.slider(
            "Rating",
            min_value=0.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
        )

        comments = st.text_area("Comments")

        submitted = st.form_submit_button(
            "Save Performance",
            type="primary",
        )

        if submitted:
            selected = next(
                x
                for x in employee_list
                if (
                    f"{x['employee_code']} — {x['full_name']}"
                    == employee_label
                )
            )

            execute(
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

                ON CONFLICT(employee_id, period)
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
                    comments.strip(),
                ),
            )

            st.success("Performance saved successfully.")
            st.rerun()


# ============================================================
# ATTENDANCE
# ============================================================

def attendance_management():
    st.title("📅 Attendance Management")

    df = attendance_df()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    employee_list = fetch_rows(
        """
        SELECT id, employee_code, full_name
        FROM employees
        ORDER BY full_name
        """
    )

    with st.form("attendance_form"):
        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['employee_code']} — {x['full_name']}"
                for x in employee_list
            ],
        )

        attendance_date = st.date_input(
            "Date",
            value=date.today(),
        )

        status = st.selectbox(
            "Status",
            [
                "Present",
                "Absent",
                "Work From Home",
                "Leave",
            ],
        )

        notes = st.text_input("Notes")

        submitted = st.form_submit_button(
            "Save Attendance",
            type="primary",
        )

        if submitted:
            selected = next(
                x
                for x in employee_list
                if (
                    f"{x['employee_code']} — {x['full_name']}"
                    == employee_label
                )
            )

            execute(
                """
                INSERT INTO attendance(
                    employee_id,
                    attendance_date,
                    status,
                    notes
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(employee_id, attendance_date)
                DO UPDATE SET
                    status = excluded.status,
                    notes = excluded.notes
                """,
                (
                    selected["id"],
                    attendance_date.isoformat(),
                    status,
                    notes.strip(),
                ),
            )

            st.success("Attendance saved successfully.")
            st.rerun()


# ============================================================
# GOALS
# ============================================================

def goals_management():
    st.title("🎯 Goals & Target Tracking")

    df = goals_df()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    employee_list = fetch_rows(
        """
        SELECT id, employee_code, full_name
        FROM employees
        ORDER BY full_name
        """
    )

    with st.form("goal_form"):
        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['employee_code']} — {x['full_name']}"
                for x in employee_list
            ],
        )

        goal_title = st.text_input("Goal Title")

        c1, c2, c3 = st.columns(3)

        target_value = c1.number_input(
            "Target Value",
            min_value=0.0,
            value=100.0,
            step=10.0,
        )

        actual_value = c2.number_input(
            "Actual Value",
            min_value=0.0,
            value=0.0,
            step=10.0,
        )

        due_date = c3.date_input(
            "Due Date",
            value=date.today(),
        )

        status = st.selectbox(
            "Status",
            [
                "Not Started",
                "In Progress",
                "Completed",
                "On Hold",
            ],
        )

        submitted = st.form_submit_button(
            "Create Goal",
            type="primary",
        )

        if submitted:
            selected = next(
                x
                for x in employee_list
                if (
                    f"{x['employee_code']} — {x['full_name']}"
                    == employee_label
                )
            )

            execute(
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
                    goal_title.strip(),
                    target_value,
                    actual_value,
                    due_date.isoformat(),
                    status,
                ),
            )

            st.success("Goal created successfully.")
            st.rerun()


# ============================================================
# LEAVE
# ============================================================

def leave_management():
    st.title("📝 Leave Records")

    df = leave_df()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    employee_list = fetch_rows(
        """
        SELECT id, employee_code, full_name
        FROM employees
        ORDER BY full_name
        """
    )

    with st.form("leave_form"):
        employee_label = st.selectbox(
            "Employee",
            [
                f"{x['employee_code']} — {x['full_name']}"
                for x in employee_list
            ],
        )

        leave_type = st.selectbox(
            "Leave Type",
            [
                "Casual Leave",
                "Sick Leave",
                "Earned Leave",
                "Work From Home",
                "Other",
            ],
        )

        c1, c2 = st.columns(2)

        start_date = c1.date_input(
            "Start Date",
            value=date.today(),
        )

        end_date = c2.date_input(
            "End Date",
            value=date.today(),
        )

        reason = st.text_area("Reason")

        submitted = st.form_submit_button(
            "Submit Leave",
            type="primary",
        )

        if submitted:
            if end_date < start_date:
                st.error("End Date cannot be before Start Date.")
                return

            selected = next(
                x
                for x in employee_list
                if (
                    f"{x['employee_code']} — {x['full_name']}"
                    == employee_label
                )
            )

            days = (end_date - start_date).days + 1

            execute(
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
                    reason.strip(),
                ),
            )

            st.success("Leave submitted successfully.")
            st.rerun()


# ============================================================
# REPORTS
# ============================================================

def reports():
    st.title("📄 HR Reports")

    reports_map = {
        "Employee Directory": employees_df(),
        "Performance Report": performance_df(),
        "Attendance Report": attendance_df(),
        "Goals Report": goals_df(),
        "Leave Report": leave_df(),
    }

    selected_report = st.selectbox(
        "Select Report",
        list(reports_map.keys()),
    )

    df = reports_map[selected_report]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    filename = (
        selected_report
        .lower()
        .replace(" ", "_")
        + ".csv"
    )

    st.download_button(
        "⬇️ Download CSV",
        csv_data,
        file_name=filename,
        mime="text/csv",
    )

    if REPORTLAB_OK:
        pdf_data = create_pdf(
            selected_report,
            df,
        )

        st.download_button(
            "📄 Download PDF",
            pdf_data,
            file_name=filename.replace(
                ".csv",
                ".pdf",
            ),
            mime="application/pdf",
        )
    else:
        st.warning(
            "PDF support is unavailable because ReportLab is not installed."
        )


# ============================================================
# EMPLOYEE SELF SERVICE
# ============================================================

def employee_self_service():
    employee_id = st.session_state.employee_id

    employee_rows = fetch_rows(
        """
        SELECT
            e.*,
            d.name AS department
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.id
        WHERE e.id = ?
        """,
        (employee_id,),
    )

    if not employee_rows:
        st.error("Employee profile not found.")
        return

    employee = employee_rows[0]

    perf = performance_df()
    att = attendance_df()
    goals = goals_df()

    perf = perf[
        perf["Employee Code"]
        == employee["employee_code"]
    ]

    att = att[
        att["Employee Code"]
        == employee["employee_code"]
    ]

    goals = goals[
        goals["Employee Code"]
        == employee["employee_code"]
    ]

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 My Overview",
            "📊 My Performance",
            "📅 My Attendance",
            "🎯 My Goals",
            "📄 My Report",
        ],
    )

    hero(
        f"Welcome, {employee['full_name']}",
        f"{employee['designation']} • {employee['department']} • {employee['location']}",
    )

    if page == "🏠 My Overview":
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Performance Records",
            len(perf),
        )

        c2.metric(
            "Avg Achievement",
            (
                f"{perf['Achievement %'].mean():.1f}%"
                if len(perf)
                else "0%"
            ),
        )

        c3.metric(
            "Attendance Rate",
            (
                f"{att['Status'].isin(['Present', 'Work From Home']).mean() * 100:.1f}%"
                if len(att)
                else "0%"
            ),
        )

        st.subheader("📊 My Performance")

        st.dataframe(
            perf,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "📊 My Performance":
        st.subheader("📊 My Performance")

        st.dataframe(
            perf,
            use_container_width=True,
            hide_index=True,
        )

        if len(perf):
            st.line_chart(
                perf.set_index("Period")["Achievement %"]
            )

    elif page == "📅 My Attendance":
        st.subheader("📅 My Attendance")

        st.dataframe(
            att,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "🎯 My Goals":
        st.subheader("🎯 My Goals")

        st.dataframe(
            goals,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "📄 My Report":
        st.subheader("📄 My Performance Report")

        st.dataframe(
            perf,
            use_container_width=True,
            hide_index=True,
        )

        if REPORTLAB_OK:
            pdf_data = create_pdf(
                "Employee Performance Report",
                perf,
            )

            st.download_button(
                "📄 Download My PDF",
                pdf_data,
                file_name=(
                    f"{employee['employee_code']}_performance_report.pdf"
                ),
                mime="application/pdf",
            )


# ============================================================
# ADMIN
# ============================================================

def admin_dashboard():
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
        ],
    )

    if page == "🏠 HR Overview":
        hr_overview()

    elif page == "👥 Employees":
        employee_management()

    elif page == "📊 Performance":
        performance_management()

    elif page == "📅 Attendance":
        attendance_management()

    elif page == "🎯 Goals":
        goals_management()

    elif page == "📝 Leave Records":
        leave_management()

    elif page == "📄 Reports":
        reports()


# ============================================================
# MAIN
# ============================================================

def main():
    validate_database()

    if not st.session_state.get("authenticated", False):
        login_screen()
        return

    sidebar()

    if st.session_state.role == "HR Admin":
        admin_dashboard()
    else:
        employee_self_service()


main()
