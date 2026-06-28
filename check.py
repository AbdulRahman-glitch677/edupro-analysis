import pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import load_raw, build_master, AGE_LABELS

u, c, t = load_raw()
print("Users cols:       ", list(u.columns))
print("Courses cols:     ", list(c.columns))
print("Transactions cols:", list(t.columns))

m = build_master(u, c, t)
print("Master shape:     ", m.shape)
print("AgeGroup cats:    ", list(m["AgeGroup"].cat.categories))
print("Nulls AgeGroup:   ", m["AgeGroup"].isna().sum())
print()

df = m.copy()

# KPIs
total_enroll    = len(df)
unique_learners = df["UserID"].nunique()
avg_courses     = round(df.groupby("UserID")["CourseID"].count().mean(), 1) if total_enroll else 0
top_cat         = df["CourseCategory"].value_counts().idxmax() if total_enroll else "N/A"
female_pct      = df["Gender"].value_counts(normalize=True).get("Female", 0) * 100
print(f"KPIs OK: enroll={total_enroll}, learners={unique_learners}, avg={avg_courses}, top={top_cat}, female={female_pct:.0f}%")

# S1
age_cnt = df.groupby("AgeGroup", observed=True)["UserID"].nunique().reset_index(name="Unique Learners")
age_cnt.columns = ["Age Group", "Unique Learners"]
gender_cnt = df.groupby("Gender")["UserID"].nunique().reset_index(name="Unique Learners")
print("S1 OK:", age_cnt.shape, gender_cnt.shape)

# S2
cat_enroll   = df.groupby("CourseCategory").size().reset_index(name="Enrollments").sort_values("Enrollments")
type_enroll  = df.groupby("CourseType").size().reset_index(name="Enrollments")
level_order  = ["Beginner", "Intermediate", "Advanced"]
level_enroll = df.groupby("CourseLevel").size().reindex(level_order).fillna(0).reset_index(name="Enrollments")
print("S2 OK:", cat_enroll.shape, type_enroll.shape, level_enroll.shape)
print("  level_enroll cols:", list(level_enroll.columns))
print("  level_enroll values:", level_enroll.to_dict("records"))

# S3
heat_data = df.groupby(["AgeGroup", "CourseCategory"], observed=True).size().reset_index(name="Enrollments")
pivot = heat_data.pivot(index="AgeGroup", columns="CourseCategory", values="Enrollments").fillna(0)
pivot = pivot.reindex(index=[a for a in AGE_LABELS if a in heat_data["AgeGroup"].astype(str).values])
print("S3 heatmap pivot:", pivot.shape, "index:", list(pivot.index))
gender_level = df.groupby(["Gender", "CourseLevel"]).size().reset_index(name="Enrollments")
print("S3 gender_level:", gender_level.shape)

# S4
age_cat         = df.groupby(["AgeGroup", "CourseCategory"], observed=True).size().reset_index(name="Enrollments")
enroll_per_user = df.groupby("UserID")["CourseID"].count().reset_index(name="CoursesEnrolled")
print("S4 OK:", age_cat.shape, enroll_per_user.shape)

# S5
trend = (
    df.assign(Month=pd.to_datetime(df["TransactionDate"]).dt.to_period("M").astype(str))
    .groupby(["Month", "CourseCategory"]).size().reset_index(name="Enrollments")
    .sort_values("Month")
)
print("S5 trend OK:", trend.shape)

# S6
age_level = df.groupby(["AgeGroup", "CourseLevel"], observed=True).size().reset_index(name="Enrollments")
age_type  = df.groupby(["AgeGroup", "CourseType"],  observed=True).size().reset_index(name="Enrollments")
print("S6 age_level:", age_level.shape, "age_type:", age_type.shape)

# Data explorer
cols = ["UserID", "Age", "AgeGroup", "Gender",
        "CourseName", "CourseCategory", "CourseType", "CourseLevel", "TransactionDate"]
sub = df[cols]
print("Data explorer OK:", sub.shape)

# Empty filter edge case
df_empty    = df.iloc[0:0].copy()
avg_empty   = round(df_empty.groupby("UserID")["CourseID"].count().mean(), 1) if len(df_empty) else 0
print("Empty filter edge case OK: avg=", avg_empty)

print()
print("ALL CHECKS PASSED")
