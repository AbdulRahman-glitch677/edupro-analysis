"""
EduPro - Learner Demographics & Course Enrollment Behavior Analysis
Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_raw, build_master, AGE_LABELS

st.set_page_config(page_title="EduPro Analytics", page_icon="graduation cap", layout="wide")

st.markdown("""
<style>
    .metric-card{background:#f0f4ff;border-radius:12px;padding:18px 24px;text-align:center;}
    .metric-val {font-size:2rem;font-weight:700;color:#1a56db;}
    .metric-lbl {font-size:.85rem;color:#6b7280;margin-top:4px;}
    .section-hdr{border-left:4px solid #1a56db;padding-left:10px;margin:24px 0 12px;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    users, courses, txns = load_raw()
    return build_master(users, courses, txns)


master = get_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("EduPro Analytics")
    st.markdown("---")

    sel_ages    = st.multiselect("Age Group",       AGE_LABELS,
                                 default=AGE_LABELS)
    sel_genders = st.multiselect("Gender",          sorted(master["Gender"].dropna().unique()),
                                 default=sorted(master["Gender"].dropna().unique()))
    sel_cats    = st.multiselect("Course Category", sorted(master["CourseCategory"].dropna().unique()),
                                 default=sorted(master["CourseCategory"].dropna().unique()))
    sel_levels  = st.multiselect("Course Level",    ["Beginner", "Intermediate", "Advanced"],
                                 default=["Beginner", "Intermediate", "Advanced"])

    st.markdown("---")
    st.caption("EduPro - Learner Intelligence Dashboard")

# ── Apply filters ──────────────────────────────────────────────────────────────
df = master[
    master["AgeGroup"].astype(str).isin(sel_ages) &
    master["Gender"].isin(sel_genders) &
    master["CourseCategory"].isin(sel_cats) &
    master["CourseLevel"].isin(sel_levels)
].copy()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## EduPro - Learner Demographics & Enrollment Analysis")
st.markdown("Descriptive learner intelligence across demographics, course categories, and skill levels.")
st.markdown("---")

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total_enroll    = len(df)
unique_learners = df["UserID"].nunique()
courses_per_user = df.groupby("UserID")["CourseID"].count()
avg_courses     = round(courses_per_user.mean(), 1) if total_enroll else 0
top_cat         = df["CourseCategory"].value_counts().idxmax() if total_enroll else "N/A"
female_pct      = (
    f"{df['Gender'].value_counts(normalize=True).get('Female', 0) * 100:.0f}% F"
    if total_enroll else "N/A"
)


def kpi(col, val, lbl):
    col.markdown(
        f'<div class="metric-card"><div class="metric-val">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )


k1, k2, k3, k4, k5 = st.columns(5)
kpi(k1, f"{total_enroll:,}",    "Total Enrollments")
kpi(k2, f"{unique_learners:,}", "Unique Learners")
kpi(k3, f"{avg_courses}",       "Avg Courses / Learner")
kpi(k4, top_cat,                "Top Category")
kpi(k5, female_pct,             "Female Participation")

st.markdown("")

if total_enroll == 0:
    st.warning("No data matches the current filters. Please adjust the sidebar selections.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 - Learner Demographics
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>1 - Learner Demographics</b></p>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    age_cnt = (
        df.groupby("AgeGroup", observed=True)["UserID"]
        .nunique().reset_index(name="Unique Learners")
    )
    age_cnt.columns = ["Age Group", "Unique Learners"]
    fig1 = px.bar(
        age_cnt, x="Age Group", y="Unique Learners",
        color="Age Group", text="Unique Learners",
        title="Unique Learners by Age Group",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        category_orders={"Age Group": AGE_LABELS},
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    gender_cnt = (
        df.groupby("Gender")["UserID"]
        .nunique().reset_index(name="Unique Learners")
    )
    fig2 = px.pie(
        gender_cnt, names="Gender", values="Unique Learners",
        title="Gender Distribution of Learners",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4,
    )
    fig2.update_traces(textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 - Enrollment Distribution
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>2 - Enrollment Distribution</b></p>', unsafe_allow_html=True)
c3, c4, c5 = st.columns(3)

with c3:
    cat_enroll = (
        df.groupby("CourseCategory").size()
        .reset_index(name="Enrollments")
        .sort_values("Enrollments")
    )
    fig3 = px.bar(
        cat_enroll, x="Enrollments", y="CourseCategory", orientation="h",
        color="Enrollments", title="Enrollments by Course Category",
        color_continuous_scale="Blues",
    )
    fig3.update_layout(
        yaxis={"categoryorder": "total ascending"},
        yaxis_title="Category",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    type_enroll = df.groupby("CourseType").size().reset_index(name="Enrollments")
    fig4 = px.pie(
        type_enroll, names="CourseType", values="Enrollments",
        title="Enrollments by Course Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.35,
    )
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    level_order = ["Beginner", "Intermediate", "Advanced"]
    level_enroll = (
        df.groupby("CourseLevel").size()
        .reindex(level_order).fillna(0)
        .reset_index(name="Enrollments")
    )
    fig5 = px.funnel(
        level_enroll, x="Enrollments", y="CourseLevel",
        title="Enrollments by Course Level",
        color_discrete_sequence=["#1a56db", "#3b82f6", "#93c5fd"],
    )
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 - Demographics x Course Preferences
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>3 - Demographics x Course Preferences</b></p>', unsafe_allow_html=True)
c6, c7 = st.columns(2)

with c6:
    heat_data = (
        df.groupby(["AgeGroup", "CourseCategory"], observed=True)
        .size().reset_index(name="Enrollments")
    )
    pivot = (
        heat_data
        .pivot(index="AgeGroup", columns="CourseCategory", values="Enrollments")
        .fillna(0)
        .reindex(index=[a for a in AGE_LABELS if a in heat_data["AgeGroup"].astype(str).values])
    )
    fig6 = px.imshow(
        pivot, text_auto=True, aspect="auto",
        color_continuous_scale="Blues",
        title="Age Group x Course Category Heatmap",
    )
    fig6.update_layout(xaxis_title="Course Category", yaxis_title="Age Group")
    st.plotly_chart(fig6, use_container_width=True)

with c7:
    gender_level = (
        df.groupby(["Gender", "CourseLevel"])
        .size().reset_index(name="Enrollments")
    )
    fig7 = px.bar(
        gender_level, x="CourseLevel", y="Enrollments",
        color="Gender", barmode="group",
        category_orders={"CourseLevel": ["Beginner", "Intermediate", "Advanced"]},
        title="Gender x Course Level Preferences",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig7.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 - Behavioral Insights
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>4 - Behavioral Insights</b></p>', unsafe_allow_html=True)
c8, c9 = st.columns(2)

with c8:
    age_cat = (
        df.groupby(["AgeGroup", "CourseCategory"], observed=True)
        .size().reset_index(name="Enrollments")
    )
    fig8 = px.bar(
        age_cat, x="AgeGroup", y="Enrollments",
        color="CourseCategory", barmode="stack",
        title="Enrollment Volume by Age Group & Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        category_orders={"AgeGroup": AGE_LABELS},
    )
    fig8.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Age Group")
    st.plotly_chart(fig8, use_container_width=True)

with c9:
    enroll_per_user = (
        df.groupby("UserID")["CourseID"]
        .count().reset_index(name="CoursesEnrolled")
    )
    fig9 = px.histogram(
        enroll_per_user, x="CoursesEnrolled", nbins=20,
        title="Distribution: Courses Enrolled per Learner",
        color_discrete_sequence=["#1a56db"],
    )
    fig9.update_layout(plot_bgcolor="rgba(0,0,0,0)", bargap=0.1, xaxis_title="Courses Enrolled")
    st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 - Enrollment Trend Over Time
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>5 - Enrollment Trend Over Time</b></p>', unsafe_allow_html=True)

trend = (
    df.assign(Month=pd.to_datetime(df["TransactionDate"]).dt.to_period("M").astype(str))
    .groupby(["Month", "CourseCategory"])
    .size().reset_index(name="Enrollments")
    .sort_values("Month")
)
fig10 = px.line(
    trend, x="Month", y="Enrollments", color="CourseCategory",
    title="Monthly Enrollment Trend by Course Category",
    color_discrete_sequence=px.colors.qualitative.Vivid,
)
fig10.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Month")
st.plotly_chart(fig10, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 - Age Group vs Course Level Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr"><b>6 - Age Group vs Course Level Deep Dive</b></p>', unsafe_allow_html=True)
c10, c11 = st.columns(2)

with c10:
    age_level = (
        df.groupby(["AgeGroup", "CourseLevel"], observed=True)
        .size().reset_index(name="Enrollments")
    )
    fig11 = px.bar(
        age_level, x="AgeGroup", y="Enrollments",
        color="CourseLevel", barmode="group",
        category_orders={
            "AgeGroup": AGE_LABELS,
            "CourseLevel": ["Beginner", "Intermediate", "Advanced"],
        },
        title="Age Group vs Course Level",
        color_discrete_sequence=["#93c5fd", "#3b82f6", "#1a56db"],
    )
    fig11.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Age Group")
    st.plotly_chart(fig11, use_container_width=True)

with c11:
    age_type = (
        df.groupby(["AgeGroup", "CourseType"], observed=True)
        .size().reset_index(name="Enrollments")
    )
    fig12 = px.bar(
        age_type, x="AgeGroup", y="Enrollments",
        color="CourseType", barmode="group",
        category_orders={"AgeGroup": AGE_LABELS},
        title="Age Group vs Course Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig12.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Age Group")
    st.plotly_chart(fig12, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 - Raw Data Explorer
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("Explore Filtered Data"):
    display_cols = [
        "UserID", "Age", "AgeGroup", "Gender",
        "CourseName", "CourseCategory", "CourseType", "CourseLevel",
        "TransactionDate",
    ]
    st.dataframe(
        df[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=320,
    )
    st.download_button(
        "Download CSV",
        df[display_cols].to_csv(index=False).encode("utf-8"),
        "edupro_filtered.csv",
        "text/csv",
    )

st.markdown("---")
st.caption("EduPro Learner Intelligence Dashboard - Built with Streamlit & Plotly")
