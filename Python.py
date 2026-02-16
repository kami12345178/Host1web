import tkinter as tk
from tkinter import messagebox
from datetime import datetime, time
import sqlite3

# ==============================
# DATABASE SETUP
# ==============================
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Employees Login Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    id TEXT PRIMARY KEY,
    name TEXT,
    password TEXT
)
""")

# Employee Full Details Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employee_details(
    id TEXT PRIMARY KEY,
    name TEXT,
    department TEXT,
    cnic TEXT,
    phone TEXT,
    address TEXT,
    joining_date TEXT
)
""")

# Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id TEXT,
    name TEXT,
    date TEXT,
    time TEXT,
    status TEXT
)
""")

# Admin Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()

# ==============================
# DEFAULT DATA
# ==============================
default_staff = [
    ("E001","Ahmed Khan","1234"),
    ("E002","Ali Raza","1234"),
]

for emp in default_staff:
    cursor.execute("INSERT OR IGNORE INTO employees VALUES (?, ?, ?)", emp)

cursor.execute("INSERT OR IGNORE INTO admins VALUES ('admin1','admin123')")
conn.commit()

# ==============================
# TIME SETTINGS
# ==============================
start_time = time(9, 0)
late_cutoff = time(9, 30)

# ==============================
# EMPLOYEE ATTENDANCE
# ==============================
def mark_attendance():
    emp_id = eid_entry.get().strip()
    pwd = pwd_entry.get().strip()

    cursor.execute("SELECT name FROM employees WHERE id=? AND password=?",
                   (emp_id, pwd))
    result = cursor.fetchone()

    if result:
        name = result[0]
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        cursor.execute("SELECT * FROM attendance WHERE id=? AND date=?",
                       (emp_id, today))
        if cursor.fetchone():
            messagebox.showinfo("Info", "Attendance already marked today")
            return

        if now.time() <= start_time:
            status = "Present"
        elif now.time() <= late_cutoff:
            status = "Late"
        else:
            status = "Absent"

        cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?, ?)",
                       (emp_id, name, today, current_time, status))
        conn.commit()

        messagebox.showinfo("Success", f"{name} marked {status}")
        eid_entry.delete(0, tk.END)
        pwd_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Invalid ID or Password")

# ==============================
# FULL EMPLOYEE JOINING FORM
# ==============================
def employee_joining_form():

    join_win = tk.Toplevel()
    join_win.title("Full Employee Joining Form")
    join_win.geometry("400x500")
    join_win.config(bg="#f3e5f5")

    tk.Label(join_win, text="Employee Joining Form",
             font=("Arial",16,"bold"),
             bg="#f3e5f5").pack(pady=10)

    fields = [
        "Employee ID",
        "Full Name",
        "Password",
        "Department",
        "CNIC",
        "Phone",
        "Address"
    ]

    entries = {}

    for field in fields:
        tk.Label(join_win, text=field, bg="#f3e5f5").pack()
        entry = tk.Entry(join_win, width=30)
        entry.pack(pady=3)
        entries[field] = entry

    def register_employee():
        emp_id = entries["Employee ID"].get().strip()
        name = entries["Full Name"].get().strip()
        password = entries["Password"].get().strip()
        department = entries["Department"].get().strip()
        cnic = entries["CNIC"].get().strip()
        phone = entries["Phone"].get().strip()
        address = entries["Address"].get().strip()
        joining_date = datetime.now().strftime("%Y-%m-%d")

        if "" in [emp_id,name,password,department,cnic,phone,address]:
            messagebox.showerror("Error","All fields required")
            return

        try:
            # Insert login record
            cursor.execute("INSERT INTO employees VALUES (?,?,?)",
                           (emp_id,name,password))

            # Insert full details
            cursor.execute("""
            INSERT INTO employee_details VALUES (?,?,?,?,?,?,?)
            """,(emp_id,name,department,cnic,phone,address,joining_date))

            conn.commit()
            messagebox.showinfo("Success","Employee Registered Successfully")
            join_win.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error","Employee ID already exists")

    tk.Button(join_win, text="Register Employee",
              bg="#8e24aa", fg="white",
              width=25,
              command=register_employee).pack(pady=15)

# ==============================
# ADMIN DASHBOARD
# ==============================
def admin_dashboard():

    dash = tk.Toplevel()
    dash.title("Admin Dashboard")
    dash.geometry("800x500")
    dash.config(bg="#e8f5e9")

    tk.Label(dash, text="Admin Dashboard",
             font=("Arial",16,"bold"),
             bg="#e8f5e9").pack(pady=10)

    # View Attendance
    def view_attendance():
        win = tk.Toplevel(dash)
        win.title("All Attendance Records")
        win.geometry("800x400")

        headers = ["ID", "Name", "Date", "Time", "Status"]
        for col, h in enumerate(headers):
            tk.Label(win, text=h, width=15,
                     bg="#2e7d32", fg="white",
                     relief="solid").grid(row=0, column=col)

        cursor.execute("SELECT * FROM attendance")
        records = cursor.fetchall()

        for row, record in enumerate(records, start=1):
            for col, value in enumerate(record):
                tk.Label(win, text=value, width=15,
                         relief="solid").grid(row=row, column=col)

    # View Employee Details
    def view_employees():
        win = tk.Toplevel(dash)
        win.title("Employee Details")
        win.geometry("900x400")

        headers = ["ID","Name","Department","CNIC","Phone","Address","Joining"]
        for col, h in enumerate(headers):
            tk.Label(win, text=h, width=15,
                     bg="#6a1b9a", fg="white",
                     relief="solid").grid(row=0, column=col)

        cursor.execute("SELECT * FROM employee_details")
        records = cursor.fetchall()

        for row, record in enumerate(records, start=1):
            for col, value in enumerate(record):
                tk.Label(win, text=value, width=15,
                         relief="solid").grid(row=row, column=col)

    tk.Button(dash, text="View All Attendance",
              bg="#2e7d32", fg="white",
              width=25,
              command=view_attendance).pack(pady=10)

    tk.Button(dash, text="View Employee Details",
              bg="#6a1b9a", fg="white",
              width=25,
              command=view_employees).pack(pady=10)

# ==============================
# ADMIN LOGIN
# ==============================
def admin_login_page():
    root.withdraw()

    admin_root = tk.Toplevel()
    admin_root.title("Admin Login")
    admin_root.geometry("400x300")
    admin_root.config(bg="#fff3e0")

    tk.Label(admin_root, text="Admin Login",
             font=("Arial",16,"bold"),
             bg="#fff3e0").pack(pady=20)

    tk.Label(admin_root, text="Username", bg="#fff3e0").pack()
    user_entry = tk.Entry(admin_root)
    user_entry.pack()

    tk.Label(admin_root, text="Password", bg="#fff3e0").pack()
    pass_entry = tk.Entry(admin_root, show="*")
    pass_entry.pack()

    def verify_admin():
        username = user_entry.get().strip()
        password = pass_entry.get().strip()

        cursor.execute("SELECT * FROM admins WHERE username=? AND password=?",
                       (username, password))
        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Success", "Admin Login Successful")
            admin_root.destroy()
            admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def back():
        admin_root.destroy()
        root.deiconify()

    tk.Button(admin_root, text="Login",
              bg="#ef6c00", fg="white",
              width=20, command=verify_admin).pack(pady=10)

    tk.Button(admin_root, text="Back",
              bg="#9e9e9e", fg="white",
              width=20, command=back).pack()

# ==============================
# MAIN WINDOW
# ==============================
root = tk.Tk()
root.title("Employee Attendance System")
root.geometry("400x450")
root.config(bg="#e3f2fd")

tk.Label(root, text="Employee Attendance",
         font=("Arial",16,"bold"),
         bg="#e3f2fd").pack(pady=15)

tk.Label(root, text="Employee ID", bg="#e3f2fd").pack()
eid_entry = tk.Entry(root)
eid_entry.pack()

tk.Label(root, text="Password", bg="#e3f2fd").pack()
pwd_entry = tk.Entry(root, show="*")
pwd_entry.pack()

tk.Button(root, text="Mark Attendance",
          bg="#1976D2", fg="white",
          width=20, command=mark_attendance).pack(pady=10)

tk.Button(root, text="New Employee Joining",
          bg="#7b1fa2", fg="white",
          width=20, command=employee_joining_form).pack(pady=5)

tk.Button(root, text="Admin Login",
          bg="#d32f2f", fg="white",
          width=20, command=admin_login_page).pack(pady=10)

root.mainloop()