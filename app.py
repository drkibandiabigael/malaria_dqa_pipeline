import streamlit as st
import pandas as pd
import plotly.express as px

# Configure the web page layout and title
st.set_page_config(page_title="MEL DQA Dashboard", page_icon="📊", layout="wide")

st.title("🌍 East Africa Regional Malaria Control: MEL & DQA Dashboard")
st.markdown("""
This executive dashboard tracks routine health facility reporting across Kenya, Uganda, and Tanzania. 
It highlights programmatic coverage and tracks **Data Quality Assurance (DQA)** anomalies flagged by the automated validation pipeline.
""")

# Load the datasets generated from Project 1
@st.cache_data
def load_data():
    health_data = pd.read_csv("regional_malaria_data.csv")
    dqa_log = pd.read_excel("Biweekly_DQA_Issue_Log.xlsx")
    return health_data, dqa_log

health_data, dqa_log = load_data()

# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.header("Program Filters")
selected_country = st.sidebar.multiselect(
    "Select Country Office:",
    options=health_data['country'].unique(),
    default=health_data['country'].unique()
)

# Apply filters to dataframes
filtered_health = health_data[health_data['country'].isin(selected_country)]
filtered_dqa = dqa_log[dqa_log['Country'].isin(selected_country)]

# ==========================================
# TOP ROW: EXECUTIVE KPI METRICS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

total_facilities = len(filtered_health)
reporting_rate = (filtered_health['tests_conducted'].count() / total_facilities) * 100
total_dqa_issues = len(filtered_dqa)
unresolved_issues = len(filtered_dqa[filtered_dqa['Status'] != 'Resolved'])

col1.metric("Active Facilities", f"{total_facilities}")
col2.metric("HMIS Reporting Completeness", f"{reporting_rate:.1f}%")
col3.metric("DQA Anomalies Flagged", f"{total_dqa_issues}")
col4.metric("Unresolved DQA Tickets", f"{unresolved_issues}", delta_color="inverse")

st.markdown("---")

# ==========================================
# MIDDLE ROW: VISUALIZATIONS
# ==========================================
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader("DQA Anomaly Severity by Country")
    # Grouping data for the stacked bar
    error_counts = filtered_dqa.groupby(['Country', 'Issue_Type']).size().reset_index(name='Count')
    fig_bar = px.bar(
        error_counts, x='Country', y='Count', color='Issue_Type',
        barmode='stack', text='Count',
        color_discrete_map={
            'Protocol Variance': '#d9534f',
            'Logic Contradiction': '#f0ad4e',
            'Completeness': '#5bc0de',
            'Epi Outlier': '#292b2c'
        }
    )
    fig_bar.update_layout(xaxis_title="", yaxis_title="Total Issues")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_viz2:
    st.subheader("Bi-Weekly Remediation Workflow")
    status_counts = filtered_dqa['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_pie = px.pie(
        status_counts, values='Count', names='Status', hole=0.4,
        color='Status',
        color_discrete_map={
            'Resolved': '#5cb85c', 
            'Escalated to Facility': '#f0ad4e',
            'Logged - Pending': '#d9534f'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==========================================
# BOTTOM ROW: AUDITABLE ISSUE LOG DATAFRAME
# ==========================================
st.subheader("📋 Actionable DQA Focal Point Log")
st.markdown("Dynamic log for country MEL focal persons to track and resolve data discrepancies prior to donor reporting.")

# Interactive dataframe toggle
st.dataframe(
    filtered_dqa[['Country', 'Issue_Type', 'Status']], 
    use_container_width=True,
    height=200
)