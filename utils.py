# utils.py

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import unicodedata
import re
import base64
from pathlib import Path
from collections import OrderedDict
from PIL import Image


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
        st.title(f':color[{"Earth and Life Institute"}]{{foreground="rgb(96,136,161)"}}')
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
            
                with st.container(height=250):
                    st.subheader(fullname,text_alignment="center")
                    st.markdown(
                        f':color[{pole}]{{foreground="white" background={color}}}',
                        text_alignment="center"
                        )
                        
                    st.markdown(
                       score_to_dots(score),text_alignment="center"
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


@st.cache_data(show_spinner=False)
def _image_to_data_uri(path):
    """Encode une image locale en data URI base64, pour pouvoir l'intégrer
    dans du HTML/JS injecté via components.html (pas d'accès direct au
    système de fichiers depuis l'iframe)."""

    suffix = Path(path).suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/{mime};base64,{encoded}"


def display_magnifier_image(image_path, max_width=1000, zoom=2.5, glass_size=180):
    """
    Affiche une image avec une vraie loupe : au survol, une lentille
    circulaire suit précisément le curseur et affiche un zoom local de la
    zone survolée (et non toute l'image qui s'agrandit).

    Implémenté via streamlit.components.v1.html plutôt que st.markdown, car
    le JavaScript inséré via st.markdown(unsafe_allow_html=True) ne s'exécute
    pas dans le navigateur (limitation de Streamlit) - components.html rend
    le contenu dans une iframe où le JS fonctionne normalement.
    """

    data_uri = _image_to_data_uri(image_path)

    with Image.open(image_path) as im:
        orig_w, orig_h = im.size

    display_w = min(max_width, orig_w)
    display_h = int(orig_h * (display_w / orig_w)) if orig_w else 0

    html = f"""
    <style>
        html, body {{ margin:0; padding:0; }}
        .img-magnifier-container {{
            position: relative;
            width: {display_w}px;
            height: {display_h}px;
        }}
        .img-magnifier-container img {{
            width: {display_w}px;
            height: {display_h}px;
            display: block;
            border-radius: 6px;
        }}
        .img-magnifier-glass {{
            position: absolute;
            border: 3px solid #ffffff;
            border-radius: 50%;
            cursor: none;
            width: {glass_size}px;
            height: {glass_size}px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.45);
            display: none;
            pointer-events: none;
        }}
    </style>

    <div class="img-magnifier-container">
        <img id="magnifier-img" src="{data_uri}">
    </div>

    <script>
    (function() {{
        var img = document.getElementById("magnifier-img");
        var zoom = {zoom};

        var glass = document.createElement("DIV");
        glass.setAttribute("class", "img-magnifier-glass");
        img.parentElement.appendChild(glass);

        glass.style.backgroundImage = "url('" + img.src + "')";
        glass.style.backgroundRepeat = "no-repeat";
        glass.style.backgroundSize =
            (img.width * zoom) + "px " + (img.height * zoom) + "px";

        var w = glass.offsetWidth / 2;
        var h = glass.offsetHeight / 2;

        function getCursorPos(e) {{
            var a = img.getBoundingClientRect();
            var x = e.pageX - a.left - window.pageXOffset;
            var y = e.pageY - a.top - window.pageYOffset;
            return {{x: x, y: y}};
        }}

        function moveMagnifier(e) {{
            e.preventDefault();
            var pos = getCursorPos(e);
            var x = pos.x;
            var y = pos.y;

            if (x > img.width - (w / zoom))  {{ x = img.width - (w / zoom); }}
            if (x < w / zoom)                {{ x = w / zoom; }}
            if (y > img.height - (h / zoom)) {{ y = img.height - (h / zoom); }}
            if (y < h / zoom)                {{ y = h / zoom; }}

            glass.style.left = (x - w) + "px";
            glass.style.top = (y - h) + "px";
            glass.style.display = "block";
            glass.style.backgroundPosition =
                "-" + ((x * zoom) - w) + "px -" + ((y * zoom) - h) + "px";
        }}

        img.addEventListener("mousemove", moveMagnifier);
        img.addEventListener("mouseleave", function() {{
            glass.style.display = "none";
        }});
    }})();
    </script>
    """

    components.html(html, height=display_h + 10, scrolling=False)


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
        display_magnifier_image(image_file, max_width=1000, zoom=2.5, glass_size=180)
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

            