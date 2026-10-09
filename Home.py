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

st.info(
    "**Beta version — work in progress.** This application is still under active "
    "development. The research area classification is computed automatically from "
    "publications and research projects and may not fully reflect the scope of each "
    "research group. Content, features and results may change as the application evolves.",
    icon="🚧",
)

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
    "Each academic is profiled from two sources: their **scientific publications** and the "
    "**research projects** they have led at UCLouvain. Both are mapped onto a common grid of "
    "10 research areas and 46 sub-areas, shown below. This grid was built from the topics "
    "that actually appear in ELI publications and projects, so that every research group "
    "finds its place in it (marine biology, microbiology, forests, planetary science, "
    "One Health, etc.)."
    )

st.write(
    "**Publications.** The publication list of each academic was exported from "
    "[Scopus](https://www.scopus.com/) and completed with references found only in "
    "[OpenAlex](https://openalex.org) (these count for half, as OpenAlex attributions are "
    "less reliable). Each publication is assigned to one or more sub-areas from its "
    "author and index keywords, or, when no keyword is informative, from its title and "
    "abstract. Overly generic keywords (e.g. *article*, *human*, *soil*, country names) are "
    "ignored. Each publication counts once and is shared among the sub-areas it covers."
    )

st.write(
    "**Research projects.** Projects recorded at UCLouvain since 2013 were classified in "
    "the same grid from their titles and keywords. Administrative agreements, start-up "
    "grants and other projects without a scientific topic were left out."
    )

st.write(
    "**Recent work counts more.** A publication from ten years ago weighs half as much as "
    "a publication from this year (eight years for projects), so that profiles reflect "
    "current expertise rather than past topics."
    )

st.write(
    "**Combining both sources.** For each academic, the share of each sub-area is computed "
    "as 70% publications and 30% projects (or from a single source when only one is "
    "available). Up to five sub-areas covering at least 5% of the academic's work are shown. "
    "The indicator reflects that share: ●○○○○ below 15%, ●●○○○ around 20%, ●●●○○ around 30%, "
    "●●●●○ around 40% and ●●●●● 45% or more. The keywords listed next to each sub-area are "
    "the ones that contributed most to it."
    )

st.write(
    "The keyword maps shown in each profile were produced with "
    "[VOSviewer](https://www.vosviewer.com) from the same Scopus publications. They were used "
    "to check the classification: the main sub-area obtained from publications matches the "
    "one suggested by the VOSviewer keywords for 46 of the 47 academics."
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

    
