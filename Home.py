import streamlit as st
import base64
import requests
import json
from datetime import datetime

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
image_path = (r"cartoon.JPG")
# Get the base64 string of the image
image_base64 = image_to_base64(image_path)

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
- **Drug Ionization and pH Effects**: Explore how pH affects drug ionization.
- **Particle Size Distribution in Pharmaceutical Formulations**
- **Pharmacokinetic Modeling**
- **Pharmacodynamics Module**
- **Drug Diffusion and Release Mechanisms**
- **Physical Pharmacy Interactive Module**
- **Drug-Drug Interactions Analysis**
- **Pharmaceutical Excipients Module**
- **Drug Designer Challenge Game**

Choose a module form sidebar to get started!

### How to Use
1. Select a module form sidebar
2. Adjust the parameters using the controls
3. Watch the plots learn and adapt in real-time
4. Experiment with different settings to understand their impact
""")

st.sidebar.success("Select a module above.")

st.markdown("---")

# Function to get and update the visitor count using a cloud database
def track_visitor():
    if 'firebase_option' == True:
        import firebase_admin
        from firebase_admin import credentials, db
        
        # Initialize Firebase (do this only once)
        if 'firebase_initialized' not in st.session_state:
            try:
                cred = credentials.Certificate("your-firebase-credentials.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://your-project.firebaseio.com/'
                })
                st.session_state.firebase_initialized = True
            except Exception as e:
                st.error(f"Error initializing Firebase: {e}")
                return 0
        
        # Increment the counter
        try:
            ref = db.reference('visitor_counter')
            current_count = ref.get() or 0
            new_count = current_count + 1
            ref.set(new_count)
            return new_count
        except Exception as e:
            st.error(f"Error updating counter: {e}")
            return 0
    
    elif 'streamlit_cloud_option' == True:
        if 'count' not in st.session_state:
            # This works only on Streamlit Cloud with secrets management
            try:
                # Get current count
                response = requests.get(
                    "https://kvdb.io/YOUR_BUCKET_ID/visitor_count",
                    headers={"Content-Type": "application/json"}
                )
                current_count = int(response.text) if response.text else 0
                
                # Update count
                new_count = current_count + 1
                requests.post(
                    "https://kvdb.io/YOUR_BUCKET_ID/visitor_count",
                    data=str(new_count),
                    headers={"Content-Type": "text/plain"}
                )
                st.session_state.count = new_count
                return new_count
            except Exception as e:
                st.error(f"Error with KV store: {e}")
                return 0
        return st.session_state.count
    
    else:
        if 'count' not in st.session_state:
            try:
                with open('visitor_count.txt', 'r') as f:
                    current_count = int(f.read().strip())
            except FileNotFoundError:
                current_count = 0
            
            new_count = current_count + 1
            
            try:
                with open('visitor_count.txt', 'w') as f:
                    f.write(str(new_count))
                st.session_state.count = new_count
            except Exception as e:
                st.error(f"Error saving count: {e}")
                st.session_state.count = current_count + 1
                
        return st.session_state.count

# Only increment the counter once per session
if 'visitor_counted' not in st.session_state:
    count = track_visitor()
    st.session_state.visitor_counted = True
else:
    count = st.session_state.get('count', 0)

# Display the counter with nice styling
st.markdown(
    f"""
    <div style="text-align: center; padding: 10px; margin-top: 30px; 
         border-top: 1px solid #f0f0f0; color: #888;">
        <span style="font-size: 14px;">👥 Total Visitors: {count}</span>
    </div>
    """, 
    unsafe_allow_html=True
)

today = datetime.now().strftime("%B %d, %Y")
st.markdown(
    f"""
    <div style="text-align: center; color: #888; font-size: 12px; margin-top: 5px;">
        {today}
    </div>
    """,
    unsafe_allow_html=True
)

