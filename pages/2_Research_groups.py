import streamlit as st
import pandas as pd

from utils import display_profile, render_researcher_grid, POLE_COLORS, load_data, header_logo

st.set_page_config(
    page_title="Research groups",
    layout="wide"
)

# ------------------------------------------------------------------
# Chargement des données
# ------------------------------------------------------------------

#@st.cache_data

researchers_df, domains_df = load_data()

subdomain_map = {}

for _, row in domains_df.iterrows():

    code = row["Code"].strip()

    if code not in subdomain_map:
        subdomain_map[code] = {
            "subdomain_title": row["Subdomain title"],
            "domain_title": row["Domain title"]
        }

# ------------------------------------------------------------------
# Session state propre à cette page
# (indépendant de "selected_researcher" utilisé par app.py, pour que
# la sélection faite depuis une page domaine n'interfère pas ici)
# ------------------------------------------------------------------

if "researcher_page_selection" not in st.session_state:
    st.session_state.researcher_page_selection = None

selected_researcher = st.session_state.researcher_page_selection

# ====================================================
# PAGE HEADER
# ====================================================

header_logo()

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------

st.title("Research groups",anchor=False)

# ==================================================
# CAS 1 : UN CHERCHEUR EST SELECTIONNE -> PROFIL COMPLET
# ==================================================

if selected_researcher is not None:

    if st.button("⬅ Back to all research groups"):
        st.session_state.researcher_page_selection = None
        st.rerun()

    st.divider()

    display_profile(
        selected_researcher,
        subdomain_map
    )

# ==================================================
# CAS 2 : LISTE DE TOUS LES CHERCHEURS
# ==================================================

else:

    st.write(
        f"Research groups found: "
        f"**{len(researchers_df)}**"
    )

    sort_mode = st.radio(
        "Sort by",
        options=["Name (A-Z)", "Pole, then name (A-Z)"],
        horizontal=True,
        key="researcher_sort_mode",
    )

    if sort_mode == "Name (A-Z)":
        sort_columns = ["nom"]
    else:
        sort_columns = ["pole", "nom"]

    researchers_sorted = researchers_df.sort_values(
        by=sort_columns,
        key=lambda col: col.str.lower(),
    ).reset_index(drop=True)

    render_researcher_grid(
        researchers_sorted,
        pole_colors=POLE_COLORS,
        session_key="researcher_page_selection",
        key_prefix="allres",
        ncols=4,
    )
