import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- Load Data ---
df = pd.read_csv("District_Data_Modified.csv")

# --- Parameters ---
param_cols = df.columns.tolist()
param_cols.remove('ADM2_EN')

# --- Rank by descending value (high = better) ---
rank_df = df[['ADM2_EN']].copy()
for col in param_cols:
    rank_df[col] = df[col].rank(ascending=False, method='min').astype(int)

# --- Page Config ---
st.set_page_config(page_title="Sri Lanka EnviroRank", layout="wide")

# --- Header ---
st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>🌿 Sri Lanka Environmental Ranking Dashboard</h1>
    <p style='text-align: center; font-size:18px;'>Compare and rank districts based on environmental characteristics</p>
    <hr style='margin-top:10px; margin-bottom:25px;'>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("⚙️ Dashboard Controls")
selected_param = st.sidebar.selectbox("📊 Select Parameter to View Ranking", param_cols)
selected_districts = st.sidebar.multiselect("🏙 Compare Districts (Max 3)", df['ADM2_EN'].unique(), max_selections=3)

# --- Section 1: Parameter Ranking ---
st.subheader(f"📊 District Ranking: {selected_param}")
param_table = df[['ADM2_EN', selected_param]].copy()
param_table['Rank'] = rank_df[selected_param]
param_table = param_table.sort_values(by=selected_param, ascending=False).reset_index(drop=True)

# Styled table
styled_table = param_table.style.background_gradient(cmap='YlGnBu', subset=[selected_param]).format(precision=3)
st.dataframe(styled_table, use_container_width=True)

# Plotly bar chart
fig = px.bar(param_table, x='ADM2_EN', y=selected_param, color=selected_param,
             color_continuous_scale='YlGnBu', title=f"{selected_param} by District")
fig.update_layout(xaxis_title="", yaxis_title=selected_param, title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

# --- Section 2: Comparison ---
st.subheader("🔍 District Comparison Overview")

if selected_districts:
    compare_df = df[df['ADM2_EN'].isin(selected_districts)].set_index('ADM2_EN')
    compare_rank = rank_df[rank_df['ADM2_EN'].isin(selected_districts)].set_index('ADM2_EN')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("📈 **Raw Values**")
        st.dataframe(compare_df[param_cols].T.style.background_gradient(cmap='BuGn').format(precision=2),
                     use_container_width=True)

    with col2:
        st.markdown("🏅 **Rankings**")
        st.dataframe(compare_rank[param_cols].T.style.background_gradient(cmap='PuBu').format(precision=0),
                     use_container_width=True)

    # Radar Chart
    st.subheader("📉 Environmental Profile Radar Chart")
    norm_df = compare_df[param_cols].copy()
    for col in param_cols:
        norm_df[col] = (norm_df[col] - df[col].min()) / (df[col].max() - df[col].min())

    radar_fig = go.Figure()
    for district in norm_df.index:
        radar_fig.add_trace(go.Scatterpolar(
            r=norm_df.loc[district].values,
            theta=param_cols,
            fill='toself',
            name=district
        ))

    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=600,
        title="Normalized Environmental Profile",
        title_x=0.5
    )
    st.plotly_chart(radar_fig, use_container_width=True)
else:
    st.info("ℹ️ Please select 1–3 districts from the sidebar to compare.")
