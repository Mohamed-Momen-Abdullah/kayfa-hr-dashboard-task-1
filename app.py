import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- 1. CONFIG & SETUP ---
st.set_page_config(page_title="Week #1 Task: HR Attrition Analytics", layout="wide")


# This natively pins the logo to the top-left of the sidebar, above the navigation
st.logo("kayfa_logo_light.png")

# CSS Injection for the Sky Blue Gradient Header & Transparent Top Bar
st.markdown("""
<style>
    /* 1. Make the default Streamlit top header transparent so the gradient shows through */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* 2. Premium Sky Blue Gradient Banner at the top */
    .stApp {
        background-image: linear-gradient(to bottom, rgba(14, 165, 233, 0.5) 0%, transparent 70%);
        background-attachment: fixed;
    }
    
    /* 3. Insight Callout Boxes */
    .insight-box {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Safe Logo Loader (Prioritizing Light Theme Logo)
def display_logo(width_px=300):
    logo_path = "kayfa_logo_light.png"
    if os.path.exists(logo_path):
        # We use standard width to avoid the deprecation warnings
        st.image(logo_path, width=width_px)
    else:
        st.markdown("**[Kayfa كيف Logo]**")

# --- 2. LOAD & PREP DATA ---
@st.cache_data
def load_data():
    return pd.read_csv('cleaned_hr_data.csv')

df = load_data()

# 1. Clean label column for all charts
df['attrition_label'] = df['attrition'].astype(str).str.strip().map({'0': 'Stayed', '0.0': 'Stayed', '1': 'Left', '1.0': 'Left'})
df['attrition_label'] = df['attrition_label'].fillna(df['attrition'].astype(str))

# 2. Create the strict numeric column (THIS IS THE LINE THAT WAS MISSING)
df['attrition_numeric'] = (df['attrition_label'] == 'Left').astype(int)

# 3. Transform company_tenure from months to years
df['company_tenure_years'] = df['company_tenure'] / 12

# Corporate Muted Palette
color_map = {"Stayed": "#4B7FA1", "Left": "#D56D58"} # Steel Blue and Muted Terracotta

# --- 3. DEFINE MULTIPAGE FUNCTIONS ---

def page_main_dashboard():
    col_text, col_logo = st.columns([5, 1], vertical_alignment="center")
    with col_text:
        st.title("Week #1 Task: Systemic Culture & Employee Attrition")
    with col_logo:
        st.image("kayfa_logo_light.png", width=300) 
    st.markdown("An interactive exploratory analysis identifying the root causes behind our current turnover crisis.")
    st.divider()

    # --- Executive KPIs (Upgraded 2-Row Layout) ---
    st.markdown("### Executive Summary")
    
    # Row 1: The Basics
    c1, c2, c3 = st.columns(3)
    total_employees = len(df)
    attrition_rate = df['attrition_numeric'].mean() * 100
    avg_tenure = df['company_tenure_years'].mean()
    
    c1.metric("Total Workforce Analyzed", f"{total_employees:,}")
    c2.metric("Overall Attrition Rate", f"{attrition_rate:.1f}%")
    c3.metric("Average Tenure", f"{avg_tenure:.1f} Yrs")
    
    st.markdown("<br>", unsafe_allow_html=True) # Adds a little breathing room between rows
    
    # Row 2: The Business Impact
    c4, c5, c6 = st.columns(3)
    
    # Calculate High Performer Attrition
    high_perf_attrition = df[df['performance_rating'] == 'High']['attrition_numeric'].mean() * 100
    
    # Calculate Financial Bleed (Monthly Income * 12 for everyone who left)
    lost_payroll = (df[df['attrition_label'] == 'Left']['monthly_income'] * 12).sum()
    
    # Helper function to format massive numbers beautifully (e.g., $3.20B instead of $3,200,000,000)
    def format_currency(num):
        if num >= 1_000_000_000:
            return f"${num/1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"${num/1_000_000:.2f}M"
        else:
            return f"${num:,.0f}"

    # Calculate Critical Risk Count (From Q9)
    risk_count = len(df[(df['work_life_balance'] == 'Poor') & (df['overtime'] == 'Yes') & (df['job_satisfaction'] == 'Low')])

    c4.metric("High-Performer Flight Rate", f"{high_perf_attrition:.1f}%", "Losing top-tier talent", delta_color="off")
    c5.metric("Annual Payroll Lost", format_currency(lost_payroll), "Capital walking out the door", delta_color="off")
    c6.metric("Critical Risk Employees", f"{risk_count:,}", "Immediate intervention required", delta_color="off")
    
    st.divider()
    # Split related insights into tabs
    tab1, tab2, tab3 = st.tabs(["📊 1. The Crisis Overview", "💸 2. Busting Compensation Myths", "🤝 3. The Cultural Drivers"])

    with tab1:
        st.subheader("The Baseline: How severe is the crisis?")
        pie_counts = df['attrition_label'].value_counts().reset_index()
        pie_counts.columns = ['Status', 'Count']
        
        fig_pie = px.pie(pie_counts, values='Count', names='Status', hole=0.4, color='Status',
                         color_discrete_map=color_map, title="Workforce Retention vs. Attrition Distribution")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, width="stretch")

        st.info("**Insight:** We are facing an unsustainable 47.5% turnover rate. \n\n **Action (CTA):** Leadership must immediately freeze secondary HR initiatives and prioritize a core retention strategy based on the data findings in the next tabs.")

    with tab2:
        st.subheader("Busting Assumptions: Compensation & Demographics")
        col_myth1, col_myth2 = st.columns(2)

        with col_myth1:
            fig_income = px.box(df, x="attrition_label", y="monthly_income", color="attrition_label", 
                                title="Monthly Income Equality Between Cohorts", 
                                labels={"attrition_label": "Employment Status", "monthly_income": "Monthly Income ($)"},
                                color_discrete_map=color_map)
            
            avg_income = df['monthly_income'].mean()
            fig_income.add_hline(y=avg_income, line_dash="dash", line_color="gray", annotation_text="Company Average")
            st.plotly_chart(fig_income, width="stretch")

        with col_myth2:
            fig_age = px.histogram(df, x="age", color="attrition_label", barmode="overlay", opacity=0.75,
                                   title="Generational Stability Across Attrition", 
                                   labels={"attrition_label": "Employment Status", "age": "Employee Age"},
                                   color_discrete_map=color_map)
            st.plotly_chart(fig_age, width="stretch")

        st.success("**Insight:** The median pay and age distribution for departing employees is nearly identical to those who stay. \n\n **Action (CTA):** Halt blanket salary increases and avoid age-targeted retention campaigns; they will burn budget without solving the issue.")

    with tab3:
        st.subheader("The True Drivers: Early Flight & Burnout")
        
        # CHANGED x="years_at_company" to our new x="company_tenure_years"
        fig_tenure = px.histogram(df, x="company_tenure_years", color="attrition_label", barmode="overlay", opacity=0.75,
                                  title="Attrition by Tenure: The 'Early Flight' Crisis", 
                                  labels={"attrition_label": "Employment Status", "company_tenure_years": "Tenure (Years)"},
                                  color_discrete_map=color_map)
        
        # Optional: Force the x-axis to show clean tick marks every 1 year
        fig_tenure.update_xaxes(dtick=1) 
        
        st.plotly_chart(fig_tenure, width="stretch")

        st.markdown("#### The Cultural Tipping Point")
        col_truth1, col_truth2 = st.columns(2)

        with col_truth1:
            order_wlb = ["Poor", "Fair", "Good", "Excellent"]
            fig_wlb = px.histogram(df, x="work_life_balance", color="attrition_label", barmode="group",
                                   title="Impact of Work-Life Balance", 
                                   labels={"attrition_label": "Status", "work_life_balance": "Reported Balance"},
                                   category_orders={"work_life_balance": order_wlb}, text_auto=True,
                                   color_discrete_map=color_map)
            st.plotly_chart(fig_wlb, width="stretch")

        with col_truth2:
            order_rep = ["Poor", "Fair", "Good", "Excellent"]
            fig_rep = px.histogram(df, x="company_reputation", color="attrition_label", barmode="group",
                                   title="Impact of Internal Company Reputation", 
                                   labels={"attrition_label": "Status", "company_reputation": "Perceived Reputation"},
                                   category_orders={"company_reputation": order_rep}, text_auto=True,
                                   color_discrete_map=color_map)
            st.plotly_chart(fig_rep, width="stretch")

        st.warning("**Insight:** Employees in their first 8 years are experiencing severe burnout. When Work-Life balance drops to 'Fair' or 'Poor', attrition radically overtakes retention. \n\n **Action (CTA):** HR must immediately audit the workload expectations of junior staff and implement strict overtime boundaries.")


# --- PLACEHOLDER FUNCTIONS FOR YOUR 10 QUESTIONS ---
def page_q1():
    st.title("1️⃣ Q1: The Headline")
    st.markdown("What share of employees left overall, and which job role is losing the most people?")
    
    # Calculate using the numeric column
    overall_rate = df['attrition_numeric'].mean() * 100
    
    role_group = df.groupby('job_role')['attrition_numeric'].mean().reset_index()
    role_group['Attrition Rate (%)'] = role_group['attrition_numeric'] * 100
    role_group = role_group.sort_values(by='Attrition Rate (%)', ascending=False)
    
    highest_role = role_group.iloc[0]['job_role']
    highest_rate = role_group.iloc[0]['Attrition Rate (%)']
    lowest_rate = role_group.iloc[-1]['Attrition Rate (%)']
    variance = highest_rate - lowest_rate

    st.metric("Overall Company Attrition", f"{overall_rate:.1f}%")

    # Chart
    fig = px.bar(role_group, x='job_role', y='Attrition Rate (%)', 
                 title="Attrition Rate by Job Role: A Systemic Bleed",
                 labels={'job_role': 'Department / Role', 'Attrition Rate (%)': 'Turnover Rate (%)'},
                 color='Attrition Rate (%)', color_continuous_scale="Blues")
    
    # Add a reference line for the company average
    fig.add_hline(y=overall_rate, line_dash="dash", line_color="red", annotation_text="Company Average")
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0, 60]) 
    st.plotly_chart(fig, width="stretch")

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Our overall attrition sits at a critical {overall_rate:.1f}%. However, when breaking this down by job role, the most alarming finding is the <i>lack</i> of variance. The difference between our worst-performing department ({highest_role} at {highest_rate:.1f}%) and our best-performing department is a mere {variance:.1f}%. This proves the exodus is entirely department-agnostic.<br><br>
        <strong>Recommended Action:</strong> Do not waste resources on localized, department-specific management interventions. A perfectly uniform turnover rate across all disciplines indicates a massive, systemic failure at the core organizational level. Leadership must look outward to global company policies rather than investigating individual department heads.
    </div>
    """, unsafe_allow_html=True)

def page_q2():
    st.title("2️⃣ Q2: Overtime vs. Burnout")
    st.markdown("Are employees who work overtime more likely to leave, and by how much?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_vol = px.histogram(df, x="overtime", color="attrition_label", barmode="group",
                               title="Total Employee Volume by Overtime",
                               labels={"overtime": "Works Overtime", "attrition_label": "Status"},
                               color_discrete_map=color_map, text_auto=True)
        st.plotly_chart(fig_vol, width="stretch")
        
    with col2:
        ot_rate = df.groupby('overtime')['attrition_numeric'].mean().reset_index()
        ot_rate['Attrition Rate'] = ot_rate['attrition_numeric'] * 100
        
        fig_rate = px.bar(ot_rate, x='overtime', y='Attrition Rate', color='overtime',
                          title="Attrition Rate: Overtime vs. No Overtime",
                          labels={'overtime': 'Works Overtime', 'Attrition Rate': 'Turnover Rate (%)'},
                          color_discrete_sequence=["#D56D58", "#6B9080"])
        fig_rate.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        st.plotly_chart(fig_rate, width="stretch")

    rate_yes = ot_rate[ot_rate['overtime'] == 'Yes']['Attrition Rate'].values[0]
    rate_no = ot_rate[ot_rate['overtime'] == 'No']['Attrition Rate'].values[0]
    difference = rate_yes - rate_no

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Employees logging overtime are leaving at a rate of {rate_yes:.1f}%, which is {difference:.1f} percentage points higher than those working standard hours ({rate_no:.1f}%). While overtime is contributing to burnout, the fact that nearly half of the non-overtime staff is <i>also</i> quitting proves that simply reducing hours won't solve the core cultural issues.<br><br>
        <strong>Recommended Action:</strong> HR must implement strict overtime caps to stop the immediate bleeding in high-stress roles, but leadership must simultaneously investigate <i>how</i> standard work is being managed, as baseline hours are still resulting in unsustainable turnover.
    </div>
    """, unsafe_allow_html=True)

def page_q3():
    st.title("3️⃣ Q3: The Remote Work Effect")
    st.markdown("Does offering remote work appear to keep people? What are the limitations of this data?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        remote_counts = df['remote_work'].value_counts().reset_index()
        remote_counts.columns = ['Remote Status', 'Total Employees']
        fig_pie = px.pie(remote_counts, values='Total Employees', names='Remote Status', hole=0.5,
                         title="Company Policy: Who actually gets to work remotely?",
                         color_discrete_sequence=["#64748b", "#3b82f6"])
        fig_pie.update_traces(textinfo='percent+value')
        st.plotly_chart(fig_pie, width="stretch")
        
    with col2:
        rw_rate = df.groupby('remote_work')['attrition_numeric'].mean().reset_index()
        rw_rate['Attrition Rate'] = rw_rate['attrition_numeric'] * 100
        
        fig_rw_rate = px.bar(rw_rate, x='remote_work', y='Attrition Rate', color='remote_work',
                             title="Attrition Rate: Remote vs. On-Site",
                             labels={'remote_work': 'Remote Work Allowed', 'Attrition Rate': 'Turnover Rate (%)'},
                             color_discrete_sequence=["#D56D58", "#6B9080"]) 
        fig_rw_rate.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        st.plotly_chart(fig_rw_rate, width="stretch")

    rw_yes_rate = rw_rate[rw_rate['remote_work'] == 'Yes']['Attrition Rate'].values[0]
    rw_no_rate = rw_rate[rw_rate['remote_work'] == 'No']['Attrition Rate'].values[0]
    percent_remote = (df['remote_work'] == 'Yes').mean() * 100

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Remote work acts as a massive retention anchor. On-site employees are fleeing at a rate of {rw_no_rate:.1f}%, while remote workers have a highly stabilized attrition rate of just {rw_yes_rate:.1f}%. However, only {percent_remote:.1f}% of our workforce is currently allowed to work remotely, meaning we cannot conclude if this success would scale company-wide.<br><br>
        <strong>Recommended Action:</strong> Do not mandate a sweeping company-wide remote policy yet. Instead, launch a controlled pilot program expanding remote or hybrid options to a high-flight-risk on-site department to test if the retention benefit scales.
    </div>
    """, unsafe_allow_html=True)

def page_q4():
    st.title("4️⃣ Q4: Pay Fairness & Thresholds")
    st.markdown("Within the same job level, do lower-paid employees leave more often? At what point does pay stop reducing attrition?")
    
    # Create Income Tiers strictly within each Job Level
    df['job_level_str'] = 'Level ' + df['job_level'].astype(str)
    # Use qcut to divide people in the SAME job level into 5 pay brackets
    df['pay_tier'] = df.groupby('job_level')['monthly_income'].transform(
        lambda x: pd.qcut(x, 5, labels=['1. Lowest 20%', '2. Lower-Mid', '3. Middle', '4. Upper-Mid', '5. Highest 20%'], duplicates='drop')
    )
    
    q4_data = df.groupby(['job_level_str', 'pay_tier'])['attrition_numeric'].mean().reset_index()
    q4_data['Attrition Rate (%)'] = q4_data['attrition_numeric'] * 100
    
    fig = px.bar(q4_data, x='pay_tier', y='Attrition Rate (%)', color='job_level_str', barmode='group',
                 title="Attrition by Relative Pay Tier (Within Same Job Level)",
                 labels={'pay_tier': 'Pay Tier (Compared to Peers)', 'job_level_str': 'Job Level'},
                 color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(yaxis_range=[0, max(q4_data['Attrition Rate (%)']) + 10])
    st.plotly_chart(fig, width="stretch")

    # Dynamic calculation for insight
    lowest_tier_rate = q4_data[q4_data['pay_tier'] == '1. Lowest 20%']['Attrition Rate (%)'].mean()
    highest_tier_rate = q4_data[q4_data['pay_tier'] == '5. Highest 20%']['Attrition Rate (%)'].mean()
    variance = abs(lowest_tier_rate - highest_tier_rate)

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> When comparing employees working at the exact same job level, the attrition rate for those in the lowest 20% pay bracket averages {lowest_tier_rate:.1f}%, while those in the highest 20% bracket average {highest_tier_rate:.1f}%. A variance of {variance:.1f}% indicates whether relative pay fairness within a title is a true flight risk or a non-factor.<br><br>
        <strong>Recommended Action:</strong> If the variance is flat, HR should immediately halt attempts to solve attrition through minor salary bumps—the data proves it does not buy loyalty. If lower-tier attrition spikes, HR must audit their pay bands to ensure internal equity, focusing raises solely on those in the bottom 20% of their level rather than broad, company-wide increases.
    </div>
    """, unsafe_allow_html=True)

def page_q5():
    st.title("5️⃣ Q5: The Retention Timeline")
    st.markdown("At what stage of an employee's time at the company is attrition highest?")
    
    # Round down to the nearest year for clean grouping
    df['tenure_year'] = df['company_tenure_years'].apply(np.floor).astype(int)
    q5_data = df.groupby('tenure_year')['attrition_numeric'].agg(['mean', 'count']).reset_index()
    q5_data['Attrition Rate (%)'] = q5_data['mean'] * 100
    
    # Filter out years with less than 50 people to avoid noisy data spikes at the tail end
    q5_data = q5_data[q5_data['count'] > 50]
    
    fig = px.line(q5_data, x='tenure_year', y='Attrition Rate (%)', markers=True,
                  title="The Flight Risk Timeline: Attrition Rate by Year",
                  labels={'tenure_year': 'Years at Company'})
    fig.update_traces(line_color="#ef4444", line_width=4, marker=dict(size=10))
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, width="stretch")

    # Dynamic calculation
    peak_year = q5_data.loc[q5_data['Attrition Rate (%)'].idxmax()]['tenure_year']
    peak_rate = q5_data['Attrition Rate (%)'].max()

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Attrition does not happen randomly; it is highly concentrated. The data shows a distinct peak flight risk at Year {int(peak_year)}, where turnover hits an extreme {peak_rate:.1f}%. This proves our core retention failure is not occurring during initial onboarding, nor is it related to long-term retirement.<br><br>
        <strong>Recommended Action:</strong> HR must entirely redesign the "mid-career" experience. Retention efforts—such as targeted promotions, workload audits, and sabbatical offerings—must be proactively deployed to employees approaching the Year {int(peak_year)} mark to intercept them before they hit the historical breaking point.
    </div>
    """, unsafe_allow_html=True)

def page_q6():
    st.title("6️⃣ Q6: Engagement Warning Signs")
    st.markdown("Combine Job Satisfaction and Work-Life Balance. Which combination is the strongest early-warning sign?")
    
    # Calculate cross-tabulated attrition rates
    q6_data = df.groupby(['job_satisfaction', 'work_life_balance'])['attrition_numeric'].mean().reset_index()
    q6_data['Attrition Rate (%)'] = q6_data['attrition_numeric'] * 100
    
    # Order the categories logically for the heatmap
    sat_order = ['Low', 'Medium', 'High', 'Very High']
    wlb_order = ['Poor', 'Fair', 'Good', 'Excellent']
    
    pivot = q6_data.pivot(index='job_satisfaction', columns='work_life_balance', values='Attrition Rate (%)')
    pivot = pivot.reindex(index=sat_order, columns=wlb_order)
    
    fig = px.imshow(pivot, text_auto=".1f", color_continuous_scale="Reds",
                    title="Heatmap: Attrition Risk by Engagement Combination",
                    labels={'x': 'Work-Life Balance', 'y': 'Job Satisfaction', 'color': 'Attrition %'})
    st.plotly_chart(fig, width="stretch")

    # Dynamic calculation
    highest_risk = q6_data.loc[q6_data['Attrition Rate (%)'].idxmax()]
    combo_sat = highest_risk['job_satisfaction']
    combo_wlb = highest_risk['work_life_balance']
    combo_rate = highest_risk['Attrition Rate (%)']

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Analyzing these metrics in isolation masks the true danger zone. The matrix reveals that the lethal combination driving turnover is a <b>'{combo_sat}' Job Satisfaction</b> paired with a <b>'{combo_wlb}' Work-Life Balance</b>, resulting in a staggering {combo_rate:.1f}% attrition rate.<br><br>
        <strong>Recommended Action:</strong> Managers must be trained to recognize this specific intersection as an immediate "Code Red." Performance check-ins should stop treating satisfaction and workload as separate scores; if an employee flags this specific combination during a 1-on-1, managers must be empowered to unilaterally intervene with workload reductions before the employee quits.
    </div>
    """, unsafe_allow_html=True)

def page_q7():
    st.title("7️⃣ Q7: Life Stage Risk")
    st.markdown("Do age, marital status, and number of dependents change who leaves?")
    
    # Create Life Stage proxy
    df['Dependents Status'] = df['number_of_dependents'].apply(lambda x: 'With Dependents' if x > 0 else 'No Dependents')
    
    q7_data = df.groupby(['marital_status', 'Dependents Status'])['attrition_numeric'].mean().reset_index()
    q7_data['Attrition Rate (%)'] = q7_data['attrition_numeric'] * 100
    
    fig = px.bar(q7_data, x='marital_status', y='Attrition Rate (%)', color='Dependents Status', barmode='group',
                 title="Attrition by Marital Status & Dependents",
                 labels={'marital_status': 'Marital Status'},
                 color_discrete_sequence=["#3b82f6", "#ef4444"])
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(yaxis_range=[0, max(q7_data['Attrition Rate (%)']) + 15])
    st.plotly_chart(fig, width="stretch")

    # Dynamic calculation
    highest_risk = q7_data.loc[q7_data['Attrition Rate (%)'].idxmax()]
    risk_marital = highest_risk['marital_status']
    risk_deps = highest_risk['Dependents Status']
    risk_rate = highest_risk['Attrition Rate (%)']

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Life stage dramatically alters flight risk. Our data proves that the <b>{risk_marital} / {risk_deps}</b> demographic is our most vulnerable cohort, churning at {risk_rate:.1f}%. While overall age doesn't strictly dictate attrition, the responsibilities anchoring an employee (or lack thereof) heavily influence their willingness to tolerate a poor work culture.<br><br>
        <strong>Recommended Action:</strong> A one-size-fits-all benefits package is failing us. To retain this specific high-risk demographic, HR must introduce flexible, life-stage specific benefits (e.g., expanded childcare stipends, flexible hours, or commuter benefits) that directly alleviate the friction points unique to their personal situations.
    </div>
    """, unsafe_allow_html=True)
def page_q8():
    st.title("8️⃣ Q8: Career Stagnation")
    st.markdown("Build the case that lack of growth drives attrition. Does feeling 'stuck' line up with leaving?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Promotions
        q8_prom = df.groupby('number_of_promotions')['attrition_numeric'].mean().reset_index()
        q8_prom['Attrition Rate (%)'] = q8_prom['attrition_numeric'] * 100
        fig_prom = px.bar(q8_prom, x='number_of_promotions', y='Attrition Rate (%)',
                          title="Attrition by Number of Promotions",
                          labels={'number_of_promotions': 'Total Promotions', 'Attrition Rate (%)': 'Turnover Rate (%)'},
                          color='Attrition Rate (%)', color_continuous_scale="OrRd")
        fig_prom.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_prom, width="stretch")
        
    with col2:
        # Leadership Opportunities (Assuming categorical/ordinal)
        q8_lead = df.groupby('leadership_opportunities')['attrition_numeric'].mean().reset_index()
        q8_lead['Attrition Rate (%)'] = q8_lead['attrition_numeric'] * 100
        q8_lead = q8_lead.sort_values(by='Attrition Rate (%)', ascending=False)
        fig_lead = px.bar(q8_lead, x='leadership_opportunities', y='Attrition Rate (%)',
                          title="Attrition by Leadership Opportunities",
                          labels={'leadership_opportunities': 'Access to Leadership Opps', 'Attrition Rate (%)': 'Turnover Rate (%)'},
                          color_discrete_sequence=["#ef4444"])
        st.plotly_chart(fig_lead, width="stretch")

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> Career stagnation is a massive accelerant for turnover. Employees who have received zero promotions or report a lack of leadership and innovation opportunities leave at significantly higher rates than those experiencing internal mobility. When an employee feels their career has "plateaued" within their current job level, they don't wait for a fix—they seek upward mobility at a competitor.<br><br>
        <strong>Recommended Action:</strong> HR must implement a "Lateral Mobility & Micro-Promotion" framework. For employees stuck in job levels where upward promotions are currently unavailable, we must provide formalized leadership shadowing, innovation task forces, or lateral department moves to ensure they continue building their resumes internally rather than externally.
    </div>
    """, unsafe_allow_html=True)

def page_q9():
    st.title("9️⃣ Q9: The Highest-Risk Profile")
    st.markdown("Combine 3-4 factors to construct the single highest-risk employee profile. Report how much higher their attrition is than the baseline, and how many people match it.")
    
    baseline_rate = df['attrition_numeric'].mean() * 100
    
    # Constructing the "Perfect Storm" Profile based on previous findings
    # 1. Poor Work Life Balance, 2. Overtime = Yes, 3. Low Job Satisfaction
    high_risk_df = df[(df['work_life_balance'] == 'Poor') & 
                      (df['overtime'] == 'Yes') & 
                      (df['job_satisfaction'] == 'Low')]
    
    hr_count = len(high_risk_df)
    
    if hr_count > 0:
        hr_rate = high_risk_df['attrition_numeric'].mean() * 100
        multiplier = hr_rate / baseline_rate
    else:
        hr_rate = 0
        multiplier = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Company Baseline Attrition", f"{baseline_rate:.1f}%")
    col2.metric("Profile Attrition Rate", f"{hr_rate:.1f}%", f"+{(hr_rate - baseline_rate):.1f}% vs Avg", delta_color="inverse")
    col3.metric("Employees in this Profile", f"{hr_count:,}", "Immediate Flight Risks", delta_color="off")

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> By synthesizing the data, we have identified the "Perfect Storm" flight-risk profile: An employee who works <b>Overtime</b>, reports a <b>Poor Work-Life Balance</b>, and has <b>Low Job Satisfaction</b>. This specific cohort quits at a staggering rate of {hr_rate:.1f}%, which is {multiplier:.1f}x higher than the company baseline.<br><br>
        <strong>Recommended Action:</strong> We have exactly {hr_count:,} employees currently matching this terminal profile. Leadership must stop viewing retention as a broad, company-wide initiative. HR must pull the roster of these {hr_count:,} specific individuals tomorrow morning and execute immediate emergency interventions (workload reduction, mandatory PTO) before we lose them.
    </div>
    """, unsafe_allow_html=True)

def page_q10():
    st.title("🔟 Q10: What Moves the Needle")
    st.markdown("If HR could fix only one thing next quarter to reduce attrition, what does the data say it should be? Rank the top 3 drivers.")
    
    baseline_rate = df['attrition_numeric'].mean()
    
    # Dynamically calculate the "Delta" (How much the worst category of a metric drives up attrition)
    drivers = ['work_life_balance', 'overtime', 'company_reputation', 'job_satisfaction', 'remote_work']
    impacts = []
    
    for col in drivers:
        # Find the category with the highest attrition in this column
        worst_cat = df.groupby(col)['attrition_numeric'].mean().idxmax()
        worst_rate = df.groupby(col)['attrition_numeric'].mean().max()
        delta = (worst_rate - baseline_rate) * 100 # Percentage points above baseline
        
        # Format a clean name for the chart
        clean_name = col.replace('_', ' ').title()
        impacts.append({'Driver': f"{clean_name} ('{worst_cat}')", 'Points Above Baseline': delta})
        
    impact_df = pd.DataFrame(impacts).sort_values(by='Points Above Baseline', ascending=False).head(3)
    
    fig = px.bar(impact_df, x='Points Above Baseline', y='Driver', orientation='h',
                 title="Top 3 Attrition Accelerants (Impact vs Company Baseline)",
                 labels={'Points Above Baseline': 'Percentage Points Added to Attrition'},
                 color='Points Above Baseline', color_continuous_scale="Reds")
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")

    top_driver = impact_df.iloc[0]['Driver']
    top_impact = impact_df.iloc[0]['Points Above Baseline']

    st.markdown(f"""
    <div class='insight-box'>
        <strong>Strategic Insight:</strong> The data unequivocally identifies <b>{top_driver}</b> as our #1 organizational threat. Falling into this specific category shifts an employee's flight risk by an astronomical +{top_impact:.1f} percentage points above our already critical baseline. Tackling drivers #2 and #3 will yield marginal returns as long as the primary driver remains broken.<br><br>
        <strong>Recommended Action:</strong> If leadership can only fund one initiative next quarter, 100% of the budget must go toward resolving the {top_driver} crisis. By neutralizing this single massive delta and bringing those employees just back to the company average, we could salvage hundreds of headcount globally. No other initiative offers this level of mathematical ROI.
    </div>
    """, unsafe_allow_html=True)

def page_summary():
    st.title("📝 Executive Summary & Action Plan")
    st.markdown("A high-level synthesis of the attrition crisis, the core drivers, and strategic next steps.")
    
    st.divider()

    # --- Section 1: The Core Problem ---
    st.header("1. The State of the Workforce")
    c1, c2, c3 = st.columns(3)
    c1.metric("Overall Attrition", f"{df['attrition_numeric'].mean() * 100:.1f}%", "Critical Level", delta_color="inverse")
    c2.metric("Peak Flight Risk", "Years 1 - 4", "Mid-career exodus")
    c3.metric("Annual Payroll Lost", f"${(df[df['attrition_label'] == 'Left']['monthly_income'] * 12).sum() / 1_000_000:.1f}M", "Capital Drain", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 2: Key Drivers ---
    st.header("2. The Primary Drivers of Turnover")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("**⏳ The Overtime Crisis**\n\nEmployees working overtime are abandoning the company at significantly higher rates. However, baseline hours also yield high turnover, indicating standard workloads are unmanageable.")
        st.warning("**🚧 Career Stagnation**\n\nLack of upward mobility is a massive accelerant. Employees with zero promotions or lacking leadership opportunities are seeking growth externally.")
        
    with col_b:
        st.success("**🏠 The Remote Anchor**\n\nRemote work acts as our strongest retention tool. Remote employees have less than half the turnover rate of their on-site counterparts.")
        st.error("**⚠️ The 'Perfect Storm'**\n\nThe most lethal combination for retention is an employee experiencing **Low Job Satisfaction**, **Poor Work-Life Balance**, and working **Overtime**. This profile quits at astronomical rates.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Section 3: Strategic Action Plan ---
    st.header("3. Recommended Action Plan")
    
    st.markdown("""
    Based on the mathematical realities of the dataset, HR and Leadership must prioritize the following initiatives next quarter:
    
    *   **Phase 1 (Immediate): Halt the 'Perfect Storm' Bleed.** HR must immediately pull the roster of employees currently matching the high-risk profile (Overtime + Poor WLB + Low Satisfaction) and mandate workload reductions or PTO.
    *   **Phase 2 (Short-Term): Mid-Career Interventions.** Shift retention resources away from initial onboarding and target employees approaching the 1-to-4 year tenure mark with proactive check-ins and lateral mobility opportunities.
    *   **Phase 3 (Long-Term): Remote Pilot Expansion.** Launch a controlled pilot program expanding remote or hybrid options to high-flight-risk on-site departments to test if the retention benefit scales company-wide.
    """)

# --- 4. RENDER NATIVE MULTIPAGE NAVIGATION ---

pg = st.navigation(
    {
        "Executive Overview": [
            st.Page(page_main_dashboard, title="Main Dashboard", icon="📊"),
            st.Page(page_summary, title="Executive Summary", icon="📝") # Added right here!
        ],
        "10 Business Questions": [
            st.Page(page_q1, title="Question 1", icon="1️⃣"),
            st.Page(page_q2, title="Question 2", icon="2️⃣"),
            st.Page(page_q3, title="Question 3", icon="3️⃣"),
            st.Page(page_q4, title="Question 4", icon="4️⃣"),
            st.Page(page_q5, title="Question 5", icon="5️⃣"),
            st.Page(page_q6, title="Question 6", icon="6️⃣"),
            st.Page(page_q7, title="Question 7", icon="7️⃣"),
            st.Page(page_q8, title="Question 8", icon="8️⃣"),
            st.Page(page_q9, title="Question 9", icon="9️⃣"),
            st.Page(page_q10, title="Question 10", icon="🔟")
        ]
    }
)
pg.run()
