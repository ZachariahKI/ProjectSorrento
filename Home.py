import streamlit as st

# --- Page Configuration (Set this first) ---
st.set_page_config(layout="wide")

# --- Main Title ---
st.markdown("<h1 style='text-align: center;'>BSM</h1>", unsafe_allow_html=True)

# Add some vertical space below the title
st.write("")
st.write("")

# --- Create the 4 clickable boxes/sections ---
box_labels = {
    "box1": "Distribution",
    "box2": "Portfolio Management",
    "box3": "Forecasting",
    "box4": "Post Deal"
}
# Define the target page files (relative path from the main script)
page_paths = {
    "box1": "pages/01_Distribution.py",
    "box2": "pages/02_Portfolio_Management.py",
    "box3": "pages/03_Forecasting.py",
    "box4": "pages/04_Post_Deal.py"
}

# --- Row 1 ---
col1, col2 = st.columns(2) # Create two equal-width columns

with col1:
    clicked_box1 = st.button(label=f"Explore {box_labels['box1']}", key="box1_button", use_container_width=True)
    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{box_labels['box1']}</p>", unsafe_allow_html=True)
    # Add navigation logic
    if clicked_box1:
        st.switch_page(page_paths["box1"])

with col2:
    clicked_box2 = st.button(label=f"Explore {box_labels['box2']}", key="box2_button", use_container_width=True)
    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{box_labels['box2']}</p>", unsafe_allow_html=True)
    # Add navigation logic
    if clicked_box2:
        st.switch_page(page_paths["box2"])


# Add some vertical space between the rows
st.write("")
st.write("")


# --- Row 2 ---
col3, col4 = st.columns(2) # Create two more equal-width columns

with col3:
    clicked_box3 = st.button(label=f"Explore {box_labels['box3']}", key="box3_button", use_container_width=True)
    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{box_labels['box3']}</p>", unsafe_allow_html=True)
    # Add navigation logic
    if clicked_box3:
        st.switch_page(page_paths["box3"])

with col4:
    clicked_box4 = st.button(label=f"Explore {box_labels['box4']}", key="box4_button", use_container_width=True)
    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{box_labels['box4']}</p>", unsafe_allow_html=True)
    # Add navigation logic
    if clicked_box4:
        st.switch_page(page_paths["box4"])


# --- Optional: CSS Styling ---
# (Keep the st.markdown CSS block here if you were using it)
st.markdown("""
<style>
    button[data-testid="stButton"] {
        height: 150px;
        padding: 10px 0px;
        margin-bottom: 5px;
        border: 1px solid #cccccc;
        border-radius: 5px;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Info ---
st.sidebar.header("Dashboard Sections")
st.sidebar.info("Select a section from the list above or click one of the 'Explore...' buttons.")