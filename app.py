"""Optional local dashboard: streamlit run app.py"""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
TABLES = ROOT / "results" / "tables"

st.set_page_config(page_title="Quantum Readiness Overview", page_icon="⚛️", layout="wide")
st.title("⚛️ Quantum Readiness Overview")
st.caption("P2 prototype: authorized evidence → explainable inventory risk → migration roadmap → architecture benchmark")

scored = pd.read_csv(TABLES / "inventory_scored.csv")
comparison = pd.read_csv(TABLES / "final_comparison.csv")

page = st.sidebar.radio("Explore", ["Overview", "Inventory & roadmap", "Processor A/B"])

if page == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cryptographic assets", len(scored))
    c2.metric("Assets requiring assessment", int((scored["risk_level"] != "Safe").sum()))
    c3.metric("Phase 1 assets", int(scored["phase"].str.startswith("Phase 1").sum()))
    c4.metric("HNDL flagged", int(scored["HNDL"].sum()))
    st.subheader("What this prototype proves")
    st.markdown("""
    - The inventory scorer explains *why* an asset is risky instead of treating every non-PQC algorithm identically.
    - The migration roadmap prioritizes by phase, risk score, and sensitivity.
    - The Qiskit benchmark is a separate architecture study: it does **not** estimate the cost of attacking real RSA/ECC keys.
    - Processor definitions are placeholders until the official Challenge Kit values are supplied.
    """)
    st.bar_chart(scored.groupby("phase").size().rename("assets"))
elif page == "Inventory & roadmap":
    st.subheader("Prioritized migration roadmap")
    st.dataframe(scored[["priority_rank", "asset_name", "algorithm", "cryptographic_role", "risk_level", "risk_score", "HNDL", "migration", "phase"]], use_container_width=True, hide_index=True)
    selected = st.selectbox("Inspect evidence", scored["asset_name"].tolist())
    row = scored.loc[scored["asset_name"] == selected].iloc[0]
    st.info(f"**Risk rationale:** {row['risk_rationale']}\n\n**Next step:** {row['migration']} ({row['migration_effort']} effort).")
else:
    st.subheader("Measured Processor A/B comparison")
    metric = st.selectbox("Metric", ["success_probability", "depth", "two_qubit_gates", "swap_estimate", "total_ops"])
    chart = comparison[comparison["Metric"] == metric].set_index("Metric")[["Processor A", "Processor B"]]
    st.bar_chart(chart)
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    st.caption("All values come from the generated CSVs. Runtime and topology figures are simulator/environment evidence, not hardware claims.")
