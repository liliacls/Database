import streamlit as st
import pandas as pd
import io
import csv
import _bootstrap
from utils.neutral_mass import (
    ADDUCT_SHIFTS,
    ADDUCT_SIGNS,
    add_adduct,
    list_adducts,
    remove_adduct,
)

# ── En-tête ───────────────────────────────────────────────────────────────────

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

# ── Guide des colonnes ────────────────────────────────────────────────────────

st.subheader("MS1 integration - column guide")
st.write("")

st.caption(
    "⚠️ Field labels are case-sensitive : use the exact capitalization shown below."
)

guide_ms1 = pd.DataFrame(
    [
        {
            "Column": "Precursor_MZ",
            "Required": "✅",
            "Type": "float",
            "Description": "Precursor ion m/z measured by the mass spectrometer (694.478487)",
        },
        {
            "Column": "Adduct",
            "Required": "✅",
            "Type": "text",
            "Description": "Precursor adduct : Determines the neutral "
                            "mass calculation and is independent of the ionization mode.",
        },
        {
            "Column": "Formula",
            "Required": "✅",
            "Type": "text",
            "Description": "Molecular formula in Hill notation (C36H71O10P)",
        },
        {
            "Column": "FA_composition",
            "Required": "❌",
            "Type": "text",
            "Description": "Fatty acid composition (leave empty if not available)",
        },
        {
            "Column": "Lipid_Name",
            "Required": "✅",
            "Type": "text",
            "Description": "Unique identifier of the lipid (PG 30:0)",
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

st.dataframe(guide_ms1, hide_index=True, width="stretch")

st.divider()

# ── Modèles ───────────────────────────────────────────────────────────────────

st.subheader("Templates")
st.write("")

template_ms1 = pd.DataFrame(
    [
        {
            "Precursor_MZ": 716.52358,
            "Adduct": "[M-H]-",
            "Formula": "C39H76NO8P",
            "FA_composition": "",
            "Lipid_Name": "PE 34:1",
            "Lipid_category": "Glycerophospholipids (GP)",
            "Lipid_class": "Glycerophosphoethanolamines (GP02)",
            "Lipid_subclass": "Diacylglycerophosphoethanolamines (GP0201)",
            "RT": "",
            "CCS": "",
        }
    ]
)

generate_csv = io.StringIO()
template_ms1.to_csv(generate_csv, index=False)

st.download_button(
    label="Download MS1 template (.csv)",
    data=generate_csv.getvalue(),
    file_name="BacLipidDB_MS1_template.csv",
    mime="text/csv",
    type="primary",
)

st.caption(
    "The template contains the 7 required columns and the 3 optional columns (FA_composition, RT, CCS). Leave optional columns empty if not available."
)

st.divider()

# ── Guide des colonnes MS2 ───────────────────────────────────────────────────────

st.subheader("MS2 integration - column guide")
st.write("")

st.markdown(
    "MS2 files are organized in blocks stacked vertically, one block per scan, separated by a "
    "single blank line. Each block starts with a `Scan #<id>` line, followed by one "
    "`Label,Value` line per field (any order), the `m/z,Intensity` header, then the fragment rows :"
)

st.code(
    "Scan #<id>\n"
    "Precursor_MZ,<precursor_mz>\n"
    "Adduct,<adduct>\n"
    "Formula,<formula>\n"
    "FA_composition,<fa_composition>\n"
    "Lipid_Name,<lipid_name>\n"
    "Lipid_category,<lipid_category>\n"
    "Lipid_class,<lipid_class>\n"
    "Lipid_subclass,<lipid_subclass>\n"
    "Num_peaks,<count>\n"
    "m/z,Intensity\n"
    "<mz_1>,<intensity_1>\n"
    "<mz_2>,<intensity_2>\n"
    "...",
    language="text",
)

st.caption(
    "⚠️ Field labels are case-sensitive : use the exact capitalization shown below."
)

guide_ms2 = pd.DataFrame(
    [
        {
            "Column": "Scan #<id>",
            "Required": "✅",
            "Type": "text",
            "Description": "First cell of the scan block, must start with 'Scan #' (Scan #2183)",
        },
        {
            "Column": "Precursor_MZ",
            "Required": "✅",
            "Type": "float",
            "Description": "Precursor ion m/z measured by the mass spectrometer (716.5236)",
        },
        {
            "Column": "Adduct",
            "Required": "✅",
            "Type": "text",
            "Description": "Precursor adduct : Determines the neutral "
                            "mass calculation and is independent of the ionization mode.",
        },
        {
            "Column": "Formula",
            "Required": "✅",
            "Type": "text",
            "Description": "Molecular formula in Hill notation (C39H76NO8P)",
        },
        {
            "Column": "FA_composition",
            "Required": "❌",
            "Type": "text",
            "Description": "Fatty acid composition (16:0_18:1) (delete this column if not available)",
        },
        {
            "Column": "Lipid_Name",
            "Required": "✅",
            "Type": "text",
            "Description": "Unique identifier of the lipid (PE 34:1)",
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
            "Description": "Lipid class (Glycerophosphoethanolamines (GP02))",
        },
        {
            "Column": "Lipid_subclass",
            "Required": "✅",
            "Type": "text",
            "Description": "Lipid subclass (Diacylglycerophosphoethanolamines (GP0201))",
        },
        {
            "Column": "Num_peaks",
            "Required": "✅",
            "Type": "int",
            "Description": "Number of fragment peaks in the scan (6). Must match the number of "
                            "m/z/Intensity rows",
        },
        {
            "Column": "m/z",
            "Required": "✅",
            "Type": "float",
            "Description": "Fragment ion m/z, one row per fragment peak (255.232772827)",
        },
        {
            "Column": "Intensity",
            "Required": "✅",
            "Type": "float",
            "Description": "Fragment peak intensity (292725.5)",
        },
        {
            "Column": "RT",
            "Required": "❌",
            "Type": "float",
            "Description": "Retention time in minutes (delete this column if not available)",
        },
        {
            "Column": "CCS",
            "Required": "❌",
            "Type": "float",
            "Description": "Collision cross section in Å² (delete this column if not available)",
        },
    ]
)

st.dataframe(guide_ms2, hide_index=True, width="stretch")

template_ms2 = [
    ["Scan #2183"],
    ["Precursor_MZ", 716.5236],
    ["Adduct", "[M-H]-"],
    ["Formula", "C39H76NO8P"],
    ["FA_composition", "16:0_18:1"],
    ["Lipid_Name", "PE 34:1"],
    ["Lipid_category", "Glycerophospholipids (GP)"],
    ["Lipid_class", "Glycerophosphoethanolamines (GP02)"],
    ["Lipid_subclass", "Diacylglycerophosphoethanolamines (GP0201)"],
    ["RT", 6.42],
    ["CCS", 245.8],
    ["Num_peaks", 6],
    ["m/z", "Intensity"],
    [122.001441956, 10847.9541015625],
    [140.01121521, 40577.88671875],
    [255.232772827, 292725.5],
    [281.248474121, 754703.9375],
    [452.27734375, 14803.171875],
    [716.52355957, 806111.1875],
    [],
    ["Scan #1743"],
    ["Precursor_MZ", 747.5182],
    ["Adduct", "[M-H]-"],
    ["Formula", "C40H77O10P"],
    ["FA_composition", "16:0_18:1"],
    ["Lipid_Name", "PG 34:1"],
    ["Lipid_category", "Glycerophospholipids (GP)"],
    ["Lipid_class", "Glycerophosphoglycerols (GP04)"],
    ["Lipid_subclass", "Diacylglycerophosphoglycerols (GP0401)"],
    ["Num_peaks", 3],
    ["m/z", "Intensity"],
    [255.233078003, 31095.443359375],
    [281.248596191, 88691.546875],
    [747.518249512, 133242.75],
]

generate_file = io.StringIO()
csv.writer(generate_file).writerows(template_ms2)

st.download_button(
    label="Download MS2 template (.csv)",
    data=generate_file.getvalue(),
    file_name="BacLipidDB_MS2_template.csv",
    mime="text/csv",
    type="primary",
)

st.caption(
    "The template contains 2 example scans showing the expected block structure, separated by a single blank "
    "line. The first scan includes the optional RT and CCS fields, the second shows that these lines can be "
    "omitted entirely when not available."
)

st.divider()

# ── Adduits ───────────────────────────────────────────────────────────────────

st.subheader("Adducts")
st.write("")

st.markdown(
    "Adducts accepted in the `Adduct` column (MS1 and MS2 integration). Custom adducts added "
    "below are saved locally and stay available across sessions."
)

custom_adducts = list_adducts()

adducts_table = pd.DataFrame(
    [
        {
            "Adduct": name,
            "Mass shift (Da)": ADDUCT_SHIFTS[name],
            "Operation to get neutral mass": "m/z − shift" if ADDUCT_SIGNS[name] == -1 else "m/z + shift",
            "Custom": "✅" if name in custom_adducts else "❌",
        }
        for name in ADDUCT_SHIFTS
    ]
)

st.dataframe(adducts_table, hide_index=True, width="stretch")

st.write("")

with st.form("add_adduct_form", clear_on_submit=True):
    st.markdown("**Add a custom adduct**")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_name = st.text_input("Adduct name", placeholder="[M+Cl]-")
    with col2:
        new_shift = st.number_input("Mass shift (Da)", min_value=0.0, step=0.000001, format="%.6f")
    with col3:
        new_operation = st.radio(
            "Ion formed by",
            ["Addition (e.g. [M+H]+, [M+Na]+)", "Loss (e.g. [M-H]-)"],
        )
    submitted = st.form_submit_button("Add adduct", type="primary")

if submitted:
    sign = -1 if new_operation.startswith("Addition") else 1
    try:
        add_adduct(new_name, new_shift, sign)
        st.success(f"Adduct '{new_name.strip()}' added.")
        st.rerun()
    except ValueError as e:
        st.error(str(e))

if custom_adducts:
    st.write("")
    col1, col2 = st.columns([3, 1])
    with col1:
        to_remove = st.selectbox("Remove a custom adduct", list(custom_adducts))
    with col2:
        st.write("")
        st.write("")
        if st.button("Remove"):
            remove_adduct(to_remove)
            st.rerun()
