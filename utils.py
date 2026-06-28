"""Shared data loading, joining, and age-banding utilities."""
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "edupro_data.xlsx")

AGE_BINS   = [0, 17, 25, 35, 45, 100]
AGE_LABELS = ["<18", "18-25", "26-35", "36-45", "45+"]


def load_raw():
    xl = pd.read_excel(DATA_PATH, sheet_name=None, engine="openpyxl")
    users   = xl["Users"]
    courses = xl["Courses"]
    txns    = xl["Transactions"]
    return users, courses, txns


def build_master(users, courses, txns):
    df = (
        txns
        .merge(users,   on="UserID",   how="left")
        .merge(courses, on="CourseID", how="left")
    )
    df["AgeGroup"] = pd.cut(
        df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=True
    )
    return df
