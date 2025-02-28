import streamlit as st
import base64

st.set_page_config(
    page_title="BioPharamcy Platform",
    page_icon="💊",
    layout="wide"
)

# Convert the image to a base64 string
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Load your image from a local path
image_path = (r"C:\Users\mas082\OneDrive - UiT Office 365\Desktop\Introduce_Your_Self\cartoon.JPG")
# Get the base64 string of the image
image_base64 = image_to_base64(image_path)

# Display your image and name in the top right corner
st.markdown(
    f"""
    <style>
    .header {{
        position: absolute;  /* Fix the position */
        top: -60px;  /* Adjust as needed */
        right: -40px;  /* Align to the right */
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 10px;
        flex-direction: column; /* Stack items vertically */
        text-align: center; /* Ensures text is centrally aligned */
    }}
    .header img {{
        border-radius: 50%;
        width: 50px;
        height: 50px;
        margin-bottom: 5px; /* Space between image and text */
    }}
    .header-text {{
        font-size: 12px;
        font-weight: normal; /* Regular weight for text */
        text-align: center;
    }}
    </style>
    <div class="header">
        <img src="data:image/jpeg;base64,{image_base64}" alt="Mohsen Askar">
        <div class="header-text">Developed by: Mohsen Askar</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("BioPharamcy Platform 💊")
st.markdown("""
Welcome to the BioPharamcy Platform!

This application helps you understand how different machine learning algorithms work in real-time.

### Available modules visualizations:
- **Drug Dissolution Profile Simulator**: Explore how different parameters affect drug dissolution kinetics.

Choose a module form sidebar to get started!

### How to Use
1. Select a module form sidebar
2. Adjust the parameters using the controls
3. Watch the plots learn and adapt in real-time
4. Experiment with different settings to understand their impact
""")

# Display some sample visualizations or key metrics on the home page
st.sidebar.success("Select a module above.")