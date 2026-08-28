import streamlit as st
import pandas as pd
from utils import (display_profile, render_researcher_grid, header_logo, 
    POLE_COLORS, load_data, extract_domain, get_domain_mapping, strip_domain_prefix)

# ====================================================
# CONFIG
# ====================================================

st.set_page_config(
    page_title="ELI research areas",
    layout="wide"
)

# ====================================================
# CHARGEMENT DES CSV
# ====================================================

researchers_df, domains_df = load_data()

# ====================================================
# PAGE HEADER
# ====================================================

header_logo()

# ====================================================
# MAPPING DOMAIN
# ====================================================

domain_map, subdomain_map = get_domain_mapping(domains_df)



# ====================================================
# SESSION STATE
# ====================================================

if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None

if "selected_researcher" not in st.session_state:
    st.session_state.selected_researcher = None
    
# ====================================================
# HEADER
# ====================================================

st.title("ELI research areas")

# ====================================================
# PAGE 1 : DOMAINES
# ====================================================

if st.session_state.selected_domain is None:

    cols = st.columns(2)

    items = list(domain_map.items())

    for idx, (domain_code, domain_title) in enumerate(items):

        with cols[idx % 2]:

            if st.button(
                f"{strip_domain_prefix(domain_title)}",
                use_container_width=True,
                key=f"domain_{domain_code}"
            ):
                st.session_state.selected_domain = domain_code
                st.rerun()

# ====================================================
# PAGE 2 : CHERCHEURS DU DOMAINE
# ====================================================

else:

    current_domain = st.session_state.selected_domain
    selected_researcher = st.session_state.selected_researcher

    st.markdown(f"## {strip_domain_prefix(domain_map[current_domain])}")
    
    if st.button("⬅ ⬅ Back to all research areas"):

        st.session_state.selected_domain = None
        st.session_state.selected_researcher = None

        st.rerun()

# ==================================================
# CAS 1 : PROFIL SELECTIONNE
# ==================================================

    if selected_researcher is not None:

        if st.button(f"⬅ Back to research groups active in {strip_domain_prefix(domain_map[current_domain])}"):

            st.session_state.selected_researcher = None
            st.rerun()

        display_profile(
            selected_researcher,
            subdomain_map
        )

# ==================================================
# CAS 2 : LISTE DES CHERCHEURS
# ==================================================

    else:

        researchers_in_domain = []

        for _, row in researchers_df.iterrows():

            domain_score = 0.0
            matched = False

            for i in range(1, 6):

                sd_col = f"sd{i}"
                conf_col = f"conf{i}"

                if sd_col not in row:
                    continue

                domain = extract_domain(row[sd_col])

                if domain == current_domain:

                    matched = True

                    try:
                        domain_score += float(row.get(conf_col, ""))
                    except (TypeError, ValueError):
                        pass

            if matched:
                row_dict = row.to_dict()
                row_dict["score"] = domain_score
                researchers_in_domain.append(row_dict)

        researchers_in_domain.sort(
            key=lambda r: r["score"],
            reverse=True,
        )

        st.write(
            f"Researchers found: "
            f"**{len(researchers_in_domain)}**"
        )

        render_researcher_grid(
            researchers_in_domain,
            pole_colors=POLE_COLORS,
            session_key="selected_researcher",
            key_prefix=f"dom_{current_domain}",
            ncols=4,
        )