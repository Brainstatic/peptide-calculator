import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

duration_weeks = st.sidebar.number_input("Simulation duration (weeks)", min_value=1, value=12)
total_days = duration_weeks * 7
days = np.arange(0, total_days + 1)

# Reverse planning mode
if mode == "Plan for target concentration":
    st.sidebar.markdown("## Target Planning Inputs")
    peptide = st.sidebar.selectbox("Select peptide", list(predefined_half_lives.keys()), index=0)
    half_life = st.sidebar.number_input(
        "Half-life (days)", min_value=0.1,
        value=predefined_half_lives[peptide] if predefined_half_lives[peptide] else 1.0
    )
    target_conc = st.sidebar.number_input("Target concentration (mg)", min_value=0.1, value=5.0)
    dosing_interval = st.sidebar.number_input("Dosing interval (days)", min_value=0.5, value=1.0)
    include_loading_dose = st.sidebar.checkbox("Include loading dose?", value=True)

    k = LN2 / half_life
    maintenance_dose = target_conc * dosing_interval * k

    # Build simulation
    concentration = np.zeros_like(days, dtype=float)
    if include_loading_dose:
        concentration[0] += target_conc  # Instant loading dose

    for t in days:
        for d in np.arange(0, t + 0.1, dosing_interval):
            if d <= t:
                concentration[t] += maintenance_dose * np.exp(-k * (t - d))

    # Display results
    st.subheader("💡 Dosing Recommendation")
    if include_loading_dose:
        st.markdown(f"- **Loading dose:** {target_conc:.2f} mg at day 0")
    st.markdown(f"- **Maintenance dose:** {maintenance_dose:.2f} mg every {dosing_interval} day(s)")

    fig, ax = plt.subplots()
    ax.plot(days, concentration, label="Predicted Concentration")
    ax.axhline(y=target_conc, color='gray', linestyle='--', label="Target")
    ax.set_xlabel("Days")
    ax.set_ylabel("Concentration (mg)")
    ax.set_title("Planned Concentration Curve")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

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
        half_life = st.sidebar.number_input(
            f"Half-life (days) {i+1}",
            min_value=0.1,
            value=predefined_half_lives[selected] if predefined_half_lives[selected] else 1.0,
            key=f"hl{i}"
        )
        dose = st.sidebar.number_input(f"Dose (mg) {i+1}", min_value=0.0, value=1.0, key=f"dose{i}")
        interval = st.sidebar.number_input(f"Dosing interval (days) {i+1}", min_value=1, value=7, key=f"int{i}")
        offset = st.sidebar.number_input(f"Start delay (days) {i+1}", min_value=0, value=0, key=f"offset{i}")
        peptides.append((selected, half_life, dose, interval, offset))

    def calculate_concentration(hl, dose, interval, offset):
        k = LN2 / hl
        conc = np.zeros_like(days, dtype=float)
        for t in days:
            for d in range(offset, t + 1, interval):
                conc[t] += dose * np.exp(-k * (t - d))
        return conc

    df = pd.DataFrame({"Day": days})
    fig, ax = plt.subplots(figsize=(10, 5))

    for name, hl, dose, interval, offset in peptides:
        conc = calculate_concentration(hl, dose, interval, offset)
        label = name
        if compare_mode == "Compare":
            ax.plot(days, conc, label=label)
        else:
            df[label] = conc

    if compare_mode == "Accumulate":
        df["Total"] = df[[p[0] for p in peptides]].sum(axis=1)
        ax.plot(df["Day"], df["Total"], label="Total", linewidth=2)

    ax.set_title("Peptide Concentration Over Time")
    ax.set_xlabel("Day")
    ax.set_ylabel("Concentration (mg)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "multi_peptide_concentration.csv", "text/csv")
