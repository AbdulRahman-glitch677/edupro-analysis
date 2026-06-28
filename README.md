# EduPro – Learner Demographics & Course Enrollment Behavior Analysis

Streamlit dashboard providing descriptive learner intelligence for the EduPro online platform.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic dataset (skip if you have the real .xlsx)
python data/generate_data.py

# 3. (Optional) Drop your real edupro_data.xlsx into data/

# 4. Launch the dashboard
streamlit run app.py
```

## Using Your Own Dataset

Place your Excel file at `data/edupro_data.xlsx`.  
The file must contain three sheets with these columns:

| Sheet        | Required Columns                                              |
|--------------|---------------------------------------------------------------|
| Users        | UserID, UserName, Age, Gender                                 |
| Courses      | CourseID, CourseName, CourseCategory, CourseType, CourseLevel |
| Transactions | TransactionID, UserID, CourseID, TransactionDate              |

## Dashboard Sections

1. KPI Cards — Total Enrollments, Unique Learners, Avg Courses/Learner, Top Category, Female %
2. Learner Demographics — Age group bar chart, Gender donut chart
3. Enrollment Distribution — Category bar, Course type pie, Level funnel
4. Demographics × Preferences — Age/Category heatmap, Gender/Level grouped bar
5. Behavioral Insights — Stacked bar by age+category, Enrollment distribution histogram
6. Trend Over Time — Monthly enrollment line chart by category
7. Data Explorer — Filterable table with CSV download

## Sidebar Filters

- Age Group (multi-select)
- Gender (multi-select)
- Course Category (multi-select)
- Course Level (multi-select)
