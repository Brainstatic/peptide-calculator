# 🧪 Peptide Concentration Calculator + Target Planner

This upgraded Streamlit app models peptide concentration over time and includes a powerful reverse-planning tool to help you design effective dosing protocols.

## 🚀 Features

### 🔍 Mode 1: Visualize Dosing Schedule
- Plot up to 5 peptides with individual:
  - Names and half-lives
  - Doses
  - Dosing intervals
  - Start delays (offsets)
- Compare vs Accumulate mode
- Pre-loaded with peptides like:
  - GLP-3, Semaglutide, Tirzepatide, Retatrutide, CJC-1295, BPC-157

### 🎯 Mode 2: Plan for Target Concentration
- Enter your desired steady-state concentration (e.g., 5 mg)
- Select peptide and interval
- App calculates:
  - **Maintenance dose** needed to sustain that level
  - Optional **loading dose** to reach target quickly
- Simulated graph and downloadable CSV

## 📸 Example

![screenshot-placeholder](https://via.placeholder.com/800x400?text=App+Preview+Coming+Soon)

## 🧠 Behind the Scenes

The app uses exponential decay and pharmacokinetic formulas:
```
C_ss = (Dose × F) / (tau × k)  
k = ln(2) / t_half
```

This helps visualize buildup and identify ideal dosing strategies based on half-life.

## 💻 How to Use

1. Clone or upload this repo to GitHub
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
streamlit run peptide_calculator.py
```

Or deploy online using [Streamlit Cloud](https://streamlit.io/cloud)

## 📁 Included Files

- `peptide_calculator.py` — main app
- `requirements.txt` — dependencies

## ⚠️ Disclaimer

This tool is for **informational and educational use only**. It does not provide medical advice and should not be used to guide real-world treatment decisions.

---
Created with ❤️ by Wesley Adams
