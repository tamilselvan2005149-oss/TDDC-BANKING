"""
TDDC BANKING ENTERPRISE
"""

import sqlite3
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
DB_PATH = "tddc_bank.db"
random.seed(42)
np.random.seed(42)

BRANCH_NAMES = ["Salem Main", "Chennai Anna Nagar", "Coimbatore RS Puram",
                "Madurai Central", "Trichy Junction", "Erode Town"]
ACCOUNT_TYPES = ["Savings", "Current", "Salary", "NRI", "MSME", "Senior Citizen"]
TXN_MODES = ["UPI", "NEFT", "RTGS", "IMPS", "ATM", "Cash Deposit"]
DEPARTMENTS = ["Operations", "Loans", "Customer Service", "IT", "Compliance", "HR"]
DESIGNATIONS = ["Clerk", "Officer", "Senior Officer", "Branch Manager", "Assistant Manager"]
TN_DISTRICTS = ["Salem", "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli",
                "Erode", "Tirunelveli", "Vellore", "Thanjavur", "Dindigul",
                "Namakkal", "Karur", "Cuddalore", "Kanchipuram"]

# --- Tamil Nadu style name pools -------------------------------------
TAMIL_MALE_FIRST = [
    "Arun", "Karthik", "Vignesh", "Suriya", "Dinesh", "Bala", "Ganesan",
    "Muthu", "Sivakumar", "Raja", "Prabhu", "Selvam", "Manikandan",
    "Sundar", "Elango", "Kumaresan", "Ramesh", "Saravanan", "Vetri",
    "Ashok", "Senthil", "Vijay", "Kavin", "Nandhakumar", "Boopathi",
    "Loganathan", "Murugan", "Pandiyan", "Rajesh", "Gopinath",
    "Anbarasan", "Thiagarajan", "Velmurugan", "Yogesh", "Sathish",
    "Naveen", "Prakash", "Jeyakumar", "Chandran", "Palanisamy",
]
TAMIL_FEMALE_FIRST = [
    "Priya", "Kavya", "Meena", "Deepa", "Lakshmi", "Kalaivani", "Divya",
    "Nithya", "Revathi", "Anitha", "Sudha", "Vani", "Malar", "Selvi",
    "Poornima", "Vasanthi", "Gayathri", "Bhuvana", "Shanthi", "Uma",
    "Radha", "Saranya", "Dhanalakshmi", "Karpagam", "Mala", "Jothi",
    "Amudha", "Rani", "Sowmya", "Yamuna", "Indira", "Parvathi",
    "Thenmozhi", "Vidya", "Abirami", "Chitra", "Geetha", "Pushpa",
    "Sangeetha", "Kamakshi",
]
TAMIL_SURNAMES = [
    "Pillai", "Gounder", "Naidu", "Chettiar", "Iyer", "Iyengar",
    "Nadar", "Mudaliar", "Thevar", "Reddiar", "Rajan", "Subramaniam",
    "Krishnan", "Natarajan", "Balasubramaniam", "Ramaswamy",
    "Venkataraman", "Ayyappan", "Marimuthu", "Perumal",
]


def tamil_name(gender):
    first = random.choice(TAMIL_MALE_FIRST if gender == "Male" else TAMIL_FEMALE_FIRST)
    last = random.choice(TAMIL_SURNAMES)
    return f"{first} {last}"


def random_gender():
    return random.choices(["Male", "Female"], weights=[51, 49])[0]


def random_phone():
    return f"9{random.randint(100000000, 999999999)}"


def random_email(name):
    handle = name.lower().replace(" ", ".") + str(random.randint(1, 999))
    return f"{handle}@example.com"


st.set_page_config(page_title="TDDC BANKING ENTERPRISE", layout="wide", page_icon="🏦")

# ----------------------------------------------------------------------
# DATABASE LAYER
# ----------------------------------------------------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS branches (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT, branch_code TEXT, ifsc TEXT,
        district TEXT, state TEXT, manager TEXT, status TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_name TEXT, gender TEXT, department TEXT, designation TEXT,
        branch_id INTEGER, joining_date TEXT, salary REAL,
        performance_score REAL, status TEXT,
        FOREIGN KEY(branch_id) REFERENCES branches(branch_id))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS attendance (
        att_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER, att_date TEXT, status TEXT,
        login_time TEXT, logout_time TEXT,
        FOREIGN KEY(emp_id) REFERENCES employees(emp_id))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS customers (
        cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cust_name TEXT, gender TEXT, cif_number TEXT, account_number TEXT,
        account_type TEXT, branch_id INTEGER, balance REAL,
        phone TEXT, email TEXT, kyc_status TEXT, risk_score REAL,
        created_on TEXT, status TEXT,
        FOREIGN KEY(branch_id) REFERENCES branches(branch_id))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cust_id INTEGER, txn_date TEXT, txn_mode TEXT,
        txn_type TEXT, amount REAL, status TEXT,
        FOREIGN KEY(cust_id) REFERENCES customers(cust_id))""")

    conn.commit()
    conn.close()


def seed_data(n_branches=6, n_employees=60, n_customers=500, n_txns=2500):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM branches")
    if cur.fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    # Branches
    for i in range(n_branches):
        cur.execute("""INSERT INTO branches (branch_name, branch_code, ifsc, district, state, manager, status)
            VALUES (?,?,?,?,?,?,?)""",
            (BRANCH_NAMES[i % len(BRANCH_NAMES)] + f" #{i+1}", f"BR{1000+i}",
             f"TDDC000{1000+i}", random.choice(TN_DISTRICTS), "Tamil Nadu",
             tamil_name(random_gender()), "Active"))
    conn.commit()

    branch_ids = [r[0] for r in cur.execute("SELECT branch_id FROM branches").fetchall()]

    # Employees
    for _ in range(n_employees):
        gender = random_gender()
        name = tamil_name(gender)
        join_date = datetime.now().date() - timedelta(days=random.randint(1, 6 * 365))
        cur.execute("""INSERT INTO employees (emp_name, gender, department, designation, branch_id,
            joining_date, salary, performance_score, status) VALUES (?,?,?,?,?,?,?,?,?)""",
            (name, gender, random.choice(DEPARTMENTS), random.choice(DESIGNATIONS),
             random.choice(branch_ids), join_date.isoformat(),
             round(random.uniform(25000, 95000), 2),
             round(random.uniform(50, 100), 1), "Active"))
    conn.commit()

    emp_ids = [r[0] for r in cur.execute("SELECT emp_id FROM employees").fetchall()]

    # Attendance (last 14 days per employee)
    for emp_id in emp_ids:
        for d in range(14):
            att_date = (datetime.now() - timedelta(days=d)).date()
            status = random.choices(["Present", "Absent", "Half Day", "Leave"],
                                     weights=[80, 5, 10, 5])[0]
            login = f"{random.randint(8,10)}:{random.randint(0,59):02d}" if status != "Absent" else ""
            logout = f"{random.randint(17,19)}:{random.randint(0,59):02d}" if status != "Absent" else ""
            cur.execute("""INSERT INTO attendance (emp_id, att_date, status, login_time, logout_time)
                VALUES (?,?,?,?,?)""", (emp_id, att_date.isoformat(), status, login, logout))
    conn.commit()

    # Customers (500, Tamil Nadu names, with gender)
    for _ in range(n_customers):
        gender = random_gender()
        name = tamil_name(gender)
        created = datetime.now().date() - timedelta(days=random.randint(1, 3 * 365))
        cur.execute("""INSERT INTO customers (cust_name, gender, cif_number, account_number, account_type,
            branch_id, balance, phone, email, kyc_status, risk_score, created_on, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (name, gender, f"CIF{random.randint(100000,999999)}",
             f"{random.randint(10**11,10**12-1)}", random.choice(ACCOUNT_TYPES),
             random.choice(branch_ids), round(random.uniform(500, 500000), 2),
             random_phone(), random_email(name),
             random.choices(["Verified", "Pending"], weights=[85, 15])[0],
             round(random.uniform(0, 100), 1), created.isoformat(), "Active"))
    conn.commit()

    cust_ids = [r[0] for r in cur.execute("SELECT cust_id FROM customers").fetchall()]

    # Transactions (last 120 days, so "monthly" reports have a few months of data)
    for _ in range(n_txns):
        txn_date = datetime.now() - timedelta(days=random.randint(0, 120),
                                               hours=random.randint(0, 23))
        mode = random.choice(TXN_MODES)
        # Occasionally inject an unusually large amount to simulate anomalies
        if random.random() < 0.02:
            amount = round(random.uniform(300000, 900000), 2)
        else:
            amount = round(random.uniform(100, 100000), 2)
        cur.execute("""INSERT INTO transactions (cust_id, txn_date, txn_mode, txn_type, amount, status)
            VALUES (?,?,?,?,?,?)""",
            (random.choice(cust_ids), txn_date.isoformat(), mode,
             random.choice(["Credit", "Debit"]), amount,
             random.choices(["Success", "Pending", "Failed"], weights=[92, 5, 3])[0]))
    conn.commit()
    conn.close()


def df_query(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def run_action(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# INIT
# ----------------------------------------------------------------------
init_db()
seed_data()

# ----------------------------------------------------------------------
# SIDEBAR NAV
# ----------------------------------------------------------------------
st.sidebar.title("🏦 TDDC BANKING ENTERPRISE")
st.sidebar.caption("Simulation / demo platform — not a real bank system")
page = st.sidebar.radio("Navigate", [
    "Dashboard", "Customers", "Employees", "Attendance",
    "Branches", "Transactions", "Analytics",
    "Account Summaries", "Monthly Transaction Reports",
    "Customer Activity Analysis", "Unusual Transaction Detection",
])

if st.sidebar.button("🔄 Reset Demo Data"):
    run_action("DELETE FROM transactions")
    run_action("DELETE FROM customers")
    run_action("DELETE FROM attendance")
    run_action("DELETE FROM employees")
    run_action("DELETE FROM branches")
    seed_data()
    st.sidebar.success("Demo data regenerated.")
    st.rerun()

# ----------------------------------------------------------------------
# DASHBOARD
# ----------------------------------------------------------------------
if page == "Dashboard":
    st.title("Enterprise Dashboard")

    n_cust = df_query("SELECT COUNT(*) c FROM customers").c[0]
    n_emp = df_query("SELECT COUNT(*) c FROM employees").c[0]
    n_branch = df_query("SELECT COUNT(*) c FROM branches").c[0]
    total_bal = df_query("SELECT SUM(balance) b FROM customers").b[0] or 0
    today = datetime.now().date().isoformat()
    txns_today = df_query("SELECT COUNT(*) c FROM transactions WHERE txn_date LIKE ?",
                           (today + "%",)).c[0]
    present_today = df_query("SELECT COUNT(*) c FROM attendance WHERE att_date=? AND status='Present'",
                              (today,)).c[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{n_cust:,}")
    c2.metric("Total Employees", f"{n_emp:,}")
    c3.metric("Total Branches", f"{n_branch:,}")
    c4.metric("Deposit Portfolio (₹)", f"{total_bal:,.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Transactions Today", f"{txns_today:,}")
    c6.metric("Employees Present Today", f"{present_today:,}")
    pending_kyc = df_query("SELECT COUNT(*) c FROM customers WHERE kyc_status='Pending'").c[0]
    c7.metric("Pending KYC", f"{pending_kyc:,}")
    failed_txn = df_query("SELECT COUNT(*) c FROM transactions WHERE status='Failed'").c[0]
    c8.metric("Failed Transactions", f"{failed_txn:,}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        df_mode = df_query("SELECT txn_mode, COUNT(*) as count FROM transactions GROUP BY txn_mode")
        fig = px.pie(df_mode, names="txn_mode", values="count", title="Transactions by Mode")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_acc = df_query("SELECT account_type, COUNT(*) as count FROM customers GROUP BY account_type")
        fig2 = px.bar(df_acc, x="account_type", y="count", title="Customers by Account Type")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        df_gender_c = df_query("SELECT gender, COUNT(*) as count FROM customers GROUP BY gender")
        fig3 = px.pie(df_gender_c, names="gender", values="count", title="Customer Gender Distribution",
                      color="gender", color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        df_gender_e = df_query("SELECT gender, COUNT(*) as count FROM employees GROUP BY gender")
        fig4 = px.pie(df_gender_e, names="gender", values="count", title="Employee Gender Distribution",
                      color="gender", color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"})
        st.plotly_chart(fig4, use_container_width=True)

# ----------------------------------------------------------------------
# CUSTOMERS
# ----------------------------------------------------------------------
elif page == "Customers":
    st.title("Customer Management")

    tab1, tab2 = st.tabs(["📋 View / Search", "➕ Add Customer"])

    with tab1:
        search = st.text_input("Search by name, CIF, or account number")
        query = "SELECT * FROM customers"
        params = ()
        if search:
            query += " WHERE cust_name LIKE ? OR cif_number LIKE ? OR account_number LIKE ?"
            params = tuple(f"%{search}%" for _ in range(3))
        df = df_query(query, params)
        st.dataframe(df, use_container_width=True, height=400)

        st.subheader("Update / Delete")
        if not df.empty:
            sel = st.selectbox("Select Customer ID", df["cust_id"])
            colu, cold = st.columns(2)
            with colu:
                new_status = st.selectbox("Status", ["Active", "Frozen", "Closed"])
                if st.button("Update Status"):
                    run_action("UPDATE customers SET status=? WHERE cust_id=?", (new_status, sel))
                    st.success("Updated.")
                    st.rerun()
            with cold:
                if st.button("Delete Customer", type="secondary"):
                    run_action("DELETE FROM customers WHERE cust_id=?", (sel,))
                    st.warning("Deleted.")
                    st.rerun()

    with tab2:
        with st.form("add_customer"):
            gender = st.selectbox("Gender", ["Male", "Female"])
            name = st.text_input("Customer Name", value=tamil_name(gender))
            acc_type = st.selectbox("Account Type", ACCOUNT_TYPES)
            branches = df_query("SELECT branch_id, branch_name FROM branches")
            branch_choice = st.selectbox("Branch", branches["branch_name"])
            balance = st.number_input("Opening Balance", min_value=0.0, value=1000.0)
            phone = st.text_input("Phone", value=random_phone())
            email = st.text_input("Email")
            submitted = st.form_submit_button("Create Customer")
            if submitted and name:
                branch_id = int(branches[branches.branch_name == branch_choice].branch_id.iloc[0])
                run_action("""INSERT INTO customers (cust_name, gender, cif_number, account_number, account_type,
                    branch_id, balance, phone, email, kyc_status, risk_score, created_on, status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (name, gender, f"CIF{random.randint(100000,999999)}",
                     f"{random.randint(10**11,10**12-1)}", acc_type, branch_id, balance,
                     phone, email or random_email(name), "Pending", round(random.uniform(0, 100), 1),
                     datetime.now().date().isoformat(), "Active"))
                st.success(f"Customer '{name}' created.")

# ----------------------------------------------------------------------
# EMPLOYEES
# ----------------------------------------------------------------------
elif page == "Employees":
    st.title("Employee Management")
    tab1, tab2 = st.tabs(["📋 View / Search", "➕ Add Employee"])

    with tab1:
        dept_filter = st.multiselect("Filter by Department", DEPARTMENTS)
        query = "SELECT * FROM employees"
        if dept_filter:
            placeholders = ",".join("?" * len(dept_filter))
            query += f" WHERE department IN ({placeholders})"
            df = df_query(query, tuple(dept_filter))
        else:
            df = df_query(query)
        st.dataframe(df, use_container_width=True, height=400)

        if not df.empty:
            sel = st.selectbox("Select Employee ID", df["emp_id"])
            score = st.slider("Update Performance Score", 0.0, 100.0, 75.0)
            if st.button("Update Performance"):
                run_action("UPDATE employees SET performance_score=? WHERE emp_id=?", (score, sel))
                st.success("Updated.")
                st.rerun()

    with tab2:
        with st.form("add_employee"):
            gender = st.selectbox("Gender", ["Male", "Female"])
            name = st.text_input("Employee Name", value=tamil_name(gender))
            dept = st.selectbox("Department", DEPARTMENTS)
            desig = st.selectbox("Designation", DESIGNATIONS)
            branches = df_query("SELECT branch_id, branch_name FROM branches")
            branch_choice = st.selectbox("Branch", branches["branch_name"])
            salary = st.number_input("Salary", min_value=0.0, value=30000.0)
            submitted = st.form_submit_button("Add Employee")
            if submitted and name:
                branch_id = int(branches[branches.branch_name == branch_choice].branch_id.iloc[0])
                run_action("""INSERT INTO employees (emp_name, gender, department, designation, branch_id,
                    joining_date, salary, performance_score, status) VALUES (?,?,?,?,?,?,?,?,?)""",
                    (name, gender, dept, desig, branch_id, datetime.now().date().isoformat(),
                     salary, 75.0, "Active"))
                st.success(f"Employee '{name}' added.")

# ----------------------------------------------------------------------
# ATTENDANCE
# ----------------------------------------------------------------------
elif page == "Attendance":
    st.title("Employee Attendance")
    date_sel = st.date_input("Select Date", datetime.now().date())
    df = df_query("""SELECT a.att_id, e.emp_name, e.gender, e.department, a.status, a.login_time, a.logout_time
                      FROM attendance a JOIN employees e ON a.emp_id = e.emp_id
                      WHERE a.att_date = ?""", (date_sel.isoformat(),))
    st.dataframe(df, use_container_width=True, height=400)

    if not df.empty:
        counts = df["status"].value_counts().reset_index()
        counts.columns = ["status", "count"]
        fig = px.bar(counts, x="status", y="count", title=f"Attendance Summary — {date_sel}")
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# BRANCHES
# ----------------------------------------------------------------------
elif page == "Branches":
    st.title("Branch Management")
    tab1, tab2 = st.tabs(["📋 View", "➕ Add Branch"])

    with tab1:
        df = df_query("""SELECT b.*, 
            (SELECT COUNT(*) FROM customers c WHERE c.branch_id=b.branch_id) as customers,
            (SELECT COUNT(*) FROM employees e WHERE e.branch_id=b.branch_id) as employees
            FROM branches b""")
        st.dataframe(df, use_container_width=True, height=350)

    with tab2:
        with st.form("add_branch"):
            name = st.text_input("Branch Name")
            code = st.text_input("Branch Code")
            ifsc = st.text_input("IFSC Code")
            district = st.selectbox("District", TN_DISTRICTS)
            gender = st.selectbox("Manager Gender", ["Male", "Female"])
            manager = st.text_input("Branch Manager", value=tamil_name(gender))
            submitted = st.form_submit_button("Add Branch")
            if submitted and name:
                run_action("""INSERT INTO branches (branch_name, branch_code, ifsc, district, state,
                    manager, status) VALUES (?,?,?,?,?,?,?)""",
                    (name, code, ifsc, district, "Tamil Nadu", manager, "Active"))
                st.success(f"Branch '{name}' added.")

# ----------------------------------------------------------------------
# TRANSACTIONS
# ----------------------------------------------------------------------
elif page == "Transactions":
    st.title("Transaction Ledger")
    col1, col2, col3 = st.columns(3)
    mode_filter = col1.multiselect("Mode", TXN_MODES)
    status_filter = col2.multiselect("Status", ["Success", "Pending", "Failed"])
    days_back = col3.slider("Last N days", 1, 120, 30)

    cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
    query = """SELECT t.txn_id, c.cust_name, c.gender, t.txn_date, t.txn_mode, t.txn_type, t.amount, t.status
               FROM transactions t JOIN customers c ON t.cust_id = c.cust_id
               WHERE t.txn_date >= ?"""
    params = [cutoff]
    if mode_filter:
        query += f" AND t.txn_mode IN ({','.join('?'*len(mode_filter))})"
        params += mode_filter
    if status_filter:
        query += f" AND t.status IN ({','.join('?'*len(status_filter))})"
        params += status_filter
    query += " ORDER BY t.txn_date DESC"

    df = df_query(query, tuple(params))
    st.dataframe(df, use_container_width=True, height=450)
    st.caption(f"{len(df)} transactions | Total value: ₹{df['amount'].sum():,.2f}" if not df.empty else "No transactions found.")

# ----------------------------------------------------------------------
# ANALYTICS
# ----------------------------------------------------------------------
elif page == "Analytics":
    st.title("Executive Analytics")

    df_txn = df_query("SELECT txn_date, amount, txn_mode FROM transactions")
    df_txn["txn_date"] = pd.to_datetime(df_txn["txn_date"])
    df_txn["day"] = df_txn["txn_date"].dt.date

    daily = df_txn.groupby("day")["amount"].sum().reset_index()
    fig1 = px.line(daily, x="day", y="amount", title="Daily Transaction Volume (₹)")
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        df_branch = df_query("""SELECT b.branch_name, COUNT(c.cust_id) as customers
            FROM branches b LEFT JOIN customers c ON b.branch_id = c.branch_id
            GROUP BY b.branch_name""")
        fig2 = px.bar(df_branch, x="branch_name", y="customers", title="Customers per Branch")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        df_perf = df_query("SELECT department, AVG(performance_score) as avg_score FROM employees GROUP BY department")
        fig3 = px.bar(df_perf, x="department", y="avg_score", title="Avg Employee Performance by Department")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("CASA-style Ratio (Savings+Current vs Total)")
    df_acc = df_query("SELECT account_type, SUM(balance) as total FROM customers GROUP BY account_type")
    casa = df_acc[df_acc.account_type.isin(["Savings", "Current"])].total.sum()
    total = df_acc.total.sum()
    ratio = (casa / total * 100) if total else 0
    st.metric("CASA Ratio", f"{ratio:.1f}%")

    st.divider()
    st.subheader("Balance Distribution by Gender")
    df_bal_gender = df_query("SELECT gender, balance FROM customers")
    fig5 = px.box(df_bal_gender, x="gender", y="balance", color="gender",
                  title="Customer Balance Spread by Gender",
                  color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"})
    st.plotly_chart(fig5, use_container_width=True)

# ----------------------------------------------------------------------
# ACCOUNT SUMMARIES
# ----------------------------------------------------------------------
elif page == "Account Summaries":
    st.title("Account Summaries")

    branches = df_query("SELECT branch_id, branch_name FROM branches")
    branch_choice = st.selectbox("Filter by Branch (optional)", ["All"] + list(branches["branch_name"]))

    query = """SELECT c.cust_id, c.cust_name, c.gender, c.account_number, c.account_type,
               b.branch_name, c.balance, c.kyc_status, c.status,
               (SELECT COUNT(*) FROM transactions t WHERE t.cust_id = c.cust_id) as txn_count,
               (SELECT COALESCE(SUM(amount),0) FROM transactions t WHERE t.cust_id=c.cust_id AND t.txn_type='Credit') as total_credit,
               (SELECT COALESCE(SUM(amount),0) FROM transactions t WHERE t.cust_id=c.cust_id AND t.txn_type='Debit') as total_debit
               FROM customers c JOIN branches b ON c.branch_id = b.branch_id"""
    if branch_choice != "All":
        query += " WHERE b.branch_name = ?"
        df = df_query(query, (branch_choice,))
    else:
        df = df_query(query)

    st.dataframe(df, use_container_width=True, height=450)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accounts Shown", f"{len(df):,}")
    c2.metric("Total Balance (₹)", f"{df['balance'].sum():,.0f}")
    c3.metric("Avg Balance (₹)", f"{df['balance'].mean():,.0f}" if len(df) else "0")
    c4.metric("Avg Txns / Account", f"{df['txn_count'].mean():.1f}" if len(df) else "0")

    st.divider()
    df_type = df.groupby("account_type")["balance"].sum().reset_index()
    fig = px.bar(df_type, x="account_type", y="balance", title="Total Balance by Account Type")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# MONTHLY TRANSACTION REPORTS
# ----------------------------------------------------------------------
elif page == "Monthly Transaction Reports":
    st.title("Monthly Transaction Reports")

    df = df_query("SELECT txn_date, txn_mode, txn_type, amount, status FROM transactions")
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["month"] = df["txn_date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").agg(
        total_amount=("amount", "sum"),
        txn_count=("amount", "count"),
        avg_amount=("amount", "mean"),
        success_count=("status", lambda s: (s == "Success").sum()),
        failed_count=("status", lambda s: (s == "Failed").sum()),
    ).reset_index().sort_values("month")

    st.dataframe(monthly, use_container_width=True)

    fig1 = px.bar(monthly, x="month", y="total_amount", title="Total Transaction Value by Month (₹)")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(monthly, x="month", y="txn_count", title="Transaction Count by Month", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Mode Breakdown by Month")
    mode_month = df.groupby(["month", "txn_mode"])["amount"].sum().reset_index()
    fig3 = px.bar(mode_month, x="month", y="amount", color="txn_mode", barmode="stack",
                  title="Monthly Transaction Value by Mode")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Download Monthly Report")
    csv = monthly.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "monthly_transaction_report.csv", "text/csv")

# ----------------------------------------------------------------------
# CUSTOMER ACTIVITY ANALYSIS
# ----------------------------------------------------------------------
elif page == "Customer Activity Analysis":
    st.title("Customer Activity Analysis")

    df = df_query("""SELECT c.cust_id, c.cust_name, c.gender, c.account_type, c.balance,
                      t.txn_date, t.amount, t.txn_type, t.status
                      FROM customers c LEFT JOIN transactions t ON c.cust_id = t.cust_id""")
    df["txn_date"] = pd.to_datetime(df["txn_date"])

    activity = df.groupby(["cust_id", "cust_name", "gender", "account_type"]).agg(
        txn_count=("amount", "count"),
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
        last_txn=("txn_date", "max"),
    ).reset_index()

    activity["total_amount"] = activity["total_amount"].fillna(0)
    activity["avg_amount"] = activity["avg_amount"].fillna(0)

    days_inactive = (pd.Timestamp.now() - activity["last_txn"]).dt.days
    activity["days_since_last_txn"] = days_inactive
    activity["activity_level"] = pd.cut(
        activity["txn_count"], bins=[-1, 0, 3, 10, float("inf")],
        labels=["Inactive", "Low", "Moderate", "High"])

    st.dataframe(activity.sort_values("txn_count", ascending=False), use_container_width=True, height=450)

    col1, col2 = st.columns(2)
    with col1:
        lvl_counts = activity["activity_level"].value_counts().reset_index()
        lvl_counts.columns = ["activity_level", "count"]
        fig1 = px.pie(lvl_counts, names="activity_level", values="count", title="Customers by Activity Level")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        gender_activity = activity.groupby("gender")["txn_count"].mean().reset_index()
        fig2 = px.bar(gender_activity, x="gender", y="txn_count", title="Avg Transactions per Customer by Gender",
                      color="gender", color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 10 Most Active Customers")
    top10 = activity.sort_values("total_amount", ascending=False).head(10)
    fig3 = px.bar(top10, x="cust_name", y="total_amount", title="Top 10 Customers by Total Transaction Value (₹)")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Dormant / Inactive Customers (no transactions)")
    dormant = activity[activity["txn_count"] == 0][["cust_id", "cust_name", "gender", "account_type"]]
    st.dataframe(dormant, use_container_width=True, height=250)
    st.caption(f"{len(dormant)} customers with zero recorded transactions.")

# ----------------------------------------------------------------------
# UNUSUAL TRANSACTION DETECTION
# ----------------------------------------------------------------------
elif page == "Unusual Transaction Detection":
    st.title("Unusual Transaction Detection")
    st.caption("Simple statistical (z-score) based flagging — for demo/portfolio purposes only, "
               "not a production fraud/AML engine.")

    z_threshold = st.slider("Z-score threshold for flagging", 1.5, 5.0, 3.0, 0.1)
    large_txn_threshold = st.number_input("Also flag any single transaction above (₹)",
                                           min_value=10000.0, value=250000.0, step=10000.0)

    df = df_query("""SELECT t.txn_id, c.cust_name, c.gender, c.account_number, t.txn_date,
                      t.txn_mode, t.txn_type, t.amount, t.status
                      FROM transactions t JOIN customers c ON t.cust_id = c.cust_id""")

    if df.empty:
        st.info("No transactions available.")
    else:
        mean_amt = df["amount"].mean()
        std_amt = df["amount"].std() if df["amount"].std() > 0 else 1
        df["z_score"] = (df["amount"] - mean_amt) / std_amt

        flagged = df[(df["z_score"].abs() >= z_threshold) | (df["amount"] >= large_txn_threshold)].copy()
        flagged = flagged.sort_values("amount", ascending=False)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Transactions", f"{len(df):,}")
        c2.metric("Flagged as Unusual", f"{len(flagged):,}")
        c3.metric("Flag Rate", f"{(len(flagged)/len(df)*100):.2f}%")

        st.subheader("Flagged Transactions")
        st.dataframe(flagged[["txn_id", "cust_name", "gender", "account_number", "txn_date",
                               "txn_mode", "txn_type", "amount", "status", "z_score"]],
                     use_container_width=True, height=400)

        fig = px.scatter(df, x="txn_date", y="amount", color=(df["z_score"].abs() >= z_threshold),
                         title="Transaction Amounts Over Time (Flagged in Red)",
                         labels={"color": "Unusual"},
                         color_discrete_map={True: "#EF4444", False: "#94A3B8"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Flagged by Customer")
        by_cust = flagged.groupby("cust_name")["amount"].sum().reset_index().sort_values("amount", ascending=False).head(15)
        if not by_cust.empty:
            fig2 = px.bar(by_cust, x="cust_name", y="amount", title="Top Customers by Flagged Transaction Value (₹)")
            st.plotly_chart(fig2, use_container_width=True)

        csv = flagged.to_csv(index=False).encode("utf-8")
        st.download_button("Download Flagged Transactions CSV", csv, "unusual_transactions.csv", "text/csv")
