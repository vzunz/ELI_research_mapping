# utils.py

import streamlit as st
import pandas as pd
import unicodedata
import re
from pathlib import Path
from collections import OrderedDict


POLE_COLORS = {
    "ELIA": "#D4A017",
    "ELIC": "#0077BE",
    "ELIE": "#2E8B57",
    "ELIV": "#8E44AD",
    "ELIM": "#C0392B",
}

def header_logo():
    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("images/logo_ELI.png", width=120)

    with col2:
        st.title(f':color[{"Earth and Life Institute"}]{{foreground="rgb(96,136,161)"}}',anchor=False)
        st.markdown(
        f':color[{"Research areas explorer app"}]{{foreground="white" background="rgb(119,191,238)"}}'
        )    

@st.cache_data
def load_data():

    researchers = pd.read_csv(
        "ELI_classification_aca_04.csv",
        sep=";",
        dtype=str
    ).fillna("")

    domains = pd.read_csv(
        "domain_subdomain_03.csv",
        sep=";",
        dtype=str
    ).fillna("")

    return researchers, domains

def extract_domain(sd):

    if sd is None:
        return ""

    sd = str(sd).strip()

    if sd == "":
        return ""

    # D3.2. -> D3
    return sd.split(".")[0]
    
def get_domain_mapping(domains_df):

    mapping_domain = {}
    mapping_subdomain = {}

    for _, row in domains_df.iterrows():

        code = row["Code"].strip()
        
        if code not in mapping_subdomain:
            mapping_subdomain[code] = {
                "subdomain_title": row["Subdomain title"],
                "domain_title": row["Domain title"]
            }

        domain_code = extract_domain(code)

        if domain_code not in mapping_domain:
            mapping_domain[domain_code] = row["Domain title"]

    return mapping_domain,mapping_subdomain

def domain_sort_key(domain_title):
    match = re.match(r"D(\d+)", domain_title)
    return int(match.group(1)) if match else 999


def subdomain_sort_key(subdomain_code):
    """Trie les codes de sous-domaine (ex: 'D3.2.') dans l'ordre naturel
    D1.1, D1.2, ..., D2.1, D2.2, ... plutôt que l'ordre alphabétique."""
    match = re.match(r"D(\d+)\.(\d+)", subdomain_code)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (999, 999)


def strip_domain_prefix(domain_title):
    """Retire le préfixe 'Dx.' au début du titre d'un domaine.
    Exemple : 'D3. Biodiversity, ecology and conservation'
           -> 'Biodiversity, ecology and conservation'
    """
    return re.sub(r"^D\d+\.\s*", "", domain_title).strip()

def score_to_dots(score):
    """Transforme un score numérique en 5 pastilles pleines/vides (●●●○○),
    reprend la logique du script original ELI_research_area_map_01.py."""
    if score is None:
        return ""
    n = min(5, max(1, int(round(score))))
    return "●" * n + "○" * (5 - n)


def render_researcher_grid(
    researchers,
    pole_colors=None,
    session_key="selected_researcher",
    key_prefix="grid",
    ncols=4,
):
    """
    Affiche une grille de cartes cliquables, une par chercheur.

    Au clic sur le bouton sous une carte, le chercheur (dict) est stocké
    dans st.session_state[session_key] puis l'app est relancée (st.rerun()).

    `researchers` peut être un DataFrame pandas ou une liste de
    dict / pandas.Series (une entrée par chercheur).

    Si un champ "score" est présent pour un chercheur (clé "score" dans le
    dict, ou colonne "score" pour une Series), 5 pastilles pleines/vides
    représentant ce score (cf. score_to_dots) sont affichées sous le pôle.
    Ce champ est optionnel : s'il est absent, aucune pastille n'est affichée.

    `key_prefix` doit être unique par grille affichée dans la même page,
    pour éviter toute collision de clés de widgets Streamlit.
    """

    pole_colors = pole_colors or POLE_COLORS

    if isinstance(researchers, pd.DataFrame):
        rows = [row for _, row in researchers.iterrows()]
    else:
        rows = list(researchers)

    if not rows:
        st.info("No researchers to display.")
        return

    for start in range(0, len(rows), ncols):

        cols = st.columns(ncols)
        chunk = rows[start:start + ncols]

        for i, (col, row) in enumerate(zip(cols, chunk)):

            fullname = f"{row['prenom']} {row['nom']}"
            pole = row["pole"]
            color = pole_colors.get(pole, "#777777")

            score = row["score"] if ("score" in row and row["score"] is not None) else None

            with col:
            
                with st.container(border=True):

                    st.markdown(f'<p style="text-align:center; font-size:16px">{row['prenom']}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="text-align:center; font-size:20px"><b>{row['nom']}</b></p>', unsafe_allow_html=True)

                    st.markdown(
                        f':color[{pole}]{{foreground="white" background={color}}}',
                        text_alignment="center"
                        )
                        
                    if score is not None:
                        st.markdown(
                           score_to_dots(score), text_alignment="center"
                        )

                    if st.button(
                        f"Open scientific profile",
                        key=f"{key_prefix}_{start + i}_{fullname}",
                        use_container_width=True,
                    ):
                        st.session_state[session_key] = (
                            row.to_dict() if hasattr(row, "to_dict") else dict(row)
                        )
                        st.rerun()


def display_full_image(image_path, caption=None, width=None):
    """
    Affiche l'image du chercheur avec st.image(). Streamlit ajoute
    automatiquement une icône d'agrandissement (plein écran) sur l'image,
    utilisable au clic (ordinateur) comme au tap (smartphone, tablette) -
    pas besoin de logique JS custom, donc compatible partout.
    """
    if width is not None:
        st.image(str(image_path), caption=caption, width=width)
    else:
        st.image(str(image_path), caption=caption, use_container_width=True)


def strip_keyword_weights(keywords):
    """Retire le poids entre parenthèses de chaque mot-clé.
    Exemple : "soil (0.0514), lichens (0.0467)" -> "soil, lichens"
    """
    if not keywords:
        return keywords

    cleaned = re.sub(r"\s*\([^)]*\)", "", keywords)
    # normalise les espaces autour des virgules restantes
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    return ", ".join(parts)


def sanitize(text):

    if pd.isna(text):
        return ""

    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_-]", "", text)

    return text


def display_profile(researcher, subdomain_map):

    fullname = (
        f"{researcher['prenom']} "
        f"{researcher['nom']}"
    )


    prenom_key = sanitize(researcher["prenom"])
    nom_key = sanitize(researcher["nom"])

    image_file = Path(
        f"images/vosviewer_map_with_title_{nom_key}_{prenom_key}.png"
    )

    if image_file.exists():
        display_full_image(image_file)
    else:
        st.warning("Image not available")


    st.divider()
    
    st.subheader(f"Research domains of {fullname}")

    # ==================================================
    # Construction d'une structure regroupée par domaine
    # ==================================================

    grouped_domains = OrderedDict()

    for i in range(1, 6):

        sd = researcher.get(f"sd{i}", "").strip()

        if not sd:
            continue

        info = subdomain_map.get(sd, {})
        
        domain_title = info.get(
            "domain_title",
            "Unknown domain"
        )

        subdomain_title = info.get(
            "subdomain_title",
            "Unknown domain"
        )

        conf = researcher.get(f"conf{i}", "").strip()
        kw = researcher.get(f"kw{i}", "").strip()

        if domain_title not in grouped_domains:

            grouped_domains[domain_title] = []

        grouped_domains[domain_title].append(
            {
                "code": sd,
                "title": subdomain_title,
                "confidence": conf,
                "keywords": kw
            }
        )

    # ==================================================
    # Affichage
    # ==================================================

    for domain_title in sorted(grouped_domains.keys(), key=domain_sort_key):
        subdomains = grouped_domains[domain_title]

        st.markdown(
            f':color[{strip_domain_prefix(domain_title)}]{{foreground="white" background="rgb(147,185,58)"}}'
            ) 

        for item in subdomains:
        
            if item["keywords"]:

                st.markdown(
                    f"**{item['title']}** • Keywords: {strip_keyword_weights(item['keywords'])}"
                )
                
            else:
            
                st.markdown(
                    f"**{item['title']}**")

            