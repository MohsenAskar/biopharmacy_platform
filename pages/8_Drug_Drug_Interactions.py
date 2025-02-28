import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

def calculate_metabolic_inhibition(time, drug_conc, inhibitor_conc, ki):
    """Calculate drug concentration with metabolic inhibition"""
    baseline_clearance = 0.1
    inhibited_clearance = baseline_clearance / (1 + inhibitor_conc/ki)
    return drug_conc * np.exp(-inhibited_clearance * time)

def calculate_enzyme_induction(time, drug_conc, inducer_effect):
    """Calculate drug concentration with enzyme induction"""
    baseline_clearance = 0.1
    induced_clearance = baseline_clearance * (1 + inducer_effect)
    return drug_conc * np.exp(-induced_clearance * time)

def calculate_synergy_effect(drug1_effect, drug2_effect, interaction_factor):
    """Calculate combined drug effect with interaction"""
    return drug1_effect + drug2_effect + (interaction_factor * drug1_effect * drug2_effect)

def main():
    st.title("Drug-Drug Interactions Analysis")
    
    # Navigation
    topic = st.radio("Select Topic", [
        "Metabolic Interactions",
        "Pharmacokinetic Interactions",
        "Pharmacodynamic Interactions",
        "Risk Assessment",
        "Clinical Cases"
    ], horizontal=True)
    
    if topic == "Metabolic Interactions":
        st.markdown("""
        ### Metabolic Drug Interactions
        
        Study the effects of:
        - Enzyme Inhibition
        - Enzyme Induction
        - Metabolic Competition
        """)
        
        interaction_type = st.selectbox(
            "Select Interaction Type",
            ["Enzyme Inhibition", "Enzyme Induction"]
        )
        
        if interaction_type == "Enzyme Inhibition":
            col1, col2 = st.columns(2)
            with col1:
                initial_conc = st.slider("Initial Drug Concentration (mg/L)", 1.0, 100.0, 50.0)
                ki = st.slider("Inhibition Constant (Ki)", 0.1, 10.0, 1.0)
            with col2:
                inhibitor_conc = st.slider("Inhibitor Concentration (mg/L)", 0.0, 20.0, 0.0)
            
            time_points = np.linspace(0, 24, 100)
            baseline = initial_conc * np.exp(-0.1 * time_points)
            inhibited = calculate_metabolic_inhibition(time_points, initial_conc, inhibitor_conc, ki)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_points, y=baseline, name="Without Inhibitor"))
            fig.add_trace(go.Scatter(x=time_points, y=inhibited, name="With Inhibitor"))
            
            fig.update_layout(
                title="Effect of Metabolic Inhibition",
                xaxis_title="Time (hours)",
                yaxis_title="Drug Concentration (mg/L)"
            )
            
            st.plotly_chart(fig)
            
            # Clinical significance
            auc_increase = (np.trapz(inhibited, time_points) / np.trapz(baseline, time_points) - 1) * 100
            st.warning(f"AUC increased by {auc_increase:.1f}% due to metabolic inhibition")
            
        else:  # Enzyme Induction
            col1, col2 = st.columns(2)
            with col1:
                initial_conc = st.slider("Initial Drug Concentration (mg/L)", 1.0, 100.0, 50.0)
            with col2:
                induction_factor = st.slider("Enzyme Induction Factor", 1.0, 5.0, 2.0)
            
            time_points = np.linspace(0, 24, 100)
            baseline = initial_conc * np.exp(-0.1 * time_points)
            induced = calculate_enzyme_induction(time_points, initial_conc, induction_factor-1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_points, y=baseline, name="Without Induction"))
            fig.add_trace(go.Scatter(x=time_points, y=induced, name="With Induction"))
            
            fig.update_layout(
                title="Effect of Enzyme Induction",
                xaxis_title="Time (hours)",
                yaxis_title="Drug Concentration (mg/L)"
            )
            
            st.plotly_chart(fig)
            
            # Clinical significance
            auc_decrease = (1 - np.trapz(induced, time_points) / np.trapz(baseline, time_points)) * 100
            st.warning(f"AUC decreased by {auc_decrease:.1f}% due to enzyme induction")
    
    elif topic == "Pharmacokinetic Interactions":
        st.markdown("""
        ### Pharmacokinetic Interactions
        
        Explore interactions affecting:
        - Absorption
        - Distribution
        - Metabolism
        - Excretion
        """)
        
        pk_type = st.selectbox(
            "Select PK Interaction Type",
            ["Absorption Interaction", "Protein Binding Interaction"]
        )
        
        if pk_type == "Absorption Interaction":
            col1, col2 = st.columns(2)
            with col1:
                ka_normal = st.slider("Normal Absorption Rate (1/hr)", 0.1, 2.0, 0.5)
                dose = st.slider("Drug Dose (mg)", 10, 200, 100)
            with col2:
                interaction_factor = st.slider("Interaction Effect", 0.1, 2.0, 1.0)
            
            time_points = np.linspace(0, 12, 100)
            conc_normal = dose * ka_normal * np.exp(-0.1 * time_points)
            conc_interaction = dose * (ka_normal * interaction_factor) * np.exp(-0.1 * time_points)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_points, y=conc_normal, name="Normal Absorption"))
            fig.add_trace(go.Scatter(x=time_points, y=conc_interaction, name="With Interaction"))
            
            fig.update_layout(
                title="Effect on Drug Absorption",
                xaxis_title="Time (hours)",
                yaxis_title="Drug Concentration (mg/L)"
            )
            
            st.plotly_chart(fig)
            
        elif pk_type == "Protein Binding Interaction":
            st.markdown("""
            ### Protein Binding Displacement
            
            When a drug is displaced from plasma proteins:
            - Free drug concentration increases
            - Volume of distribution changes
            - Clearance of free drug increases
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                total_conc = st.slider("Total Drug Concentration (mg/L)", 10, 200, 100)
                normal_free_fraction = st.slider("Normal Free Fraction (%)", 1, 20, 10) / 100
            with col2:
                displacement_factor = st.slider("Displacement Factor", 1.0, 5.0, 2.0)
                clearance = st.slider("Clearance Rate (L/hr)", 0.1, 2.0, 0.5)
            
            time_points = np.linspace(0, 24, 100)
            
            # Calculate normal concentrations
            free_conc_normal = total_conc * normal_free_fraction
            bound_conc_normal = total_conc * (1 - normal_free_fraction)
            
            # Calculate displaced concentrations
            new_free_fraction = min(normal_free_fraction * displacement_factor, 1.0)
            free_conc_displaced = total_conc * new_free_fraction
            bound_conc_displaced = total_conc * (1 - new_free_fraction)
            
            # Calculate time-dependent concentrations
            free_normal_time = free_conc_normal * np.exp(-clearance * time_points)
            free_displaced_time = free_conc_displaced * np.exp(-clearance * time_points)
            bound_normal_time = bound_conc_normal * np.exp(-clearance * time_points * 0.2)  # Bound drug eliminates slower
            bound_displaced_time = bound_conc_displaced * np.exp(-clearance * time_points * 0.2)
            
            total_normal_time = free_normal_time + bound_normal_time
            total_displaced_time = free_displaced_time + bound_displaced_time
            
            # Create subplots
            fig = make_subplots(rows=2, cols=1,
                                subplot_titles=("Free Drug Concentration", "Total Drug Concentration"))
            
            # Free drug plot
            fig.add_trace(
                go.Scatter(x=time_points, y=free_normal_time, 
                        name="Normal Free Conc", line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=time_points, y=free_displaced_time, 
                        name="Displaced Free Conc", line=dict(color='red')),
                row=1, col=1
            )
            
            # Total drug plot
            fig.add_trace(
                go.Scatter(x=time_points, y=total_normal_time, 
                        name="Normal Total Conc", line=dict(color='blue', dash='dash')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=time_points, y=total_displaced_time, 
                        name="Displaced Total Conc", line=dict(color='red', dash='dash')),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                title_text="Effect of Protein Binding Displacement",
                showlegend=True
            )
            
            fig.update_xaxes(title_text="Time (hours)")
            fig.update_yaxes(title_text="Concentration (mg/L)")
            
            st.plotly_chart(fig)
            
            # Calculate and display clinical metrics
            initial_free_increase = ((free_displaced_time[0] / free_normal_time[0]) - 1) * 100
            auc_free_increase = (np.trapz(free_displaced_time, time_points) / 
                                np.trapz(free_normal_time, time_points) - 1) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Initial Free Drug Increase", f"{initial_free_increase:.1f}%")
            with col2:
                st.metric("Free Drug AUC Increase", f"{auc_free_increase:.1f}%")
            
            # Clinical significance warning
            if initial_free_increase > 50:
                st.warning("""
                **High Risk Interaction:**
                - Significant increase in free drug concentration
                - Monitor for drug toxicity
                - Consider dose reduction
                """)
            elif initial_free_increase > 20:
                st.info("""
                **Moderate Risk Interaction:**
                - Monitor drug levels and clinical response
                - Consider dose adjustment if necessary
                """)
            else:
                st.success("""
                **Low Risk Interaction:**
                - Routine monitoring adequate
                - No immediate dose adjustment needed
                """)
    
    elif topic == "Pharmacodynamic Interactions":
        st.markdown("""
        ### Pharmacodynamic Interactions
        
        Study combined drug effects:
        - Additive Effects
        - Synergism
        - Antagonism
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            drug1_effect = st.slider("Drug 1 Effect (%)", 0, 100, 50)
            drug2_effect = st.slider("Drug 2 Effect (%)", 0, 100, 30)
        with col2:
            interaction_type = st.selectbox(
                "Interaction Type",
                ["Additive", "Synergistic", "Antagonistic"]
            )
        
        # Calculate combined effects
        if interaction_type == "Additive":
            interaction_factor = 0
        elif interaction_type == "Synergistic":
            interaction_factor = 0.5
        else:  # Antagonistic
            interaction_factor = -0.3
        
        combined_effect = calculate_synergy_effect(drug1_effect/100, drug2_effect/100, interaction_factor)
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(name="Drug 1", x=["Individual Effects"], y=[drug1_effect]),
            go.Bar(name="Drug 2", x=["Individual Effects"], y=[drug2_effect]),
            go.Bar(name="Combined", x=["Combined Effect"], y=[combined_effect*100])
        ])
        
        fig.update_layout(
            title="Drug Combination Effects",
            yaxis_title="Effect (%)",
            barmode='group'
        )
        
        st.plotly_chart(fig)
    
    elif topic == "Risk Assessment":
        st.markdown("""
        ### Drug Interaction Risk Assessment
        
        Evaluate the risk level of drug combinations.
        """)
        
        # Risk assessment form
        col1, col2 = st.columns(2)
        with col1:
            drug1_narrow = st.checkbox("Drug 1 has narrow therapeutic index")
            drug1_critical = st.checkbox("Drug 1 is critical for disease management")
        with col2:
            drug2_inhibitor = st.checkbox("Drug 2 is strong inhibitor/inducer")
            alternative_available = st.checkbox("Alternative therapy available")
        
        # Calculate risk score
        risk_score = 0
        if drug1_narrow: risk_score += 3
        if drug1_critical: risk_score += 2
        if drug2_inhibitor: risk_score += 2
        if not alternative_available: risk_score += 1
        
        # Display risk assessment
        risk_level = "Low" if risk_score <= 2 else "Moderate" if risk_score <= 5 else "High"
        risk_color = "green" if risk_score <= 2 else "orange" if risk_score <= 5 else "red"
        
        st.markdown(f"""
        #### Risk Assessment Results
        
        Risk Score: **{risk_score}/8**  
        Risk Level: **:{risk_color}[{risk_level}]**
        """)
        
        # Recommendations
        st.markdown("### Recommendations")
        if risk_score <= 2:
            st.success("Monitor routine clinical parameters")
        elif risk_score <= 5:
            st.warning("""
            - Consider alternative therapy
            - Increase monitoring frequency
            - Adjust dosing if needed
            """)
        else:
            st.error("""
            - Avoid combination if possible
            - Consider alternative therapy
            - If necessary, implement intensive monitoring
            - Adjust dosing with careful titration
            """)
    
    elif topic == "Clinical Cases":
        st.markdown("### Clinical Case Studies")
        
        case = st.selectbox(
            "Select Clinical Case",
            ["Warfarin-Antibiotic Interaction", 
             "Statin-CYP3A4 Inhibitor Interaction",
             "SSRI-NSAID Interaction"]
        )
        
        if case == "Warfarin-Antibiotic Interaction":
            st.markdown("""
            #### Case: Warfarin-Antibiotic Interaction
            
            **Patient Profile:**
            - 65-year-old male
            - On stable warfarin therapy (INR 2-3)
            - Prescribed antibiotics for respiratory infection
            
            **Interaction Mechanism:**
            - Antibiotics alter gut flora
            - Reduced vitamin K production
            - Enhanced warfarin effect
            """)
            
            # Interactive INR simulation
            time_points = np.linspace(0, 14, 100)
            baseline_inr = 2.5 + np.random.normal(0, 0.1, 100)
            interaction_inr = 2.5 * np.exp(0.1 * time_points) + np.random.normal(0, 0.2, 100)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_points, y=baseline_inr, name="Normal INR"))
            fig.add_trace(go.Scatter(x=time_points, y=interaction_inr, name="With Antibiotic"))
            fig.add_hrect(y0=2, y1=3, fillcolor="green", opacity=0.2, line_width=0)
            
            fig.update_layout(
                title="INR Changes with Antibiotic Therapy",
                xaxis_title="Days",
                yaxis_title="INR"
            )
            
            st.plotly_chart(fig)
            
            st.warning("""
            **Management Strategy:**
            1. Increase INR monitoring frequency
            2. Consider warfarin dose reduction
            3. Monitor for bleeding signs
            """)
            
        elif case == "Statin-CYP3A4 Inhibitor Interaction":
            st.markdown("""
            #### Case: Statin-CYP3A4 Inhibitor Interaction
            
            **Patient Profile:**
            - 58-year-old female
            - On atorvastatin 40mg daily
            - Starting clarithromycin for H. pylori infection
            
            **Interaction Mechanism:**
            - CYP3A4 inhibition by clarithromycin
            - Reduced statin metabolism
            - Increased risk of myopathy
            """)
            
            # Interactive statin concentration simulation
            time_points = np.linspace(0, 7, 100)  # 7 days

            # Simulate statin concentrations
            baseline_conc = 100 * np.exp(-0.2 * time_points) + np.random.normal(0, 5, 100)
            inhibited_conc = 100 * np.exp(-0.05 * time_points) + np.random.normal(0, 10, 100)

            fig = go.Figure()

            # Add zones first (below the data)
            fig.add_hrect(
                y0=80, y1=120,
                fillcolor="green", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="Therapeutic Range",
                annotation=dict(font_size=10)
            )

            fig.add_hrect(
                y0=120, y1=200,
                fillcolor="red", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="Risk Zone",
                annotation=dict(font_size=10)
            )

            # Add concentration traces
            fig.add_trace(go.Scatter(x=time_points, y=baseline_conc, name="Normal Statin Level"))
            fig.add_trace(go.Scatter(x=time_points, y=inhibited_conc, name="With CYP3A4 Inhibitor"))

            fig.update_layout(
                title="Statin Plasma Concentration with CYP3A4 Inhibition",
                xaxis_title="Days",
                yaxis_title="Relative Statin Concentration (%)",
                yaxis=dict(range=[0, 200])  # Set fixed y-axis range
            )
                        
            st.plotly_chart(fig)
            
            # Calculate risk metrics
            auc_increase = (np.trapz(inhibited_conc, time_points) / np.trapz(baseline_conc, time_points) - 1) * 100
            max_conc_increase = (np.max(inhibited_conc) / np.max(baseline_conc) - 1) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AUC Increase", f"{auc_increase:.1f}%")
            with col2:
                st.metric("Peak Level Increase", f"{max_conc_increase:.1f}%")
            
            st.warning("""
            **Management Strategy:**
            1. Reduce statin dose by 50-75%
            2. Monitor for muscle symptoms
            3. Consider temporary statin discontinuation
            4. Check CK levels if symptoms develop
            """)

        elif case == "SSRI-NSAID Interaction":
            st.markdown("""
            #### Case: SSRI-NSAID Interaction
            
            **Patient Profile:**
            - 45-year-old female
            - On escitalopram 20mg daily
            - Starting naproxen for arthritis
            
            **Interaction Mechanism:**
            - Combined effect on platelet function
            - Increased risk of GI bleeding
            - Additive serotonergic effects
            """)
            
            # Interactive bleeding risk simulation
            time_points = np.linspace(0, 30, 100)  # 30 days
            
            # Simulate bleeding risk scores
            baseline_risk = 1.0 + 0.5 * np.sin(time_points/10) + np.random.normal(0, 0.1, 100)
            ssri_risk = 2.0 + 0.5 * np.sin(time_points/10) + np.random.normal(0, 0.1, 100)
            combined_risk = 4.0 + 1.0 * np.sin(time_points/10) + np.random.normal(0, 0.2, 100)
            
            fig = go.Figure()
            
            # Add risk zones with specific boundaries
            fig.add_hrect(
                y0=0, y1=2,
                fillcolor="green", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="Low Risk",
                annotation=dict(font_size=10)
            )
            
            fig.add_hrect(
                y0=2, y1=4,
                fillcolor="yellow", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="Moderate Risk",
                annotation=dict(font_size=10)
            )
            
            fig.add_hrect(
                y0=4, y1=6,
                fillcolor="red", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="High Risk",
                annotation=dict(font_size=10)
            )
            
            # Add risk traces
            fig.add_trace(go.Scatter(x=time_points, y=baseline_risk, name="Baseline Risk"))
            fig.add_trace(go.Scatter(x=time_points, y=ssri_risk, name="SSRI Alone"))
            fig.add_trace(go.Scatter(x=time_points, y=combined_risk, name="SSRI + NSAID"))
            
            fig.update_layout(
                title="Bleeding Risk Assessment",
                xaxis_title="Days",
                yaxis_title="Relative Risk Score",
                yaxis=dict(range=[0, 6])  # Set fixed y-axis range
            )
            
            st.plotly_chart(fig)
            
            # Calculate risk metrics
            risk_increase = (np.mean(combined_risk) / np.mean(baseline_risk) - 1) * 100
            peak_risk = np.max(combined_risk)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Risk Increase", f"{risk_increase:.1f}%")
            with col2:
                st.metric("Peak Risk Score", f"{peak_risk:.1f}")
            
            if peak_risk > 4.0:
                st.error("""
                **High Risk Combination:**
                1. Consider alternative pain management
                2. Use lowest effective NSAID dose
                3. Add gastroprotection (PPI)
                4. Monitor for bleeding signs
                """)
            else:
                st.warning("""
                **Management Strategy:**
                1. Use lowest effective doses
                2. Limited duration of NSAID
                3. Consider gastroprotection
                4. Educate patient on warning signs
                """)
if __name__ == "__main__":
    main()