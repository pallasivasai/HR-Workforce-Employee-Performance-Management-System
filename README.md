# 📊 Marketing Sales & Employee Performance Dashboard

A professional **Marketing Sales Analytics + Employee Performance Dashboard** built with **Python, Pandas, Streamlit, Excel and ReportLab**.

This project is designed to analyze sales performance, compare targets vs actual sales, track employee achievement, identify target gaps, analyze brands, monitor new customers, and generate employee performance reports.

---

## 🚀 Live Project

> Add your Streamlit Cloud URL here after deployment.

**Live Demo:** `https://your-app-name.streamlit.app`

---

## 🎯 Project Overview

The dashboard combines **Sales Analytics** and **Employee Performance Analytics** into one interactive web application.

It helps management/HR teams answer questions such as:

- How much total sales were generated?
- How many orders and customers were handled?
- What is the total target?
- How much of the target was achieved?
- Did an employee reach the assigned target?
- Which employees are performing above/below target?
- What is the monthly target vs actual sales?
- What is the target gap?
- Which brands generated the most sales?
- How many new customers were acquired?
- Can an employee performance report be downloaded as PDF?

---

## ✨ Key Features

### 📌 Dashboard Overview

Provides high-level business KPIs:

- 💰 Total Sales
- 📦 Total Orders
- 👥 Customers
- 💵 Profit
- 🎯 Total Target
- 📊 Achievement %
- 🎯 Target Gap

Large currency values are displayed without unnecessary truncation.

---

### 🎯 Target Achievement Tracking

The application dynamically calculates:

**Achievement %**

```text
Achievement % = (Actual Sales / Target) × 100
```

**Target Reach**

```text
If Achievement >= 100% → YES
If Achievement < 100%  → NO
```

**Target Status**

```text
Achievement >= 100% → ✅ TARGET REACHED
Achievement < 100%  → ❌ NOT REACHED
```

This means target status is calculated from the actual sales and target data instead of being manually entered.

---

### 👥 Employee Performance Analytics

For each marketing employee, the dashboard provides:

- Total Target
- Achieved Sales
- Overall Achievement %
- Months Target Reached
- Months Missed
- Monthly Target
- Monthly Sales
- Achievement %
- Target Gap
- Target Reach
- Target Status
- Target vs Actual chart
- Achievement trend chart

---

### 🏆 Employee Performance Ranking

Admin users can compare employees using:

- Rank
- Employee
- Total Target
- Total Sales
- Achievement %
- Target Reach
- Status

Employees are ranked based on achievement percentage.

---

### 📈 Monthly Target vs Sales

The dashboard provides a month-wise comparison between:

- Assigned Target
- Actual Sales

This makes it easier to identify months where performance exceeded or fell below expectations.

---

### 🆕 New Customer Analytics

The dashboard tracks:

- New Customers
- New Customer Sales

Customer information is read from the `Merge1` Excel sheet.

---

### 🏷️ Brand-wise Sales

The dashboard provides brand-level analysis using the `MAKE TARGET` sheet.

It can show:

- Brand
- Sales
- Target
- Achievement %

---

### 📄 PDF Employee Performance Report

The application can generate downloadable employee performance reports containing:

- Employee name
- Total target
- Total sales
- Target gap
- Overall achievement
- Number of months target was reached
- Month-wise performance
- Target Reach
- Target Status

PDF generation is handled using **ReportLab**.

---

## 🔐 Role-Based Login

The application includes role-based access.

### Administrator / HR

Admin can:

- View overall dashboard
- Select marketing employees
- Upload Excel data
- View employee rankings
- Analyze employee performance

### Marketing Employee

Marketing users see data associated with their assigned marketing profile.

---

## 📁 Excel Data Structure

The application works with an Excel workbook containing these sheets:

```text
Marketing_Sales_Dashboard_Data.xlsx
│
├── MAIN_COPY
├── MARKETING TARGET
├── MAKE TARGET
└── Merge1
```

### MAIN_COPY

Main sales transaction data.

Required columns:

```text
Date
MARK
make
HELPER
Value
CUSTOMER NAME
```

Additional columns can include:

```text
City
Order ID
```

---

### MARKETING TARGET

Contains monthly targets for each marketing employee.

Example:

| Marketing Person | APR | MAY | JUN |
|---|---:|---:|---:|
| Ashok Marketing | 1800000 | 1800000 | 1800000 |
| Suresh - Marketing | 1600000 | 1600000 | 1600000 |
| H O - Marketing | 1400000 | 1400000 | 1400000 |
| Ramu Marketing | 2000000 | 2000000 | 2000000 |

The dashboard compares these targets against actual sales.

---

### MAKE TARGET

Contains brand-level target information.

Example:

```text
Make       Target
SAMSUNG    450000
APPLE      400000
LG         300000
SONY       250000
ONEPLUS    300000
DELL       250000
HP         250000
LENOVO     250000
```

---

### Merge1

Contains customer information used for new-customer analysis.

Required column:

```text
CUSTOMER NAME
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Interactive web dashboard |
| Pandas | Data processing and analytics |
| OpenPyXL | Excel reading |
| ReportLab | PDF report generation |
| Excel | Business data source |
| GitHub | Source code management |
| Streamlit Cloud | Free deployment |

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run saleswepapp_final.py
```

---

## 📋 Requirements

Create a `requirements.txt` file containing:

```text
streamlit>=1.40
pandas>=2.2
openpyxl>=3.1
reportlab>=4.0
```

---

## ☁️ Streamlit Cloud Deployment

1. Push the project to GitHub.
2. Open Streamlit Cloud.
3. Create a new application.
4. Select the GitHub repository.
5. Select:

```text
saleswepapp_final.py
```

6. Deploy the application.
7. Make sure `requirements.txt` is present in the repository.

The Excel workbook should also be available to the application according to the project's upload/data workflow.

---

## 🔑 Demo Login

The current application contains demo credentials for testing.

### Administrator / HR

```text
Username: admin
Password: admin@123
```

### Marketing Employee

```text
Username: ashok
Password: ashok@123
```

```text
Username: suresh
Password: suresh@123
```

```text
Username: ho
Password: ho@123
```

> For a production deployment, replace demo passwords with secure authentication and do not commit real credentials to GitHub.

---

## 📊 Example Performance Logic

Suppose an employee has:

```text
Monthly Target = ₹20,00,000
Actual Sales   = ₹12,00,000
```

Then:

```text
Achievement = (12,00,000 / 20,00,000) × 100
            = 60%
```

Dashboard result:

```text
Achievement % → 60%
Target Reach  → NO
Status        → ❌ NOT REACHED
```

If actual sales become:

```text
₹22,00,000
```

Then:

```text
Achievement = 110%
Target Reach = YES
Status = ✅ TARGET REACHED
```

---

## 🧑‍💼 HR Analytics Use Case

This project demonstrates how HR/management can use business data to understand employee performance.

The dashboard provides **objective performance metrics** such as:

- Target achievement
- Monthly performance
- Sales contribution
- Target gap
- Performance ranking
- Consistency across months

These metrics can support human review and performance discussions.

> The dashboard is an analytics tool and should not be used as the sole basis for employment decisions.

---

## 📈 Business Value

This project demonstrates practical skills in:

- Data cleaning
- Data transformation
- KPI development
- Target vs actual analysis
- Employee performance analytics
- Business intelligence
- Dashboard development
- Excel integration
- Role-based access
- PDF reporting
- Cloud deployment

---

## 🧠 Skills Demonstrated

### Programming

- Python
- Pandas
- Streamlit

### Data & Database Concepts

- Data cleaning
- Data validation
- Aggregation
- GroupBy analysis
- KPI calculation
- Target achievement analysis

### Business Analytics

- Sales analysis
- Employee performance
- Target tracking
- Customer analytics
- Brand analysis

### Deployment

- GitHub
- Streamlit Cloud
- Requirements management

---

## 🗂️ Suggested Repository Structure

```text
marketing-sales-dashboard/
│
├── saleswepapp_final.py
├── Marketing_Sales_Dashboard_Data.xlsx
├── requirements.txt
├── README.md
│
└── fonts/
    ├── DejaVuSans.ttf
    └── DejaVuSans-Bold.ttf
```

---

## 🔮 Future Improvements

Possible future enhancements:

- Interactive date filters
- Advanced charts using Plotly
- Sales forecasting
- Monthly performance alerts
- Automated email reports
- Database integration with MySQL/PostgreSQL
- Secure authentication
- User management
- Export performance data to Excel
- Advanced HR analytics
- Attendance/productivity integration
- Real-time sales data integration

---

## 👨‍💻 Project Author

**P Siva Sai**

Multidisciplinary technology professional with interests and experience across:

- Software Engineering
- Database & SQL
- Data Analytics
- Web Development
- Cybersecurity
- Technical Recruitment
- HR
- Teaching
- Freelance Projects

---

## ⭐ Project Purpose

This project was developed as a practical portfolio project to demonstrate how **sales data can be transformed into actionable business and employee-performance insights through an interactive dashboard.**

If you find the project useful, consider giving the repository a ⭐ on GitHub.
