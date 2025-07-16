import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Peptide preset half-lives (days)
peptide_half_lives = {
    "GLP-3": 6,
    "BPC-157": 0.5,
    "CJC-1295 (w/o DAC)": 0.5,
    "CJC-1295 (with DAC)": 6,
    "Thymosin Beta-4": 2,
    "Custom": None
}

st.title("🧪 Peptide Concentration Over Time Calculator")

# Sidebar inputs
selected_peptide = st.selectbox("Choose a peptide", list(peptide_half_lives.keys()), index=0)

# Use predefined half-life or allow custom
if peptide_half_lives[selected_peptide] is None:
    half_life = st.number_input("Enter peptide half-life (days)", min_value=0.1, value=3.0)
else:
    half_life = peptide_half_lives[selected_peptide]

dose_mg = st.number_input("Dose per injection (mg)", min_value=0.0, value=1.0)
interval_days = st.number_input("Dosing interval (days)", min_value=1, value=1)
duration_days = st.number_input("Total duration of simulation (days)", min_value=1, value=30)

stop_day = st.number_input("Stop dosing after X days (optional)", min_value=0, max_value=duration_days, value=duration_days)

# Calculation logic
def calculate_concentration(dose, half_life, interval, total_days, stop_day):
    k = np.log(2) / half_life
    days = np.arange(0, total_days + 1)
    concentrations = np.zeros_like(days, dtype=float)

    for t in days:
        for d in range(0, int(min(t + 1, stop_day + 1)), interval):
            concentrations[t] += dose * np.exp(-k * (t - d))
    return days, concentrations

# Run calculation
days, concentrations = calculate_concentration(dose_mg, half_life, interval_days, duration_days, stop_day)

# Display chart
fig, ax = plt.subplots()
ax.plot(days, concentrations, label="Concentration (mg)")
ax.set_xlabel("Days")
ax.set_ylabel("Concentration (mg)")
ax.set_title("Peptide Concentration Over Time")
ax.grid(True)
st.pyplot(fig)

# Display table
df = pd.DataFrame({"Day": days, "Concentration (mg)": concentrations})
st.dataframe(df)

# Download option
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "peptide_concentration.csv", "text/csv")
