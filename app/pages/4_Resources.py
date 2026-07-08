import streamlit as st
import pandas as pd
import io

# ── Header ────────────────────────────────────────────────────────────────────

st.html("""
    <style>
    .module {
        border: 2px solid #1F77B4;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    <div class="module">
        <h1><span style="color:#1F77B4">MODULE 4</span> : Resources</h1>
    </div>
""")
st.write("")

# ── Column guide ──────────────────────────────────────────────────────────────

st.subheader("MS1 integration - column guide")
st.write("")

guide = pd.DataFrame(
    [
        {
            "Column": "Lipid_Name",
            "Required": "✅",
            "Type": "text",
            "Description": "Unique identifier of the lipid (PG 30:0)",
        },
        {
            "Column": "Formula",
            "Required": "✅",
            "Type": "text",
            "Description": "Molecular formula in Hill notation (C36H71O10P)",
        },
        {
            "Column": "Precursor_MZ",
            "Required": "✅",
            "Type": "float",
            "Description": "Precursor ion m/z measured by the mass spectrometer (694.478487)",
        },
        {
            "Column": "Lipid_category",
            "Required": "✅",
            "Type": "text",
            "Description": "LIPID MAPS category (Glycerophospholipids (GP))",
        },
        {
            "Column": "Lipid_class",
            "Required": "✅",
            "Type": "text",
            "Description": "Lipid class (Glycerophosphoglycerols (GP04))",
        },
        {
            "Column": "Lipid_subclass",
            "Required": "✅",
            "Type": "text",
            "Description": "Lipid subclass (Diacylglycerophosphoglycerols (GP0401))",
        },
        {
            "Column": "RT",
            "Required": "❌",
            "Type": "float",
            "Description": "Retention time in minutes (leave empty if not available)",
        },
        {
            "Column": "CCS",
            "Required": "❌",
            "Type": "float",
            "Description": "Collision cross section in Å² (leave empty if not available)",
        },
    ]
)

st.dataframe(guide, hide_index=True, width="stretch")

st.divider()

# ── Templates ─────────────────────────────────────────────────────────────────

st.subheader("Templates")
st.write("")

template_ms1 = pd.DataFrame(
    [
        {
            "Lipid_Name": "PG 30:0",
            "Formula": "C36H71O10P",
            "Precursor_MZ": 694.478487,
            "Lipid_category": "Glycerophospholipids (GP)",
            "Lipid_class": "Glycerophosphoglycerols (GP04)",
            "Lipid_subclass": "Diacylglycerophosphoglycerols (GP0401)",
            "RT": "",
            "CCS": "",
        }
    ]
)

csv_buffer = io.StringIO()
template_ms1.to_csv(csv_buffer, index=False)

st.download_button(
    label="Download MS1 template (.csv)",
    data=csv_buffer.getvalue(),
    file_name="BacLipidDB_MS1_template.csv",
    mime="text/csv",
    type="primary",
)

st.caption(
    "The template contains the 6 required columns and the 2 optional columns (RT, CCS). Leave optional columns empty if not available."
)
