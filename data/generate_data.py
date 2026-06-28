"""
Generate synthetic EduPro dataset matching the spreadsheet schema.
Run once to produce edupro_data.xlsx in the data/ folder.
"""
import pandas as pd
import numpy as np
import os

rng = np.random.default_rng(42)

# ── Users ──────────────────────────────────────────────────────────────────
N_USERS = 1000
ages = rng.integers(15, 65, N_USERS)
genders = rng.choice(["Male", "Female", "Non-binary"], N_USERS, p=[0.48, 0.48, 0.04])

users = pd.DataFrame({
    "UserID":   [f"U{i:04d}" for i in range(1, N_USERS + 1)],
    "UserName": [f"User_{i}" for i in range(1, N_USERS + 1)],
    "Age":      ages,
    "Gender":   genders,
})

# ── Courses ─────────────────────────────────────────────────────────────────
categories = ["Technology", "Business", "Arts", "Science", "Health", "Language", "Mathematics"]
types      = ["Video", "Live", "Self-paced", "Hybrid"]
levels     = ["Beginner", "Intermediate", "Advanced"]

N_COURSES = 120
courses = pd.DataFrame({
    "CourseID":       [f"C{i:03d}" for i in range(1, N_COURSES + 1)],
    "CourseName":     [f"Course_{i}" for i in range(1, N_COURSES + 1)],
    "CourseCategory": rng.choice(categories, N_COURSES),
    "CourseType":     rng.choice(types,      N_COURSES),
    "CourseLevel":    rng.choice(levels,     N_COURSES, p=[0.45, 0.35, 0.20]),
})

# ── Transactions ─────────────────────────────────────────────────────────────
N_TX = 5000
tx_users   = rng.choice(users["UserID"],   N_TX)
tx_courses = rng.choice(courses["CourseID"], N_TX)
dates = pd.to_datetime("2022-01-01") + pd.to_timedelta(rng.integers(0, 730, N_TX), unit="D")

transactions = pd.DataFrame({
    "TransactionID":  [f"T{i:05d}" for i in range(1, N_TX + 1)],
    "UserID":         tx_users,
    "CourseID":       tx_courses,
    "TransactionDate": dates,
})

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "edupro_data.xlsx")
with pd.ExcelWriter(out, engine="openpyxl") as w:
    users.to_excel(w,        sheet_name="Users",        index=False)
    courses.to_excel(w,      sheet_name="Courses",      index=False)
    transactions.to_excel(w, sheet_name="Transactions", index=False)

print(f"Dataset saved: {out}")
