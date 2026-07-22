import logging

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from models.model import Annotation, Detection, Fragment, Lipid
from config import get_engine
from utils.data_access import load_database
from utils.db_backup import backup_database
from utils.history import load_history, remove_history
from utils.molecular_weight import molecular_weight
from utils.monoisotopic import monoisotopic_mass

logger = logging.getLogger(__name__)

COLOR = "#1F77B4"
NON_EMPTY_COLUMNS = ["Lipid_name", "Formula", "Precursor_MZ"]

EDITABLE_LIPID_FIELDS = ["Lipid_name", "Lipid_category", "Lipid_class", "Lipid_subclass"]
EDITABLE_DETECTION_FIELDS = ["Num_Peaks", "RT", "CCS"]

EDITOR_KEY = "editor"
HISTORY_KEY = "history_delete"
HISTORY_DEL = "pending_history_delete"
HISTORY_KEY_VERSION = "history_delete_version"
HISTORY_DELETED_MSG = "history_deleted_msg"

# ── Header ────────────────────────────────────────────────────────────────────

st.html(f"""
    <style>
    .module {{
        border: 2px solid {COLOR};
        border-radius: 10px;
        text-align: center;
    }}
    </style>
    <div class="module">
        <h1><span style="color:{COLOR}">MODULE 5</span> : Data management</h1>
    </div>
""")
st.write("")

with st.expander("ℹ️ How to use this page"):
    st.markdown("""
    This page lets you correct or remove data already integrated into BacLipidDB.

    - **Edit & delete records** - edit any cell in the table below. Changing **Formula** automatically
      recomputes **Molecular_weight** and **Monoisotopic_mass**, exactly like the automatic completion
      step of the Integration page. **Precursor_MZ**, **Ionisation_mode** and **Adduct** cannot be edited
      here, as they would require recomputing **Neutral_mass** (derived from **Precursor_MZ** and
      **Adduct** only). Tick the **Delete** box on a row to remove it, then click **Apply changes**.
    - **Delete an entire import** - pick an import from the history and remove every record it
      inserted in one go.

    A database backup is always taken automatically before any change is applied.
    """)

engine = get_engine()

# ── Section 1 : edit / delete individual records ─────────────────────────────

st.header(":blue[Edit & delete records]", divider="blue", text_alignment="left")


def _load_database() -> pd.DataFrame:
    """
    Load the joined table  (Annotation + Lipid + Detection) view used for editing.

    :return: one row per annotation, with the IDs needed to map edits back to the database.
    :rtype: pandas.DataFrame
    """
    return load_database(engine)[[
        "Annotation_ID", "Detection_ID", "Lipid_ID", "Lipid_name", "Formula",
        "Lipid_category", "Lipid_class", "Lipid_subclass", "Precursor_MZ",
        "Ionisation_mode", "Adduct", "Neutral_mass", "Molecular_weight",
        "Monoisotopic_mass", "MS_level", "Num_Peaks", "RT", "CCS",
    ]]


def _database_modif(original: pd.DataFrame, edited: pd.DataFrame) -> dict:
    """
    Diff the edited table against the original one and compute an update/delete plan.

    Rows ticked for deletion are skipped entirely. For the remaining rows, a changed
    **Formula** recomputes Molecular_weight/Monoisotopic_mass - mirroring the automatic
    completion step of the Integration page. **Precursor_MZ**, **Ionisation_mode** and
    **Adduct** are not editable here since Neutral_mass would need recomputing.

    :param original: table as currently stored in the database.
    :type original: pandas.DataFrame
    :param edited: table as returned by the data editor.
    :type edited: pandas.DataFrame
    :return: dict with keys "updates", "deletes" and "errors".
    :rtype: dict
    """
    updates, deletes, errors = [], [], []

    for idx in edited.index:
        new, orig = edited.loc[idx], original.loc[idx]
        label = orig["Lipid_name"]

        if bool(new["Delete"]):
            deletes.append({
                "Annotation_ID": int(orig["Annotation_ID"]),
                "Detection_ID":  int(orig["Detection_ID"]),
                "Lipid_ID":      int(orig["Lipid_ID"]),
                "Lipid_name":    label,
            })
            continue

        for col in NON_EMPTY_COLUMNS:
            if pd.isna(new[col]) or str(new[col]).strip() == "":
                errors.append(f"Row '{label}' : '{col}' cannot be empty.")

        def _changed(col):
            return not (pd.isna(new[col]) and pd.isna(orig[col])) and new[col] != orig[col]

        lipid_fields = {col: new[col] for col in EDITABLE_LIPID_FIELDS if _changed(col)}
        detection_fields = {col: new[col] for col in EDITABLE_DETECTION_FIELDS if _changed(col)}

        if _changed("Formula"):
            lipid_fields["Formula"] = new["Formula"]
            mw, mm = molecular_weight(new["Formula"]), monoisotopic_mass(new["Formula"])
            if mw is None or mm is None:
                errors.append(f"Row '{label}' : cannot compute masses for formula '{new['Formula']}'.")
            else:
                lipid_fields["Molecular_weight"] = mw
                lipid_fields["Monoisotopic_mass"] = mm

        if lipid_fields or detection_fields:
            updates.append({
                "Detection_ID": int(orig["Detection_ID"]),
                "Lipid_ID":     int(orig["Lipid_ID"]),
                "lipid_fields": lipid_fields,
                "detection_fields": detection_fields,
            })

    return {"updates": updates, "deletes": deletes, "errors": errors}


def _apply(plan: dict) -> None:
    """Apply a validated update/delete plan to the database.

    :param plan: plan as returned by _build_plan(), assumed free of errors.
    :type plan: dict
    """
    backup_database(label="manual_edit")
    with Session(engine) as session:
        for d in plan["deletes"]:
            session.query(Fragment).filter(Fragment.Detection_id == d["Detection_ID"]).delete(synchronize_session=False)
            session.query(Annotation).filter(Annotation.Annotation_ID == d["Annotation_ID"]).delete(synchronize_session=False)
            session.query(Detection).filter(Detection.Detection_ID == d["Detection_ID"]).delete(synchronize_session=False)
            session.query(Lipid).filter(Lipid.Lipid_ID == d["Lipid_ID"]).delete(synchronize_session=False)
        for u in plan["updates"]:
            if u["lipid_fields"]:
                session.query(Lipid).filter(Lipid.Lipid_ID == u["Lipid_ID"]).update(u["lipid_fields"], synchronize_session=False)
            if u["detection_fields"]:
                session.query(Detection).filter(Detection.Detection_ID == u["Detection_ID"]).update(u["detection_fields"], synchronize_session=False)
        session.commit()
    load_database.clear()


@st.dialog("Confirm changes")
def _confirm_apply(plan: dict) -> None:
    st.write(f"**{len(plan['updates'])}** row(s) will be updated.")
    st.write(f"**{len(plan['deletes'])}** row(s) will be permanently deleted.")
    if plan["deletes"]:
        st.warning(
            "Deleted records (Detection, Lipid, Annotation and any linked Fragment rows) cannot be "
            "recovered from the app. A database backup is taken automatically beforehand.",
            icon="⚠️",
        )
        for d in plan["deletes"]:
            st.markdown(f"- {d['Lipid_name']}")

    c1, c2 = st.columns(2)
    if c1.button("Confirm", type="primary", width="stretch"):
        _apply(plan)
        st.session_state.pop("pending_plan", None)
        st.session_state.pop(EDITOR_KEY, None)
        st.success("Changes applied.")
        st.rerun()
    if c2.button("Cancel", width="stretch"):
        st.session_state.pop("pending_plan", None)
        st.rerun()


try:
    df_database = _load_database()
except Exception as e:
    logger.exception("Error loading records for editing")
    st.error(f"Error loading records : {e}")
    st.stop()

if df_database.empty:
    st.info("This table contains no data yet.")
else:
    df_new = df_database.copy()
    df_new.insert(0, "Delete", False)

    df_edited = st.data_editor(
        df_new,
        width="stretch",
        num_rows="fixed",
        hide_index=True,
        key=EDITOR_KEY,
        column_config={
            "Delete":            st.column_config.CheckboxColumn(help="Tick to delete this record on Apply."),
            "Annotation_ID":     st.column_config.NumberColumn(disabled=True),
            "Detection_ID":      st.column_config.NumberColumn(disabled=True),
            "Lipid_ID":          st.column_config.NumberColumn(disabled=True),
            "Precursor_MZ":      st.column_config.NumberColumn(format="%.6f", disabled=True),
            "Ionisation_mode":   st.column_config.SelectboxColumn(options=["Positive", "Negative"], disabled=True),
            "Adduct":            st.column_config.TextColumn(disabled=True),
            "Neutral_mass":      st.column_config.NumberColumn(format="%.6f", disabled=True, help="Computed automatically from Precursor_MZ and Adduct."),
            "Molecular_weight":  st.column_config.NumberColumn(format="%.6f", disabled=True, help="Recomputed automatically from Formula."),
            "Monoisotopic_mass": st.column_config.NumberColumn(format="%.6f", disabled=True, help="Recomputed automatically from Formula."),
            "MS_level":          st.column_config.TextColumn(disabled=True),
            "RT":                st.column_config.NumberColumn(format="%.4f"),
            "CCS":               st.column_config.NumberColumn(format="%.4f"),
        },
    )

    if st.button("Apply changes", type="primary", width="stretch"):
        plan = _database_modif(df_database, df_edited)
        if plan["errors"]:
            for error in plan["errors"]:
                st.error(error)
        elif not plan["updates"] and not plan["deletes"]:
            st.info("No changes detected.")
        else:
            st.session_state["pending_plan"] = plan
            st.rerun()

if "pending_plan" in st.session_state:
    _confirm_apply(st.session_state["pending_plan"])

# ── Section 2 : delete an entire import ──────────────────────────────────────

st.divider()
st.header(":blue[Delete an entire import]", divider="blue", text_alignment="left")

def _delete_import(entry: dict, index: int) -> None:
    """
    Delete every record inserted by one import batch, then drop it from the history.

    :param entry: history entry to delete, as returned by load_history().
    :type entry: dict
    :param index: index of the entry within the history file.
    :type index: int
    """
    detection_ids = entry.get("detection_ids", [])
    backup_database(label=f"delete_{entry.get('filename', 'import')}")

    with Session(engine) as session:
        if detection_ids:
            lipid_ids = [
                lid for (lid,) in session.query(Annotation.Lipid_id)
                .filter(Annotation.Detection_id.in_(detection_ids))
                .all()
            ]
            session.query(Fragment).filter(Fragment.Detection_id.in_(detection_ids)).delete(synchronize_session=False)
            session.query(Annotation).filter(Annotation.Detection_id.in_(detection_ids)).delete(synchronize_session=False)
            session.query(Detection).filter(Detection.Detection_ID.in_(detection_ids)).delete(synchronize_session=False)
            if lipid_ids:
                session.query(Lipid).filter(Lipid.Lipid_ID.in_(lipid_ids)).delete(synchronize_session=False)
        session.commit()
    load_database.clear()

    remove_history(index)


@st.dialog("Confirm import deletion")
def _history_del(entry: dict, index: int) -> None:
    detection_ids = entry.get("detection_ids", [])
    st.warning(
        f"This will permanently delete **{len(detection_ids)}** record(s) from "
        f"**{entry.get('filename', '-')}** and remove this entry from the import history. "
        f"A database backup is taken automatically beforehand.",
        icon="⚠️",
    )
    c1, c2 = st.columns(2)
    if c1.button("Confirm deletion", type="primary", width="stretch"):
        _delete_import(entry, index)
        st.session_state.pop(HISTORY_DEL, None)
        # Changer la version de la clé force Streamlit à recréer le widget
        # (un simple pop() ne suffit pas à vider le champ de recherche affiché).
        st.session_state[HISTORY_KEY_VERSION] = st.session_state.get(HISTORY_KEY_VERSION, 0) + 1
        st.session_state[HISTORY_DELETED_MSG] = entry.get("filename", "-")
        st.rerun()
    if c2.button("Cancel", width="stretch"):
        st.session_state.pop("pending_history_delete", None)
        st.rerun()


if HISTORY_DELETED_MSG in st.session_state:
    st.success(f"Import **{st.session_state.pop(HISTORY_DELETED_MSG)}** deleted.")

history = load_history()

if not history:
    st.info("No import history recorded yet.")
else:
    def _label(i: int) -> str:
        e = history[i]
        by = f", by {e.get('integrator')}" if e.get("integrator") else ""
        return f"{e.get('filename', '-')} - {e.get('inserted', '-')} - {e.get('num_rows', '-')} rows{by}"

    selected = st.selectbox(
        "Select an import to delete",
        options=list(range(len(history))),
        format_func=_label,
        index=None,
        key=f"{HISTORY_KEY}_{st.session_state.get(HISTORY_KEY_VERSION, 0)}",
    )

    if selected is not None:
        entry = history[selected]
        detection_ids = entry.get("detection_ids", [])

        with Session(engine) as session:
            remaining = (
                session.query(Detection).filter(Detection.Detection_ID.in_(detection_ids)).count()
                if detection_ids else 0
            )

        st.info(
            f"**{entry.get('filename', '-')}** - imported {entry.get('inserted', '-')} "
            f"by {entry.get('integrator', '-')}\n\n"
            f"{entry.get('num_rows', '-')} row(s) recorded at import time, "
            f"**{remaining}** still present in the database."
        )

        if st.button("Delete this import", type="primary", width="stretch"):
            st.session_state[HISTORY_DEL] = selected
            st.rerun()

if HISTORY_DEL in st.session_state:
    idx = st.session_state[HISTORY_DEL]
    if 0 <= idx < len(history):
        _history_del(history[idx], idx)
    else:
        st.session_state.pop(HISTORY_DEL, None)
