import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64


# PAGE CONFIGURATION

st.set_page_config(
    page_title="COVID-19 Global Dashboard",
    page_icon="🌍",
    layout="wide"
)


# BACKGROUND IMAGE SETUP

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background("Red-and-Blue-COVID-19-Virus.jpg")


# TITLE AND INTRODUCTION

st.title("🌍 COVID-19 Global Dashboard")
st.markdown("""
This interactive dashboard analyzes **global COVID-19 trends**, highlighting:
- 📈 Global case, death, and recovery trends  
- 🌎 Regional disparities in mortality  
- 🇺🇳 Top 5 most affected countries  

_Data source: Fully Grouped Data From World Health Organization
""")


# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("full_grouped.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

data = load_data()


# SIDEBAR FILTERS

st.sidebar.header("🧭 Dashboard Filters")

# --- Region Filter with "Select All" ---
all_regions = sorted(data['WHO Region'].dropna().unique())

select_all_regions = st.sidebar.checkbox("Select All Regions", value=True)

if select_all_regions:
    selected_region = st.sidebar.multiselect(
        "Select Region(s):",
        options=all_regions,
        default=all_regions
    )
else:
    selected_region = st.sidebar.multiselect(
        "Select Region(s):",
        options=all_regions,
        default=[]
    )

# --- Country Filter ---
all_countries = sorted(data['Country/Region'].dropna().unique())
selected_country = st.sidebar.multiselect(
    "Select Country(s):",
    options=all_countries,
    default=[]
)

# --- Date Filter ---
date_range = st.sidebar.date_input(
    "Select Date Range:",
    [data['Date'].min(), data['Date'].max()]
)


# APPLY FILTERS

# Convert sidebar date objects to pandas timestamps
start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])

filtered_data = data[
    (data['WHO Region'].isin(selected_region)) &
    (data['Date'].between(start_date, end_date))
]

if selected_country:
    filtered_data = filtered_data[filtered_data['Country/Region'].isin(selected_country)]


# GLOBAL TRENDS

st.header("🌐 Global Trends Over Time")

global_data = (
    filtered_data.groupby('Date')[['Confirmed', 'Deaths', 'Recovered']]
    .sum()
    .reset_index()
)

fig_global = px.line(
    global_data,
    x='Date', y=['Confirmed', 'Deaths', 'Recovered'],
    title="Global COVID-19 Progression (Filtered)",
    labels={'value': 'Number of Cases', 'variable': 'Metric'},
)
fig_global.update_layout(
    template="plotly",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_global, use_container_width=True)


# REGIONAL IMPACT

st.header("🗺️ Regional Impact – Deaths per 1M Population")

region_deaths = (
    filtered_data.groupby('WHO Region')
    .agg({'Deaths': 'mean'})
    .reset_index()
    .sort_values('Deaths', ascending=False)
)

fig_region = px.bar(
    region_deaths,
    x='WHO Region', y='Deaths',
    color='WHO Region',
    title='Average Deaths per 1M Population by Region (Filtered)',
)
fig_region.update_layout(
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_region, use_container_width=True)


# TOP 5 AFFECTED COUNTRIES

st.header("🖐️ Top 5 Most Affected Countries")

top5 = (
    filtered_data.groupby('Country/Region')
    .agg({'Confirmed': 'max'})
    .sort_values('Confirmed', ascending=False)
    .head(5)
    .index.tolist()
)

cols = st.columns(5)
for i, country in enumerate(top5):
    subset = filtered_data[filtered_data['Country/Region'] == country]
    if subset.empty:
        continue
    last_row = subset.iloc[-1]

    labels = ['Active', 'Recovered', 'Deaths']
    values = [
        last_row.get('Active', 0),
        last_row.get('Recovered', 0),
        last_row.get('Deaths', 0)
    ]
    color_map = ['#1E90FF', '#2ECC71', '#E74C3C'] 

    fig_pie = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=color_map),
            textinfo='label+percent'
        )]
    )

    fig_pie.update_layout(
        title=f"{country} Case Distribution",
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    cols[i].plotly_chart(fig_pie, use_container_width=True)



# KEY FINDINGS

st.header("🔎 Key Findings")

st.markdown("""
**Top 3 Insights:**
1. Global infection waves peaked around Marsh and April.
2. Europe and the Americas show the highest mortality and Infection Rate per million.
3. Countries with higher population density saw faster spread like USA, India.
4- Countries with Smaller population density saw faster Recovery like Luxembourg, Monaco and UAE.
""")


# CONCLUSION

st.header("🧭 Conclusion")

st.markdown("""
- The pandemic’s impact varied widely by region and density.  
- Mortality correlated strongly with health system readiness.  
- **Lesson:** Global preparedness requires early detection, flexible infrastructure, and equitable access to healthcare.  
""")

st.success("End of Analysis — Thank you!")
