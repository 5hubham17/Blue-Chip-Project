import streamlit as st
import pandas as pd
from openai import OpenAI
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="IPL Blue Chip Intelligence", layout="wide")



#-- theme ---
st.markdown("""
    <style>
    /* 1. Global Metallic Background */
    .stApp {
        background: linear-gradient(145deg, #2c3e50 0%, #000000 100%) !important;
        background-attachment: fixed !important;
    }

    /* 2. CRITICAL: Remove the white/gray inner container */
    [data-testid="stAppViewBlockContainer"] {
        background-color: transparent !important;
        background-image: none !important;
    }
    
    /* Remove any header-related backgrounds */
    header, [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 3. Text Colors: White for general UI, Black for Search Box */
    html, body, [class*="st-"], div, p, h1, h2, h3, h4, label, span, li {
        color: #ffffff !important;
    }

    /* 4. Search Box */
    div[data-testid="stTextInput"] > div > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 10px !important;
    }
    
    input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    ::placeholder {
        color: #000000 !important;
        opacity: 0.6 !important; 
    }

    /* 5. Dropdown/Sidebar Logic */
    .stSelectbox div {
        background-color: transparent !important;
        border: none !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1e272e, #000000) !important;
        border-right: none !important;
    }

    /* 6. AI Result Area (Transparent Highlight) */
    [data-testid="stNotification"], .stAlert {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df_val = pd.read_csv('IPL_Franchise_Valuations_2025.csv')
    return df_val

df_val = load_data()

# --- LOGO MAPPING ---
LOGO_URLS = {
    "Royal Challengers Bengaluru": "https://1000logos.net/wp-content/uploads/2024/03/Royal-Challengers-Bengaluru-Logo.png",
    "Mumbai Indians": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cd/Mumbai_Indians_Logo.svg/512px-Mumbai_Indians_Logo.svg.png",
    "Chennai Super Kings": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2b/Chennai_Super_Kings_Logo.svg/512px-Chennai_Super_Kings_Logo.svg.png",
    "Kolkata Knight Riders": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Kolkata_Knight_Riders_Logo.svg/512px-Kolkata_Knight_Riders_Logo.svg.png",
    "Sunrisers Hyderabad": "https://1000logos.net/wp-content/uploads/2024/03/Sunrisers-Hyderabad-Logo.png",
    "Delhi Capitals": "https://1000logos.net/wp-content/uploads/2024/03/Delhi-Capitals-Logo.png",
    "Rajasthan Royals": "https://1000logos.net/wp-content/uploads/2024/03/Rajasthan-Royals-Logo.png",
    "Gujarat Titans": "https://upload.wikimedia.org/wikipedia/en/thumb/0/09/Gujarat_Titans_Logo.svg/512px-Gujarat_Titans_Logo.svg.png",
    "Punjab Kings": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Punjab_Kings_Logo.svg/512px-Punjab_Kings_Logo.svg.png",
    "Lucknow Super Giants": "https://1000logos.net/wp-content/uploads/2024/03/Lucknow-Super-Giants-Logo.png"
}

# --- HEADER & SIDEBAR ---
st.title("🛡️ IPL SPONSORSHIP INTELLIGENCE")

with st.sidebar:
    st.header("Financial Metrics")
    selected_team = st.selectbox("Select Team", df_val['IPL Team'].unique())
    team_stats = df_val[df_val['IPL Team'] == selected_team].iloc[0]
    st.metric("Brand Value", f"${team_stats['Brand Value (USD)']/1e6:.1f}M")
    st.metric("Net Worth", f"₹{team_stats['Net Worth (INR Crore)']} Cr")

# --- AI STRATEGIST PROMPT ---

user_query = st.text_input(
    label="Ask the Strategist", 
    placeholder="Type your strategic query (e.g., 'Analyze MI's market dominance')...",
    key="search_box"
)

if user_query:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="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")
    
    with st.spinner("Analyzing Market Synergy..."):
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": "You are a sharp IPL sponsorship analyst. Use metrics and Synergy Scores (0-100)."},
                {"role": "user", "content": f"Context: {df_val.to_string()}\n\nQuestion: {user_query}"}
            ]
        )
        st.info(response.choices[0].message.content)

# --- CHART SECTION ---
st.divider()
st.subheader("📊 Franchise Valuation Matrix")

fig = go.Figure()
x_range = df_val['Brand Value (USD)'].max() - df_val['Brand Value (USD)'].min()
y_range = df_val['Net Worth (INR Crore)'].max() - df_val['Net Worth (INR Crore)'].min()

fig.add_trace(go.Scatter(
    x=df_val['Brand Value (USD)'], y=df_val['Net Worth (INR Crore)'],
    mode='markers', marker=dict(opacity=0),
    text=df_val['IPL Team'],
    hovertemplate="<b>%{text}</b><br>Value: $%{x}<br>Net Worth: ₹%{y} Cr<extra></extra>"
))

for i, row in df_val.iterrows():
    url = LOGO_URLS.get(row['IPL Team'])
    if url:
        fig.add_layout_image(dict(
            source=url, xref="x", yref="y",
            x=row['Brand Value (USD)'], y=row['Net Worth (INR Crore)'],
            sizex=x_range * 0.12, sizey=y_range * 0.12,
            xanchor="center", yanchor="middle", layer="above"
        ))

fig.update_layout(
    font=dict(color="#ffffff"),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(gridcolor='#333', title="Brand Value (USD)"),
    yaxis=dict(gridcolor='#333', title="Net Worth (INR Crore)")
)

st.plotly_chart(fig, use_container_width=True)