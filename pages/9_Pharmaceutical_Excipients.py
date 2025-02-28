import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
st.set_page_config(layout="wide")


# Excipient database (simplified)
EXCIPIENT_DB = {
    "Fillers": {
        "Lactose Monohydrate": {
            "properties": {
                "moisture": 0.5,
                "particle_size": 100,
                "flow_index": 3.5,
                "compressibility": 4.0
            },
            "compatibility": ["most APIs", "starch", "cellulose"],
            "incompatibility": ["strong oxidizing agents", "amines"],
            "use_range": "20-90%",
            "features": ["water soluble", "good flowability", "compressible"]
        },
        "Microcrystalline Cellulose": {
            "properties": {
                "moisture": 4.0,
                "particle_size": 50,
                "flow_index": 4.0,
                "compressibility": 5.0
            },
            "compatibility": ["most APIs", "lactose", "starch"],
            "incompatibility": ["strong oxidizing agents"],
            "use_range": "20-90%",
            "features": ["highly compressible", "good flowability", "inert"]
        }
    },
    "Binders": {
        "Povidone": {
            "properties": {
                "moisture": 5.0,
                "viscosity": 3.0,
                "adhesion": 4.5,
                "stability": 4.0
            },
            "compatibility": ["most APIs", "cellulose", "starch"],
            "incompatibility": ["oxidizing agents", "some salts"],
            "use_range": "2-10%",
            "features": ["good binding", "soluble", "film forming"]
        },
        "Starch": {
            "properties": {
                "moisture": 10.0,
                "viscosity": 2.5,
                "adhesion": 3.5,
                "stability": 4.5
            },
            "compatibility": ["most APIs", "lactose", "cellulose"],
            "incompatibility": ["strong oxidizing agents"],
            "use_range": "5-20%",
            "features": ["natural", "cheap", "biodegradable"]
        }
    },
    "Disintegrants": {
        "Croscarmellose Sodium": {
            "properties": {
                "swelling": 4.5,
                "moisture": 6.0,
                "efficiency": 5.0,
                "stability": 4.0
            },
            "compatibility": ["most APIs", "fillers"],
            "incompatibility": ["strong acids", "some salts"],
            "use_range": "0.5-5%",
            "features": ["super disintegrant", "rapid action", "efficient"]
        }
    },
    "Lubricants": {
        "Magnesium Stearate": {
            "properties": {
                "lubricity": 5.0,
                "moisture": 0.5,
                "flow_impact": -1.0,
                "stability": 4.5
            },
            "compatibility": ["most excipients"],
            "incompatibility": ["some acids", "oxidizing agents"],
            "use_range": "0.25-1%",
            "features": ["effective", "hydrophobic", "common"]
        }
    }
}

def calculate_compatibility_score(excipient1, excipient2):
    """Calculate compatibility score between two excipients"""
    # Simple scoring system (could be expanded)
    score = 1.0
    if excipient1["incompatibility"] & set(excipient2["compatibility"]):
        score -= 0.5
    if excipient2["incompatibility"] & set(excipient1["compatibility"]):
        score -= 0.5
    return max(0, score)

def plot_material_properties(properties, title):
    """Create radar plot for material properties"""
    categories = list(properties.keys())
    values = list(properties.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True
    )
    
    return fig

def main():
    st.title("Pharmaceutical Excipients Module")
    
    # Navigation
    page = st.radio("Select Topic", [
        "Excipient Database",
        "Compatibility Studies",
        "Material Properties",
        "Selection Guide",
        "Formulation Builder"
    ], horizontal=True)
    
    if page == "Excipient Database":
        st.markdown("""
        ### Excipient Database
        
        Explore different categories of pharmaceutical excipients and their properties.
        """)
        
        category = st.selectbox("Select Excipient Category", list(EXCIPIENT_DB.keys()))
        excipient = st.selectbox("Select Excipient", list(EXCIPIENT_DB[category].keys()))
        
        # Display excipient information
        excipient_data = EXCIPIENT_DB[category][excipient]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Properties")
            for prop, value in excipient_data["properties"].items():
                st.metric(prop.title(), f"{value:.1f}")
        
        with col2:
            st.markdown("#### Features")
            for feature in excipient_data["features"]:
                st.write(f"- {feature}")
        
        # Plot properties
        st.plotly_chart(plot_material_properties(
            excipient_data["properties"],
            f"{excipient} Properties"
        ))
        
    elif page == "Compatibility Studies":
        st.markdown("""
        ### Excipient Compatibility Studies
        
        Analyze compatibility between different excipients.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            category1 = st.selectbox("Select First Category", list(EXCIPIENT_DB.keys()))
            excipient1 = st.selectbox("Select First Excipient", list(EXCIPIENT_DB[category1].keys()))
        
        with col2:
            category2 = st.selectbox("Select Second Category", list(EXCIPIENT_DB.keys()))
            excipient2 = st.selectbox("Select Second Excipient", list(EXCIPIENT_DB[category2].keys()))
        
        # Compare properties
        exc1_data = EXCIPIENT_DB[category1][excipient1]
        exc2_data = EXCIPIENT_DB[category2][excipient2]
        
        fig = go.Figure()
        
        # Add both excipients to radar plot
        for name, data in [(excipient1, exc1_data), (excipient2, exc2_data)]:
            fig.add_trace(go.Scatterpolar(
                r=list(data["properties"].values()),
                theta=list(data["properties"].keys()),
                fill='toself',
                name=name
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True
        )
        
        st.plotly_chart(fig)
        
    elif page == "Material Properties":
        st.markdown("""
        ### Material Properties Analysis
        
        Study physical and chemical properties of excipients.
        """)
        
        property_type = st.selectbox("Select Property Type", 
            ["Flow Properties", "Compression Properties", "Stability"])
        
        if property_type == "Flow Properties":
            # Interactive flow property demonstration
            angle_of_repose = st.slider("Angle of Repose (°)", 25, 45, 30)
            bulk_density = st.slider("Bulk Density (g/cm³)", 0.2, 0.8, 0.5, 0.1)
            
            # Calculate Carr's Index
            tapped_density = bulk_density * (1 + (45-angle_of_repose)/100)
            carrs_index = (tapped_density - bulk_density) / tapped_density * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Carr's Index", f"{carrs_index:.1f}%")
            with col2:
                st.metric("Flow Quality", 
                    "Good" if carrs_index < 15 else "Fair" if carrs_index < 25 else "Poor")
            
    elif page == "Selection Guide":
        st.markdown("""
        ### Excipient Selection Guide
        
        Get recommendations based on formulation requirements.
        """)
        
        # Formulation requirements
        st.subheader("Specify Requirements")
        
        col1, col2 = st.columns(2)
        with col1:
            dosage_form = st.selectbox("Dosage Form", ["Tablet", "Capsule"])
            manufacturing_method = st.selectbox("Manufacturing Method", 
                ["Direct Compression", "Wet Granulation"])
        
        with col2:
            drug_solubility = st.selectbox("API Solubility", 
                ["Highly Soluble", "Poorly Soluble"])
            drug_stability = st.selectbox("API Stability", 
                ["Moisture Sensitive", "Heat Sensitive", "Stable"])
        
        # Generate recommendations
        st.subheader("Recommendations")
        
        # Tablet Recommendations
        if dosage_form == "Tablet":
            if manufacturing_method == "Direct Compression":
                if drug_solubility == "Highly Soluble":
                    if drug_stability == "Moisture Sensitive":
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Microcrystalline Cellulose (low moisture grade) (60-80%)
                        2. Disintegrant: Crospovidone (moisture-resistant) (2-4%)
                        3. Lubricant: Magnesium Stearate (0.5-1%)
                        4. Glidant: Colloidal Silicon Dioxide (0.2%)
                        
                        **Rationale:**
                        - Low moisture content excipients selected
                        - Crospovidone preferred for moisture sensitivity
                        - Minimal hygroscopic components
                        """)
                    elif drug_stability == "Heat Sensitive":
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Lactose Monohydrate (60-80%)
                        2. Disintegrant: Croscarmellose Sodium (2-4%)
                        3. Lubricant: Magnesium Stearate (0.5%)
                        4. Glidant: Colloidal Silicon Dioxide (0.2%)
                        
                        **Rationale:**
                        - Direct compression avoids heat exposure
                        - Standard excipients suitable
                        - Minimal processing required
                        """)
                    else:  # Stable
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Microcrystalline Cellulose (40%) + Lactose (40%)
                        2. Disintegrant: Sodium Starch Glycolate (2-4%)
                        3. Lubricant: Magnesium Stearate (0.5%)
                        4. Glidant: Colloidal Silicon Dioxide (0.2%)
                        
                        **Rationale:**
                        - Optimal filler combination for compressibility
                        - Standard disintegration system
                        - Good flowability and compression
                        """)
                
                else:  # Poorly Soluble
                    if drug_stability == "Moisture Sensitive":
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Microcrystalline Cellulose (silicified) (60-70%)
                        2. Disintegrant: Crospovidone (4-5%)
                        3. Surfactant: Sodium Lauryl Sulfate (0.5-1%)
                        4. Lubricant: Magnesium Stearate (0.5%)
                        
                        **Rationale:**
                        - Surfactant added for solubility enhancement
                        - Moisture-resistant components
                        - Enhanced dissolution properties
                        """)
                    else:  # Heat Sensitive or Stable
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Microcrystalline Cellulose (50%) + Pregelatinized Starch (20%)
                        2. Disintegrant: Croscarmellose Sodium (5%)
                        3. Surfactant: Polysorbate 80 (1%)
                        4. Lubricant: Magnesium Stearate (0.5%)
                        
                        **Rationale:**
                        - Dissolution enhancing components
                        - Good disintegration properties
                        - Enhanced wettability
                        """)
            
            else:  # Wet Granulation
                if drug_solubility == "Highly Soluble":
                    if drug_stability == "Moisture Sensitive":
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Microcrystalline Cellulose (50%) + DCP (20%)
                        2. Binder: Povidone K30 (3-5%) - added in solvent
                        3. Disintegrant: Crospovidone (intragranular 2%, extragranular 2%)
                        4. Lubricant: Magnesium Stearate (1%)
                        
                        **Processing Note:**
                        - Use ethanol as granulation fluid
                        - Minimize granulation liquid
                        - Control drying conditions
                        """)
                    else:  # Heat Sensitive or Stable
                        st.write("""
                        **Recommended Excipients:**
                        1. Filler: Lactose Monohydrate (60%)
                        2. Binder: HPMC (4-6%)
                        3. Disintegrant: Croscarmellose Sodium (intragranular 2%, extragranular 2%)
                        4. Lubricant: Magnesium Stearate (1%)
                        
                        **Processing Note:**
                        - Aqueous granulation
                        - Standard processing conditions
                        - Optimize drying temperature
                        """)
        
        # Capsule Recommendations
        else:  # Capsule
            if drug_solubility == "Highly Soluble":
                if drug_stability == "Moisture Sensitive":
                    st.write("""
                    **Recommended Excipients:**
                    1. Filler: Microcrystalline Cellulose (70-85%)
                    2. Glidant: Colloidal Silicon Dioxide (0.5%)
                    3. Lubricant: Magnesium Stearate (0.5%)
                    
                    **Rationale:**
                    - Minimal excipients needed
                    - Low moisture content
                    - Good flow properties
                    """)
                else:  # Heat Sensitive or Stable
                    st.write("""
                    **Recommended Excipients:**
                    1. Filler: Lactose Monohydrate (70-85%)
                    2. Glidant: Colloidal Silicon Dioxide (0.5%)
                    3. Lubricant: Magnesium Stearate (0.5%)
                    
                    **Rationale:**
                    - Simple formulation
                    - Cost-effective
                    - Good flowability
                    """)
            
            else:  # Poorly Soluble
                if drug_stability == "Moisture Sensitive":
                    st.write("""
                    **Recommended Excipients:**
                    1. Filler: Microcrystalline Cellulose (60%)
                    2. Surfactant: Sodium Lauryl Sulfate (1-2%)
                    3. Disintegrant: Crospovidone (5%)
                    4. Glidant: Colloidal Silicon Dioxide (0.5%)
                    5. Lubricant: Magnesium Stearate (0.5%)
                    
                    **Rationale:**
                    - Solubility enhancement
                    - Moisture protection
                    - Quick dissolution
                    """)
                else:  # Heat Sensitive or Stable
                    st.write("""
                    **Recommended Excipients:**
                    1. Filler: Microcrystalline Cellulose (50%) + Lactose (20%)
                    2. Surfactant: Polysorbate 80 (1%)
                    3. Disintegrant: Croscarmellose Sodium (5%)
                    4. Glidant: Colloidal Silicon Dioxide (0.5%)
                    5. Lubricant: Magnesium Stearate (0.5%)
                    
                    **Rationale:**
                    - Balanced formulation
                    - Enhanced dissolution
                    - Good processability
                    """)
        
        # Add excipient property details
        st.subheader("Additional Considerations")
        st.info("""
        **Key Factors in Selection:**
        1. Processing conditions and their impact on stability
        2. Excipient moisture content and hygroscopicity
        3. Particle size compatibility
        4. Cost considerations
        5. Regulatory status of excipients
        """)
        
    elif page == "Formulation Builder":
        st.markdown("""
        ### Interactive Formulation Builder
        
        Build your formulation and analyze its properties.
        """)
        
        # Basic formulation setup
        tablet_weight = st.number_input("Target Tablet Weight (mg)", 100, 1000, 200)
        drug_load = st.number_input("API Content (mg)", 10, 500, 50)
        
        # Available space for excipients
        available_weight = tablet_weight - drug_load
        
        st.write(f"Available weight for excipients: {available_weight} mg")
        
        # Add excipients
        excipients = {}
        
        col1, col2 = st.columns(2)
        with col1:
            # Filler
            filler = st.selectbox("Select Filler", ["Lactose Monohydrate", "MCC"])
            filler_percent = st.slider("Filler Percentage", 0, 100, 70)
            excipients[filler] = filler_percent
            
            # Disintegrant
            disintegrant = st.selectbox("Select Disintegrant", ["Croscarmellose Sodium"])
            disintegrant_percent = st.slider("Disintegrant Percentage", 0, 10, 3)
            excipients[disintegrant] = disintegrant_percent
        
        with col2:
            # Binder
            binder = st.selectbox("Select Binder", ["Povidone", "Starch"])
            binder_percent = st.slider("Binder Percentage", 0, 20, 5)
            excipients[binder] = binder_percent
            
            # Lubricant
            lubricant = st.selectbox("Select Lubricant", ["Magnesium Stearate"])
            lubricant_percent = st.slider("Lubricant Percentage", 0, 5, 1)
            excipients[lubricant] = lubricant_percent
        
        # Calculate and display formulation
        total_percent = sum(excipients.values())
        
        if total_percent != 100:
            st.warning(f"Total percentage: {total_percent}% (should be 100%)")
        else:
            st.success("Valid formulation!")
            
            # Display formulation table
            data = {
                "Component": ["API"] + list(excipients.keys()),
                "Percentage": [drug_load/tablet_weight*100] + list(excipients.values()),
                "Weight (mg)": [drug_load] + [available_weight * p/100 for p in excipients.values()]
            }
            
            df = pd.DataFrame(data)
            st.table(df)

if __name__ == "__main__":
    main()