# 👥 HR Workforce Pro

### HR Workforce & Employee Performance Management System

HR Workforce Pro is a database-driven HR management and analytics application built with **Python, Streamlit, SQLite, Pandas, OpenPyXL, and ReportLab**.

It combines employee management, performance, attendance, goals, leave management, Employee 360, employee self-service, HR analytics, and reporting in one application.

## 🚀 Project Overview

This project demonstrates practical **Python + SQL/database + analytics + business application development**.

### Core Modules

- 🔐 Secure Login & Role-Based Access
- 🏠 HR Overview Dashboard
- 👥 Employee Management
- 👤 Employee 360
- 📊 Performance Management
- 📅 Attendance Management
- 🎯 Goal Management
- 📝 Leave Management
- 📄 HR Reports
- 📥 HR Data Center
- 👨‍💻 Employee Self-Service
- 📊 Excel / CSV / PDF Reporting

## 🔐 Authentication & Roles

The application supports HR Admin and Employee experiences.

### HR Admin Demo
```text
Username: admin
Password: admin@123
```

### Employee Demo
```text
Username: employee
Password: employee@123
```

Passwords are stored as hashes, and authentication data is intentionally excluded from exported HR workbooks.

## 🏠 HR Overview Dashboard

The overview provides workforce-level KPIs and analytics including:

- Active Employees
- Performance Records
- Average Achievement
- Attendance Rate
- Performance Trend
- Department Performance
- Target Achievement

Attendance rate considers records marked **Present** or **Work From Home**.

## 👥 Employee Management

Employee records include:

- Employee ID
- Employee Code
- Full Name
- Email
- Phone
- Department
- Designation
- Joining Date
- Employment Status
- Manager
- Location

## 👤 Employee 360

Employee 360 provides a consolidated employee view combining:

- Profile information
- Department
- Performance
- Attendance
- Goals
- Leave history

## 📊 Performance Management

The performance module supports:

- Performance records
- Achievement %
- Target Reach
- Performance trends
- Employee-level analysis
- Department-level performance

The dashboard calculates average achievement and target-reach metrics.

## 📅 Attendance Management

Attendance records can be maintained, reviewed, analyzed, and exported for HR reporting.

Attendance contributes to the workforce attendance KPI and Employee Self-Service view.

## 🎯 Goal Management

Goals are associated with employees and can be reviewed alongside performance information to provide a broader view of employee progress.

## 📝 Leave Management

Supported leave types include:

- Casual Leave
- Sick Leave
- Earned Leave
- Work From Home
- Other

Leave submissions include:

- Employee
- Leave Type
- Start Date
- End Date
- Reason
- Number of Days
- Status

New submissions are recorded with a **Pending** status.

## 👨‍💻 Employee Self-Service

Employees can access their own HR information through:

- 🏠 My Overview
- 📊 My Performance
- 📅 My Attendance
- 🎯 My Goals
- 📄 My Report

The employee view filters information using the logged-in employee identity.

Employees can also generate/download their performance PDF report.

## 📄 HR Reports

Available reports:

- Employee Directory
- Performance Report
- Attendance Report
- Goals Report
- Leave Report

Reports can be viewed and downloaded as:

- CSV
- PDF

PDF reports are generated using ReportLab.

## 📥 HR Data Center

The Data Center provides an Excel export containing separate worksheets for:

- Employees
- Performance
- Attendance
- Goals
- Leave Records
- Departments

The workbook intentionally excludes usernames and password hashes.

## 🗄️ Database Architecture

The application uses SQLite as the relational database.

Core tables/entities:

```text
users
employees
departments
attendance
performance
goals
leave_records
```

### Relationship Overview

```text
Departments
     │
     └── Employees
            ├── Performance
            ├── Attendance
            ├── Goals
            └── Leave Records

Users
  └── Authentication / Role Access
```

## 🔎 SQL & Database Concepts

The project demonstrates database-driven development using concepts such as:

- SELECT
- INSERT
- WHERE
- ORDER BY
- JOIN
- LEFT JOIN
- Aggregation
- Filtering
- Parameterized Queries
- Relational Data Modeling

Example:

```sql
SELECT
    e.*,
    d.name AS department
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.id
WHERE e.id = ?;
```

## 🐍 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application UI |
| SQLite | Relational database |
| SQL | Database queries |
| Pandas | Data processing & analytics |
| OpenPyXL | Excel generation |
| ReportLab | PDF reporting |
| Git | Version control |
| GitHub | Source code hosting |

## 🔐 Security Considerations

The project includes:

- Role-based access
- Password hashing
- Parameterized SQL queries
- Employee-specific data filtering
- Authentication data excluded from exports

> This is a portfolio/demo application. Production deployment would require additional controls such as stronger authentication, secret management, audit logging, session hardening, and a production-grade database.

## 📁 Suggested Project Structure

```text
HR-Workforce-Pro/
│
├── app.py
├── hr_workforce.db
├── HR_Workforce_Data.xlsx
├── requirements.txt
└── README.md
```

## ▶️ Run Locally

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd <YOUR-PROJECT-FOLDER>
pip install -r requirements.txt
streamlit run app.py
```

## 💼 Business Use Cases

HR Workforce Pro can be used for:

- Workforce monitoring
- Employee performance reviews
- Attendance analysis
- Goal tracking
- Leave management
- Department performance analysis
- Employee 360 reviews
- HR reporting
- Workforce data export
- Employee self-service

## 🎯 What This Project Demonstrates

### Software Engineering
- Python development
- Streamlit application development
- Modular application design
- Forms and session state
- Authentication workflows

### SQL & Database
- Relational database design
- SQL queries
- Table relationships
- JOIN operations
- Parameterized queries
- Database-driven applications

### Data Analytics
- Pandas
- KPI calculations
- Aggregation
- Trend analysis
- HR analytics
- Business reporting

### Reporting
- Excel generation
- CSV export
- PDF generation
- Employee reports
- HR reporting workflows

## 🌐 Project Links

### 💻 GitHub
**Add the exact HR Workforce Pro repository URL here:**
```text
https://github.com/pallasivasai/HR-Workforce-Employee-Performance-Management-System
```

### 🚀 Live Application
**Add the deployed Streamlit URL here:**
```text
https://hr-workforce-employee-performance-management-system.streamlit.app/
```

## 👨‍💻 About the Developer

**Palla Siva Sai**

Areas of interest:

- Software Engineering
- Python Development
- SQL & Database Development
- Data Analytics
- AI-Assisted Software Development
- Cybersecurity
- HR Technology
- Technical Recruitment

## 🔗 Connect

- **LinkedIn:** https://www.linkedin.com/in/pallasivasai/
- **GitHub:** https://github.com/pallasivasai/

## 🚀 Future Enhancements

Potential enhancements:

- PostgreSQL / MySQL support
- Advanced SQL analytics
- Automated email notifications
- Leave approval workflow
- Audit logs
- Advanced permissions
- Advanced employee search
- Scheduled reports
- API integration
- Cloud database deployment
- Advanced authentication

---

## ⭐ Project Summary

```text
HR Management
      +
SQL / Database
      +
Python
      +
Data Analytics
      +
Reporting
      +
Employee Self-Service
      =
HR Workforce Pro
```

**Built as a practical portfolio project demonstrating database-driven software development, HR analytics, SQL, Python, Streamlit, and reporting automation.**

**Build • Learn • Analyze • Improve 🚀**
