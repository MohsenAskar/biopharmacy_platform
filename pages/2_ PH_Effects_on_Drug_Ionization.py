import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
st.set_page_config(layout="wide")

def calculate_ionization(pH, pKa, is_acid=True):
    """Calculate the fraction of ionized and unionized species"""
    if is_acid:
        fraction_ionized = 1 / (1 + 10**(pKa - pH))
    else:
        fraction_ionized = 1 / (1 + 10**(pH - pKa))
    return fraction_ionized

def generate_ionization_plot(pKa, is_acid=True, highlight_points=None):
    """Generate ionization profile plot with optional highlighted points"""
    pH_range = np.linspace(0, 14, 100)
    ionized = [calculate_ionization(pH, pKa, is_acid) * 100 for pH in pH_range]
    unionized = [100 - ion for ion in ionized]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=pH_range, y=ionized, name='Ionized', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=pH_range, y=unionized, name='Unionized', line=dict(color='red')))
    
    # Add highlight points if provided
    if highlight_points:
        for point in highlight_points:
            ionized_value = calculate_ionization(point['pH'], pKa, is_acid) * 100
            fig.add_trace(go.Scatter(
                x=[point['pH']], 
                y=[ionized_value],
                mode='markers+text',
                name=point['name'],
                text=[f"{point['name']}<br>{ionized_value:.1f}% ionized"],
                textposition="top center",
                marker=dict(size=10, color='green'),
                showlegend=False
            ))
    
    fig.update_layout(
        title=f"{'Acid' if is_acid else 'Base'} Ionization Profile (pKa = {pKa})",
        xaxis_title="pH",
        yaxis_title="Percentage (%)",
        hovermode='x unified'
    )
    
    return fig

def main():
    st.title("Drug Ionization and pH Effects")
    
    # Main navigation
    page = st.radio("Select Topic", 
        ["Interactive Calculator", "Drug Case Studies", "Quiz"], horizontal=True)
    
    if page == "Interactive Calculator":
        st.markdown("""
        ### Understanding Drug Ionization
        
        The Henderson-Hasselbalch equation helps us understand how drugs ionize at different pH values:
        
        $pH = pKa + log_{10}\\frac{[A^-]}{[HA]}$ (for acids)
        
        This interactive calculator helps visualize how pH affects drug ionization.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            drug_type = st.radio("Drug Type", ["Acid", "Base"])
        with col2:
            pKa = st.slider("Drug pKa", 1.0, 14.0, 7.0, 0.1)
        
        ph = st.slider("Solution pH", 0.0, 14.0, 7.0, 0.1)
        
        is_acid = drug_type == "Acid"
        ionized_fraction = calculate_ionization(ph, pKa, is_acid)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ionized (%)", f"{ionized_fraction*100:.1f}")
        with col2:
            st.metric("Unionized (%)", f"{(1-ionized_fraction)*100:.1f}")
        
        st.plotly_chart(generate_ionization_plot(pKa, is_acid))
        
        st.markdown("""
        ### Key Points:
        - Unionized forms typically cross membranes more easily
        - The pH where ionized = unionized is equal to the pKa
        - Physiological pH varies throughout the body (stomach: 1-3, intestine: 6-8, blood: 7.4)
        """)

    elif page == "Drug Case Studies":
        drug = st.selectbox("Select Drug Case Study", 
            ["Aspirin (pKa 3.5)", "Morphine (pKa 8.0)", "Lidocaine (pKa 7.9)"])
        
        if drug == "Aspirin (pKa 3.5)":
            st.markdown("""
            ### Aspirin (Acetylsalicylic Acid)
            
            Aspirin is a weak acid with pKa = 3.5. Its absorption is highly dependent on pH:
            """)
            
            # Create highlight points for physiological compartments
            highlight_points = [
                {'pH': 2.0, 'name': 'Stomach'},
                {'pH': 6.8, 'name': 'Intestine'},
                {'pH': 7.4, 'name': 'Blood'}
            ]
            
            st.plotly_chart(generate_ionization_plot(3.5, True, highlight_points))
            
            st.markdown("""
            **Clinical Implications:**
            - In stomach (pH 2.0): Mostly unionized → Rapid absorption
            - In intestine (pH 6.8): Mostly ionized → Slower absorption
            - In blood (pH 7.4): Highly ionized → Stays in circulation
            """)

        elif drug == "Morphine (pKa 8.0)":
            st.markdown("""
            ### Morphine
            
            Morphine is a weak base with pKa = 8.0. Its distribution is affected by pH differences:
            """)
            
            highlight_points = [
                {'pH': 7.4, 'name': 'Blood'},
                {'pH': 7.0, 'name': 'Tissue'},
                {'pH': 6.5, 'name': 'Inflamed Tissue'}
            ]
            
            st.plotly_chart(generate_ionization_plot(8.0, False, highlight_points))
            
            st.markdown("""
            **Clinical Implications:**
            - In blood (pH 7.4): Mix of ionized/unionized forms
            - In inflamed tissue (pH 6.5): More ionized → Ion trapping
            - Enhanced effect in acidic environments
            """)

        elif drug == "Lidocaine (pKa 7.9)":
            st.markdown("""
            ### Lidocaine
            
            Lidocaine is a local anesthetic with pKa = 7.9. Its activity is pH-dependent:
            """)
            
            highlight_points = [
                {'pH': 7.4, 'name': 'Normal Tissue'},
                {'pH': 6.5, 'name': 'Infected Tissue'}
            ]
            
            st.plotly_chart(generate_ionization_plot(7.9, False, highlight_points))
            
            st.markdown("""
            **Clinical Implications:**
            - Less effective in infected (acidic) tissues
            - Adding bicarbonate can improve onset of action
            - pH affects both distribution and activity
            """)

    elif page == "Quiz":
        st.header("Test Your Understanding")
        
        # Question 1
        st.subheader("Question 1")
        quiz_answer_1 = st.radio(
            "Which statement about drug ionization is correct?",
            (
                "Ionized forms of drugs generally cross membranes more easily than unionized forms",
                "Unionized forms of drugs generally cross membranes more easily than ionized forms"
            )
        )
        
        if quiz_answer_1 == "Unionized forms of drugs generally cross membranes more easily than ionized forms":
            st.success("Correct! Unionized forms are typically more lipophilic and cross membranes more easily.")
        else:
            st.error("Not quite. Unionized forms are typically more lipophilic and cross membranes more easily.")
        
        # Question 2
        st.subheader("Question 2")
        quiz_answer_2 = st.radio(
            "At what pH relative to a drug's pKa is the drug 50% ionized?",
            (
                "When pH equals pKa",
                "When pH is one unit above pKa",
                "When pH is one unit below pKa"
            )
        )
        
        if quiz_answer_2 == "When pH equals pKa":
            st.success("Correct! At pH = pKa, the drug is exactly 50% ionized.")
        else:
            st.error("Not quite. When pH equals pKa, the concentrations of ionized and unionized forms are equal (50% each).")

if __name__ == "__main__":
    main()