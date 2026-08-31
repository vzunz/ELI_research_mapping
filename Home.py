import streamlit as st
from utils import (load_data, extract_domain, get_domain_mapping, 
    subdomain_sort_key, strip_domain_prefix, header_logo)

# ====================================================
# CONFIG
# ====================================================

st.set_page_config(
    page_title="ELI Research Areas",
    layout="wide"
)

# ====================================================
# CHARGEMENT DES CSV
# ====================================================

researchers_df, domains_df = load_data()

# ====================================================
# MAPPING DOMAIN
# ====================================================

domain_map, subdomain_map = get_domain_mapping(domains_df)

# ====================================================
# HOME / WELCOME PAGE
# ====================================================

header_logo()

#st.title("ELI Research Areas")

st.markdown(
    """
    This app lets you explore the research areas covered by the [Earth and Life
    Institute](https://uclouvain.be/en/research-institutes/eli) (ELI, UCLouvain) research groups.
    
    Each research group is represented by one academic member.

    Use the sidebar (or the shortcuts below) to navigate.
    """
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Research areas",anchor=False)
        st.write(
            "Browse the 10 research areas. Click a research area to see "
            "the academics active in it, with an indicator "
            "(●●●○○) showing how strongly each one is associated with that "
            "research area. Click an academic's card to open their full scientific profile."
        )
        if st.button(
            "Go to research areas",
            use_container_width=True
        ):
            st.switch_page("pages/1_Research_areas.py")
    
    
with col2:
    with st.container(border=True):
        st.subheader("Research groups",anchor=False)
        st.write(
            "Browse all research groups at once, regardless of research areas — sortable "
            "by academic name or by pole. Click an academic's card to open their full "
            "scientific profile."
        )
        st.markdown('<br>',unsafe_allow_html=True)
        if st.button(
            "Go to research groups",
            use_container_width=True
        ):
            st.switch_page("pages/2_Research_groups.py")

st.subheader("How was the classification performed?",anchor=False)

st.write(
    "The classification approach used here combines bibliometric keyword analysis with AI-assisted thematic "
    "classification.\n"
    )

st.write(
    "For each academic, "
    "a list of scientific publications was retrieved from the [Scopus](https://www.scopus.com/) database. "
    "A keyword analysis was then performed using [VOSviewer](https://www.vosviewer.com), based on both Author "
    "Keywords and Index Keywords. This analysis generated a keywords occurrence map "
    "for each academic, highlighting the most prominent research topics within their "
    "publication record."
    "For academics with an insufficient number of publications indexed in Scopus, "
    "publication data were retrieved from the [OpenAlex](https://openalex.org) database. "
    )
    
st.write(
    "For each academic, the 50 most frequently occurring keywords were extracted "
    "from the VOSviewer analysis. A weight was assigned to each keyword according to "
    "its frequency of occurrence, providing an estimate of its relative importance "
    "within the academic's research portfolio. The complete set of weighted keywords "
    "for all academics was subsequently analyzed using Microsoft Copilot. Based on "
    "this corpus, Copilot identified a classification structure composed "
    "of 10 main research areas and 5 sub-areas within each research areas. "
    )
    
st.write(
	"In a second step, the 50 largest weighted keywords of each academic was submitted "
    "to Copilot in order to assign the most relevant research sub-areas. "
    "For each academic, up to five research sub-areas were attributed. "
    "A score was also assigned to each subdomain to reflect the relative level of "
    "engagement and specialization of the academic within that research area."
    )


st.write("Below is the classification structure of the research areas in ELI.")

items = list(domain_map.items())

col1, col2 = st.columns(2)
cols = [col1, col2]

for idx, (domain_code, domain_title) in enumerate(items):

    with cols[idx % 2]:
      
        st.markdown(
            f':color[{strip_domain_prefix(domain_title)}]{{foreground="white" background="rgb(147,185,58)"}}'
            ) 

        subdomains_for_domain = sorted(
            (
                (code, info["subdomain_title"])
                for code, info in subdomain_map.items()
                if extract_domain(code) == domain_code
            ),
            key=lambda item: subdomain_sort_key(item[0]),
        )

        for code, subdomain_title in subdomains_for_domain:
            st.markdown(f"- {subdomain_title}")

    