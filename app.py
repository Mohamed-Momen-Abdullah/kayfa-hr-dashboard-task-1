import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Config & Minimalist Theme ---
st.set_page_config(page_title="Kayfa كيف | HR Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Deep dark minimalist background */
    .stApp { background-color: #0a0a0f; }
    
    /* Sleek metric cards */
    div[data-testid="metric-container"] {
        background-color: #16161f;
        border: 1px solid #232333;
        padding: 5% 5% 5% 10%;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    }
    
    /* Typography cleanup */
    h1, h2, h3, h4, p, li, span { color: #e2e2e2 !important; }
    
    /* Insight Callout Boxes */
    .insight-box {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    
    /* Minimal sidebar */
    [data-testid="stSidebar"] {
        background-color: #050508;
        border-right: 1px solid #1a1a24;
    }
    
    /* Center align footer */
    .footer {
        text-align: center;
        padding-top: 50px;
        padding-bottom: 20px;
        color: #6b7280 !important;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper: Safe Logo Loader ---
def display_logo(width_val=200):
    logo_path = "kayfa_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=width_val)
    else:
        st.markdown("**[Kayfa كيف Logo]**")

# --- 2. Top Branding & Header ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    display_logo(width_val=150)
with col_title:
    st.title("Employee Attrition Analytics")
    st.markdown("Presented by **Mohamed Mo'men** | Identifying the root causes of our 47.5% turnover rate.")

st.divider()

# --- 3. Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv('cleaned_hr_data.csv')

df = load_data()

# Clean label column for all charts
df['attrition_label'] = df['attrition'].astype(str).str.strip().map({'0': 'Stayed', '0.0': 'Stayed', '1': 'Left', '1.0': 'Left'})
df['attrition_label'] = df['attrition_label'].fillna(df['attrition'].astype(str))

# --- 4. Sidebar Filters ---
st.sidebar.markdown("### Control Panel")
selected_dept = st.sidebar.multiselect("Select Job Role(s)", options=df['job_role'].unique(), default=df['job_role'].unique())

gender_col = 'gender' if 'gender' in df.columns else 'Gender'
if gender_col in df.columns:
    selected_gender = st.sidebar.multiselect("Select Gender", options=df[gender_col].unique(), default=df[gender_col].unique())
    filtered_df = df[(df['job_role'].isin(selected_dept)) & (df[gender_col].isin(selected_gender))]
else:
    filtered_df = df[df['job_role'].isin(selected_dept)]

# --- Global Chart Settings ---
color_map = {"Stayed": "#3b82f6", "Left": "#ef4444"} # Blue and Red
bg_transparent = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=0))

# --- 5. Executive Dashboard ---
# Executive Summary
st.markdown("""
<div class='insight-box'>
    <strong>Executive Summary:</strong> The organization is currently facing an unsustainable attrition rate. Visual data analysis proves the root cause is not related to compensation or demographics, but rather systemic cultural burnout impacting newer employees.
</div>
""", unsafe_allow_html=True)

# KPIs
c1, c2, c3 = st.columns(3)
total_employees = len(filtered_df)
attrition_count = len(filtered_df[filtered_df['attrition_label'] == 'Left'])
attrition_rate = (attrition_count / total_employees) * 100 if total_employees > 0 else 0
avg_tenure = filtered_df['company_tenure'].mean()

c1.metric("Total Workforce Analyzed", f"{total_employees:,}")
c2.metric("Overall Attrition Rate", f"{attrition_rate:.1f}%")
c3.metric("Average Tenure", f"{avg_tenure:.1f} Yrs")

st.divider()

# --- SECTION 1: The Crisis ---
st.header("1. The Current Crisis")
pie_counts = filtered_df['attrition_label'].value_counts().reset_index()
pie_counts.columns = ['Status', 'Count']
fig_pie = px.pie(pie_counts, values='Count', names='Status', hole=0.4, color='Status',
                 color_discrete_map=color_map, template='plotly_dark')
fig_pie.update_layout(**bg_transparent)

pie_col1, pie_col2, pie_col3 = st.columns([1, 2, 1])
with pie_col2:
    st.plotly_chart(fig_pie, width="stretch")

st.divider()

# --- SECTION 2: Busting the Myths ---
st.header("2. Busting the Myths: Compensation & Demographics")
st.markdown("Initial assumptions pointed to salary, lack of promotion, or older employees retiring. However, the data reveals a completely uniform distribution of attrition across income brackets and age groups.")

col_myth1, col_myth2 = st.columns(2)

with col_myth1:
    fig_income = px.box(filtered_df, x="attrition_label", y="monthly_income", color="attrition_label", 
                        title="Income Equality (Median Pay is Identical)", color_discrete_map=color_map, template="plotly_dark")
    fig_income.update_layout(**bg_transparent, showlegend=False)
    st.plotly_chart(fig_income, width="stretch")

with col_myth2:
    fig_age = px.histogram(filtered_df, x="age", color="attrition_label", barmode="overlay", opacity=0.75,
                             title="Generational Stability (All Ages Quitting Equally)", color_discrete_map=color_map, template="plotly_dark")
    fig_age.update_layout(**bg_transparent, showlegend=False)
    st.plotly_chart(fig_age, width="stretch")

st.markdown("""
<div class='insight-box'>
    <strong>Strategic Insight:</strong> Implementing blanket salary increases or aggressive promotion tracks will burn company capital without effectively reducing the turnover rate. We are losing 25-year-olds at the exact same rate as 55-year-olds, across all pay brackets.
</div>
""", unsafe_allow_html=True)

st.divider()

# --- SECTION 3: The Early Flight Crisis ---
st.header("3. Identifying the 'Early Flight' Crisis")
st.markdown("While age is not a factor, organizational tenure is. By analyzing the years spent at the company, it becomes clear this is not a retirement issue.")

fig_tenure = px.histogram(filtered_df, x="years_at_company", color="attrition_label", barmode="overlay", opacity=0.75,
                          title="Attrition by Tenure: The First 10 Years", color_discrete_map=color_map, template="plotly_dark")
fig_tenure.update_layout(**bg_transparent)
st.plotly_chart(fig_tenure, width="stretch")

st.markdown("""
<div class='insight-box'>
    <strong>Strategic Insight:</strong> The highest volume of departures occurs within the first 1 to 8 years of employment. We are successfully hiring, but failing to retain talent past the mid-level threshold.
</div>
""", unsafe_allow_html=True)

st.divider()

# --- SECTION 4: The True Culprits ---
st.header("4. The True Culprits: Culture and Burnout")
st.markdown("Because financial and demographic metrics showed uniform attrition, the analysis pivoted to cultural indicators. This is where a distinct polarity shift occurs.")

col_truth1, col_truth2 = st.columns(2)

with col_truth1:
    order_wlb = ["Poor", "Fair", "Good", "Excellent"]
    fig_wlb = px.histogram(filtered_df, x="work_life_balance", color="attrition_label", barmode="group",
                           title="The Tipping Point: Work-Life Balance", category_orders={"work_life_balance": order_wlb},
                           color_discrete_map=color_map, template="plotly_dark")
    fig_wlb.update_layout(**bg_transparent)
    st.plotly_chart(fig_wlb, width="stretch")

with col_truth2:
    order_rep = ["Poor", "Fair", "Good", "Excellent"]
    fig_rep = px.histogram(filtered_df, x="company_reputation", color="attrition_label", barmode="group",
                           title="The Tipping Point: Company Reputation", category_orders={"company_reputation": order_rep},
                           color_discrete_map=color_map, template="plotly_dark")
    fig_rep.update_layout(**bg_transparent)
    st.plotly_chart(fig_rep, width="stretch")

st.markdown("""
<div class='insight-box'>
    <strong>Strategic Insight:</strong> When employees rate these categories as 'Excellent' or 'Good', retention outpaces attrition. The moment the experience drops to 'Fair' or 'Poor', attrition radically spikes and becomes the majority outcome.
</div>
""", unsafe_allow_html=True)

st.divider()

# --- SECTION 5: Conclusion ---
st.header("Conclusion & Next Steps")
st.markdown("""
The data dictates that HR should pivot their retention strategy away from strictly financial incentives. Immediate action should include:
* **Auditing the workload and expectations** of employees in their first 5 years to combat early burnout.
* **Implementing targeted interventions** for departments reporting poor work-life balance.

**Culture, not compensation, is the key to stabilizing the workforce.**
""")

# --- 6. Footer & Bottom Branding ---
st.markdown("<div class='footer'>", unsafe_allow_html=True)
bottom_col1, bottom_col2, bottom_col3 = st.columns([2, 1, 2])
with bottom_col2:
    display_logo(width_val=100)

st.markdown("### **Kayfa كيف** Data Analytics Internship | Week 1 Task")
st.markdown("</div>", unsafe_allow_html=True)