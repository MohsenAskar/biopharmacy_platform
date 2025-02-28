import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

def calculate_receptor_binding(drug_conc, kd):
    """Calculate receptor occupancy using binding equation"""
    return (drug_conc / (drug_conc + kd)) * 100

def hill_equation(concentration, ec50, hill_coefficient):
    """Calculate effect using Hill equation"""
    return (concentration**hill_coefficient) / (ec50**hill_coefficient + concentration**hill_coefficient) * 100

def competitive_antagonism(agonist_conc, antagonist_conc, ka_agonist, ka_antagonist):
    """Calculate effect with competitive antagonist present"""
    return (agonist_conc/ka_agonist) / (1 + agonist_conc/ka_agonist + antagonist_conc/ka_antagonist) * 100

def calculate_therapeutic_window(min_effective_conc, toxic_conc, dose_range):
    """Calculate therapeutic effect within concentration window"""
    effect = np.zeros_like(dose_range)
    for i, dose in enumerate(dose_range):
        if dose < min_effective_conc:
            effect[i] = 0
        elif dose > toxic_conc:
            effect[i] = 100  # Toxic effect
        else:
            effect[i] = ((dose - min_effective_conc) / (toxic_conc - min_effective_conc)) * 80  # Therapeutic effect
    return effect

def main():
    st.title("Pharmacodynamics Interactive Module")
    
    page = st.radio("Select Topic", 
        ["Receptor Binding", "Dose-Response", "Drug Interactions", "Case Studies"], 
        horizontal=True)
    
    if page == "Receptor Binding":
        st.markdown("""
        ### Drug-Receptor Binding
        
        The binding of a drug to its receptor follows the law of mass action:
        
        $Binding\\ (\%) = \\frac{[Drug]}{[Drug] + K_d} \\times 100$
        
        where:
        - [Drug] = drug concentration
        - Kd = dissociation constant
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            kd = st.slider("Dissociation Constant (Kd)", 0.1, 10.0, 1.0, 0.1)
            max_conc = st.slider("Maximum Drug Concentration", 1, 100, 50)
        
        # Generate concentration range
        conc_range = np.logspace(-2, np.log10(max_conc), 100)
        binding = calculate_receptor_binding(conc_range, kd)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=conc_range, 
            y=binding,
            name="Receptor Occupancy"
        ))
        
        fig.update_layout(
            title="Drug-Receptor Binding Curve",
            xaxis_title="Drug Concentration",
            yaxis_title="Receptor Occupancy (%)",
            xaxis_type="log"
        )
        
        st.plotly_chart(fig)
        
        # Show key points
        st.markdown(f"""
        **Key Points:**
        - 50% binding occurs at Kd = {kd}
        - At 10×Kd: {calculate_receptor_binding(10*kd, kd):.1f}% bound
        - At 0.1×Kd: {calculate_receptor_binding(0.1*kd, kd):.1f}% bound
        """)
        
    elif page == "Dose-Response":
        st.markdown("""
        ### Dose-Response Relationships
        
        The relationship between drug concentration and effect is often described by the Hill equation:
        
        $Effect\\ (\%) = \\frac{[Drug]^n}{EC_{50}^n + [Drug]^n} \\times 100$
        
        where:
        - EC50 = concentration producing 50% effect
        - n = Hill coefficient (steepness)
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            ec50 = st.slider("EC50", 0.1, 10.0, 1.0, 0.1)
            hill_coef = st.slider("Hill Coefficient", 0.5, 4.0, 1.0, 0.1)
        
        conc_range = np.logspace(-2, 2, 100)
        effect = hill_equation(conc_range, ec50, hill_coef)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=conc_range,
            y=effect,
            name="Effect"
        ))
        
        fig.update_layout(
            title="Dose-Response Curve",
            xaxis_title="Drug Concentration",
            yaxis_title="Effect (%)",
            xaxis_type="log"
        )
        
        st.plotly_chart(fig)
        
    elif page == "Drug Interactions":
        st.markdown("""
        ### Drug Interactions and Antagonism
        
        Study competitive and non-competitive antagonism:
        """)
        
        interaction_type = st.selectbox(
            "Select Interaction Type",
            ["Competitive Antagonism", "Therapeutic Window", "Synergism"]
        )
        
        if interaction_type == "Competitive Antagonism":
            col1, col2 = st.columns(2)
            with col1:
                ka_agonist = st.slider("Agonist Affinity (Ka)", 0.1, 10.0, 1.0, 0.1)
                antagonist_conc = st.slider("Antagonist Concentration", 0.0, 10.0, 0.0, 0.1)
            with col2:
                ka_antagonist = st.slider("Antagonist Affinity", 0.1, 10.0, 2.0, 0.1)
            
            agonist_range = np.logspace(-2, 2, 100)
            effect = competitive_antagonism(agonist_range, antagonist_conc, ka_agonist, ka_antagonist)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=agonist_range,
                y=effect,
                name="Effect"
            ))
            
            fig.update_layout(
                title="Competitive Antagonism",
                xaxis_title="Agonist Concentration",
                yaxis_title="Effect (%)",
                xaxis_type="log"
            )
            
            st.plotly_chart(fig)
            
        elif interaction_type == "Therapeutic Window":
            col1, col2 = st.columns(2)
            with col1:
                min_effective = st.slider("Minimum Effective Concentration", 1, 50, 10)
                toxic_conc = st.slider("Toxic Concentration", 51, 200, 100)
            
            dose_range = np.linspace(0, 200, 100)
            effect = calculate_therapeutic_window(min_effective, toxic_conc, dose_range)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dose_range,
                y=effect,
                name="Effect"
            ))
            
            # Add therapeutic window visualization
            fig.add_vrect(
                x0=min_effective,
                x1=toxic_conc,
                fillcolor="green",
                opacity=0.2,
                layer="below",
                line_width=0,
                annotation_text="Therapeutic Window",
                annotation_position="top left"
            )
            
            fig.update_layout(
                title="Therapeutic Window",
                xaxis_title="Drug Concentration",
                yaxis_title="Effect (%)"
            )
            
            st.plotly_chart(fig)
            
    elif page == "Case Studies":
        case = st.selectbox("Select Case Study",
            ["Beta Blockers", "Local Anesthetics", "Anticoagulants"])
        
        if case == "Beta Blockers":
            st.markdown("""
            ### Beta Blocker Pharmacodynamics
            
            Study the relationship between β-blocker concentration and heart rate reduction.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                baseline_hr = st.slider("Baseline Heart Rate", 60, 120, 80)
                drug_potency = st.slider("Drug Potency (IC50)", 0.1, 10.0, 1.0, 0.1)
            
            conc_range = np.logspace(-2, 2, 100)
            effect = hill_equation(conc_range, drug_potency, 1.0)
            heart_rate = baseline_hr - (baseline_hr - 60) * effect/100
            
            fig = make_subplots(rows=1, cols=2,
                              subplot_titles=("Drug Effect", "Heart Rate"))
            
            fig.add_trace(
                go.Scatter(x=conc_range, y=effect, name="% Effect"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=conc_range, y=heart_rate, name="Heart Rate"),
                row=1, col=2
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig)
            
        elif case == "Local Anesthetics":
            st.markdown("""
            ### Local Anesthetic Pharmacodynamics
            
            Explore the relationship between pH, ionization, and anesthetic effect.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                drug_pka = st.slider("Drug pKa", 7.0, 9.0, 7.9, 0.1)
                tissue_ph = st.slider("Tissue pH", 6.0, 7.5, 7.4, 0.1)
            
            # Calculate ionization and effect
            ph_range = np.linspace(6, 8, 100)
            ionized = 1 / (1 + 10**(ph_range - drug_pka))
            effect = 100 * (1 - ionized)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ph_range, y=effect, name="Anesthetic Effect"))
            
            # Add current pH point
            current_effect = 100 * (1 - 1/(1 + 10**(tissue_ph - drug_pka)))
            fig.add_trace(go.Scatter(
                x=[tissue_ph],
                y=[current_effect],
                mode='markers',
                name='Current pH',
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title="pH Effect on Local Anesthetic Activity",
                xaxis_title="pH",
                yaxis_title="Relative Effect (%)"
            )
            
            st.plotly_chart(fig)
            
        elif case == "Anticoagulants":
            st.markdown("""
            ### Anticoagulant Pharmacodynamics
            
            Study the relationship between anticoagulant concentration and clotting time.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                baseline_inr = st.slider("Baseline INR", 0.8, 1.2, 1.0, 0.1)
                target_inr = st.slider("Target INR Range", 2.0, 4.0, 2.5, 0.1)
            
            # Calculate INR effect
            conc_range = np.linspace(0, 10, 100)
            inr = baseline_inr + hill_equation(conc_range, 2, 1.5) * (target_inr - baseline_inr)/100
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=conc_range, y=inr, name="INR"))
            
            # Add therapeutic range
            fig.add_hrect(
                y0=2.0,
                y1=3.0,
                fillcolor="green",
                opacity=0.2,
                layer="below",
                line_width=0,
                annotation_text="Therapeutic Range",
                annotation_position="right"
            )
            
            fig.update_layout(
                title="Anticoagulant Effect on INR",
                xaxis_title="Drug Concentration",
                yaxis_title="INR"
            )
            
            st.plotly_chart(fig)
                # Add explanatory text
            st.markdown("""
            **Clinical Interpretation:**
            - Therapeutic INR range: 2.0-3.0
            - Below 2.0: Insufficient anticoagulation
            - Above 3.0: Increased bleeding risk
            """)
            

if __name__ == "__main__":
    main()