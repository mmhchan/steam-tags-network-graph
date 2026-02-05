import streamlit as st
import pandas as pd
from pyvis.network import Network
from itertools import combinations
import streamlit.components.v1 as components

# --- CONFIGURATION & STATE ---
DEFAULTS = {
    "bg_col": "#FFFFFF",
    "lbl_col": "#000000",
    "tag_col": "#4A90E2",
    "brg_col": "#FFD166",
    "lbl_sz": 14,
    "node_sz": 10,
    "edg_op": 0.2,
    "node_dist": 100,
    "spread": -50
}

def reset_params():
    for key, val in DEFAULTS.items():
        st.session_state[key] = val

# Initialize session state with default config
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- UI DEFINITIONS ---
graph_settings = [
    {"label": "Background", "type": "color", "key": "bg_col", "cat": "Visuals", "help": "Overall canvas color."},
    {"label": "Label Color", "type": "color", "key": "lbl_col", "cat": "Visuals", "help": "Color of the text labels. Ensure this contrasts well with the background."},
    {"label": "Unique Tag", "type": "color", "key": "tag_col", "cat": "Visuals", "help": "Color for tags that appear in only one game."},
    {"label": "Shared Tag", "type": "color", "key": "brg_col", "cat": "Visuals", "help": "Color for tags that connect multiple games together."},
    {"label": "Label Size", "type": "slider", "key": "lbl_sz", "min": 5, "max": 50, "cat": "Visuals", "help": "Text size."},
    {"label": "Node Size", "type": "slider", "key": "node_sz", "min": 5, "max": 50, "cat": "Visuals", "help": "Adjust the size of all nodes."},
    {"label": "Edge Opacity", "type": "slider", "key": "edg_op", "min": 0.0, "max": 1.0, "cat": "Visuals", "help": "Transparency of connections."},
    {"label": "Node Spacing", "type": "slider", "key": "node_dist", "min": 50, "max": 500, "cat": "Physics", "help": "Increases the distance between connected tags."},
    {"label": "Expansion", "type": "slider", "key": "spread", "min": -200, "max": -10, "cat": "Physics", "help": "How strongly nodes repel each other. More negative = more spread out."}
]

# --- APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Steam Tag Network Graph Builder | by Michael Chan", page_icon="🎮")
st.title("Steam Tag Network Graph Builder")
st.sidebar.header("Data")
st.sidebar.markdown("Upload your CSV with columns: **Game, Tag 1, Tag 2, Tag 3, Tag 4, Tag 5**")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

st.sidebar.header("Settings")
exp_vis = st.sidebar.expander("Visual Styles", expanded=True)
exp_phy = st.sidebar.expander("Physics & Layout", expanded=False)

# Dynamic widget generation
for setting in graph_settings:
    target = exp_vis if setting["cat"] == "Visuals" else exp_phy    
    with target:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(setting['label'], help=setting.get("help"))
        with col2:
            if setting["type"] == "color":
                st.color_picker(setting["label"], label_visibility="collapsed", key=setting["key"])
            elif setting["type"] == "number":
                st.number_input(setting["label"], min_value=setting["min"], max_value=setting["max"], label_visibility="collapsed", key=setting["key"])
            elif setting["type"] == "slider":
                st.slider(setting["label"], min_value=setting["min"], max_value=setting["max"], label_visibility="collapsed", key=setting["key"])

st.sidebar.button("Restore Defaults", on_click=reset_params)
st.sidebar.warning("⚠️ Changing settings will refresh the layout.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center;'>
        <p style='font-size: 0.8em;'>Built by <strong>Michael Chan</strong></p>
        <a href='https://linkedin.com/in/mmhchan' style='text-decoration: none; margin-right: 10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/174/174857.png' width='20'>
        </a>
        <a href='https://github.com/mmhchan' style='text-decoration: none;'>
            <img src='https://cdn-icons-png.flaticon.com/512/25/25231.png' width='20'>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# --- CORE LOGIC ---
def draw_graph(df, params):
    """Generates and renders a Pyvis network based on dataframe input."""
    net = Network(height="950px", width="100%", bgcolor=params["bg_col"], font_color=params["lbl_col"])
    
    # Configure global physics and node styles
    net.set_options(f"""
    {{
        "nodes": {{
            "size": {int(params["node_sz"])},
            "font": {{
                "size": {int(params["lbl_sz"])},
                "color": "{params["lbl_col"]}"
            }}
        }},
        "physics": {{
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {{
                "gravitationalConstant": {params["spread"]},
                "centralGravity": 0.01,
                "springLength": {params["node_dist"]},
                "springStrength": 0.08,
                "damping": 0.6,
                "avoidOverlap": 0.5
            }},
            "maxVelocity": 50,
            "minVelocity": 0.75,
            "stabilization": {{
                "enabled": true,
                "iterations": 1000,
                "updateInterval": 25
            }}
        }}
    }}
    """)

    # Parse CSV data
    game_dict = {}
    tag_columns = [f'Tag {i}' for i in range(1, 6)]
    all_tag_counts = {}

    for _, row in df.iterrows():
        game_name = str(row['Game'])
        tags = [str(row[col]).strip() for col in tag_columns if col in df.columns and pd.notna(row[col]) and str(row[col]).strip() != ""]
        if tags:
            game_dict[str(row['Game'])] = tags
            for t in tags:
                all_tag_counts[t] = all_tag_counts.get(t, 0) + 1

    # Generate Nodes
    for tag, count in all_tag_counts.items():
        node_color = params["brg_col"] if count > 1 else params["tag_col"]      
        net.add_node(tag, label=tag, color=node_color, shape="dot")

    # Generate Edges
    dynamic_edge_color = f"rgba(100, 100, 100, {params['edg_op']})"
    for game, tags in game_dict.items():
        for t1, t2 in combinations(tags, 2):
            net.add_edge(
                t1, 
                t2, 
                color=dynamic_edge_color, 
                width=1
            )
          
    # HTML, CSS, and JS injection for UI customization and high-res export
    html_injection = """
    <style>
        /* Stylize the Pyvis physics configuration panel */
        .vis-configuration-wrapper {
            position: absolute !important; top: 10px !important; right: 10px !important;
            width: 550px !important; max-height: 80vh !important; overflow-y: auto !important;
            background: #ffffff !important; padding: 10px !important; border-radius: 8px !important;
            border: 2px solid #444444 !important; z-index: 2000 !important; display: block !important;
        }
        .vis-configuration-wrapper * { color: #000000 !important; font-family: sans-serif !important; }
        
        /* Stylize the custom export button */
        #high-res-btn {
            position: absolute; top: 15px; left: 15px; z-index: 3000;
            padding: 10px 15px; background-color: #2ECC71; color: white;
            border: none; border-radius: 5px; cursor: pointer; font-family: sans-serif;
            font-weight: bold; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        }
        #high-res-btn:hover { background-color: #27AE60; }
    </style>

    <button id="high-res-btn">📸 Save 3x High-Res PNG</button>

    <script>
    document.getElementById('high-res-btn').onclick = function() {
        const container = document.getElementById('mynetwork');
        const canvas = container.getElementsByTagName('canvas')[0];
        const scale = 3; 

        // Cache original dimensions for restoration
        const originalWidth = container.style.width;
        const originalHeight = container.style.height;

        // Upscale container to trigger high-density vector re-rendering
        container.style.width = (canvas.width * scale) + "px";
        container.style.height = (canvas.height * scale) + "px";

        // Delay execution to allow the browser graphics engine to redraw the canvas
        setTimeout(() => {
            const link = document.createElement('a');
            link.download = 'steam-tag-network-crisp.png';
            link.href = canvas.toDataURL("image/png", 1.0);
            link.click();

            // Restore original UI dimensions
            container.style.width = originalWidth;
            container.style.height = originalHeight;
        }, 500); 
    };
    </script>
    """

    # Inject assets into the generated HTML and render the component
    html_content = net.generate_html().replace('</head>', f'{html_injection}</head>')
    components.html(html_content, height=1000, scrolling=False)

# --- EXECUTION ---
df = None

if uploaded_file:
    try:
        # Load user-provided data
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip() # Clean headers

        # Validate required schema
        if 'Game' not in df.columns or 'Tag 1' not in df.columns:
            st.error("CSV must contain 'Game' and 'Tag 1' columns.")
            df = None
    except Exception as e:
        st.error(f"Error parsing uploaded file: {e}")
        df = None
else:
    # Load demonstration dataset if no file is provided
    st.info("Upload a CSV to visualize custom data. Displaying sample dataset:")
    sample_data = [
        ["Heroes Of Might And Magic: Olden Era", "Strategy", "Simulation", "Turn-Based Strategy", "Tactical", "Grand Strategy"],
        ["Half Sword", "Physics", "Gore", "Combat", "Medieval", "Swordplay"],
        ["The Cube, Save Us", "Massively Multiplayer", "Extraction Shooter", "Multiplayer", "Action", "Loot"],
        ["The Midnight Walkers", "Early Access", "Action", "Extraction Shooter", "Indie", "Zombies"],
        ["Everwind", "Early Access", "RPG", "Pixel Graphics", "Survival", "Co-op"],
        ["Reanimal", "Horror", "Adventure", "Atmospheric", "Co-op", "3D"],
        ["Yapyap", "Online Co-Op", "Magic", "Comedy", "Horror", "Physics"],
        ["Car Service Together", "Racing", "Simulation", "Casual", "Automobile Sim", "FPS"],
        ["Final Sentence", "Typing", "Simulation", "Horror", "Survival", "Battle Royale"],
        ["Crashout Crew", "Driving", "Casual", "Arcade", "Character Customization", "3D"]
    ]
    
    # Convert list to DataFrame with standard headers
    df = pd.DataFrame(sample_data, columns=['Game', 'Tag 1', 'Tag 2', 'Tag 3', 'Tag 4', 'Tag 5'])

# Execute graph generation if dataframe is valid
if df is not None:
    draw_graph(df, st.session_state)