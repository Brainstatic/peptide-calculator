
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# Constants
LN2 = np.log(2)

# Predefined peptide half-lives
predefined_half_lives = {
    "GLP-3": 6,
    "BPC-157": 0.5,
    "CJC-1295 (w/o DAC)": 0.5,
    "CJC-1295 (with DAC)": 6,
    "Thymosin Beta-4": 2,
    "Semaglutide": 7,
    "Tirzepatide": 5,
    "Retatrutide": 6,
    "Custom": None
}

st.title("🧪 Peptide Concentration Planner & Plotter")

# Sidebar - Simulation parameters
mode = st.sidebar.radio("Mode", ["Visualize dosing schedule", "Plan for target concentration"])

duration_weeks = st.sidebar.number_input("Simulation duration (weeks)", min_value=1, value=8)
total_days = duration_weeks * 7
days = np.arange(0, total_days + 1)

# Reverse planning mode
if mode == "Plan for target concentration":
    st.sidebar.markdown("## Target Planning Inputs")
    peptide = st.sidebar.selectbox("Select peptide", list(predefined_half_lives.keys()), index=0)
    half_life = st.sidebar.number_input(
        "Half-life (days)",
        min_value=0.1,
        value=float(predefined_half_lives[peptide]) if predefined_half_lives[peptide] else 1.0
    )
    target_conc = st.sidebar.number_input("Target concentration (mg)", min_value=0.1, value=2.0)
    dosing_interval = st.sidebar.number_input("Dosing interval (days)", min_value=0.5, value=7.0)
    include_loading_dose = st.sidebar.checkbox("Include loading dose?", value=True)

    k = LN2 / half_life
    maintenance_dose = target_conc * dosing_interval * k

    concentration = np.zeros_like(days, dtype=float)
    concentration[0] = 0  # start at 0 mg

    if include_loading_dose:
        concentration[0] += target_conc  # Instant loading dose

    for t in days:
        start_day = dosing_interval if include_loading_dose else 0
        for d in np.arange(start_day, t + 0.1, dosing_interval):
            if d <= t:
                concentration[t] += maintenance_dose * np.exp(-k * (t - d))

    st.subheader("💡 Dosing Recommendation")
    if include_loading_dose:
        st.markdown(f"- **Loading dose:** {target_conc:.2f} mg at day 0")
    st.markdown(f"- **Maintenance dose:** {maintenance_dose:.2f} mg every {dosing_interval} day(s)")

    fig_plotly = go.Figure()
    fig_plotly.add_trace(go.Scatter(x=days, y=concentration, mode='lines', name='Predicted Concentration'))
    fig_plotly.add_trace(go.Scatter(x=days, y=[target_conc]*len(days), mode='lines', name='Target', line=dict(dash='dash')))
    fig_plotly.update_layout(
        title='Planned Concentration Curve',
        xaxis_title='Days',
        yaxis_title='Concentration (mg)',
        hovermode='x',
        yaxis_tickformat='.2f',
        xaxis_tickformat='.0f'
    )
    st.plotly_chart(fig_plotly, use_container_width=True)

    df = pd.DataFrame({"Day": days, "Concentration (mg)": concentration})
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "target_planned_concentration.csv", "text/csv")

# Default visualizer mode
else:
    num_peptides = st.sidebar.number_input("Number of peptides", min_value=1, max_value=5, value=1)
    compare_mode = st.sidebar.radio("Plot mode", ["Accumulate", "Compare"])

    peptides = []
    for i in range(num_peptides):
        st.sidebar.markdown(f"### Peptide #{i+1}")
        selected = st.sidebar.selectbox(f"Select peptide {i+1}", list(predefined_half_lives.keys()), key=f"name{i}")
        peptide_label = selected
        half_life = st.sidebar.number_input(
            f"{peptide_label} - Half-life (days)",
            min_value=0.1,
            value=float(predefined_half_lives[selected]) if predefined_half_lives[selected] else 1.0,
            key=f"hl{i}"
        )
        dose = st.sidebar.number_input(f"{peptide_label} - Dose (mg)", min_value=0.0, value=1.0, key=f"dose{i}")
        interval = st.sidebar.number_input(f"{peptide_label} - Dosing interval (days)", min_value=1, value=7, key=f"int{i}")
        offset = st.sidebar.number_input(f"{peptide_label} - Start delay (days)", min_value=0, value=0, key=f"offset{i}")
        peptides.append((selected, half_life, dose, interval, offset))

    def calculate_concentration(hl, dose, interval, offset):
        k = LN2 / hl
        conc = np.zeros_like(days, dtype=float)
        for t in days:
            for d in range(offset, t + 1, interval):
                conc[t] += dose * np.exp(-k * (t - d))
        return conc

    df = pd.DataFrame({"Day": days})
    fig = go.Figure()

    for name, hl, dose, interval, offset in peptides:
        conc = calculate_concentration(hl, dose, interval, offset)
        label = name
        if compare_mode == "Compare":
            fig.add_trace(go.Scatter(x=days, y=conc, mode='lines', name=label))
        else:
            df[label] = conc

    if compare_mode == "Accumulate":
        df["Total"] = df[[p[0] for p in peptides]].sum(axis=1)
        fig.add_trace(go.Scatter(x=df["Day"], y=df["Total"], mode='lines', name="Total"))

    fig.update_layout(
        title="Peptide Concentration Over Time",
        xaxis_title="Day",
        yaxis_title="Concentration (mg)",
        hovermode="x",
        yaxis_tickformat='.2f',
        xaxis_tickformat='.0f'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "multi_peptide_concentration.csv", "text/csv")
