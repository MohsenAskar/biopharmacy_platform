import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.integrate import odeint
st.set_page_config(layout="wide")

def one_compartment_iv_bolus(t, D, V, k):
    """IV bolus administration"""
    return (D/V) * np.exp(-k*t)

def one_compartment_infusion(t, R, V, k, T_inf):
    """IV infusion administration"""
    C = np.zeros_like(t)
    for i, time in enumerate(t):
        if time <= T_inf:
            C[i] = (R/k/V) * (1 - np.exp(-k*time))
        else:
            C[i] = (R/k/V) * (1 - np.exp(-k*T_inf)) * np.exp(-k*(time-T_inf))
    return C

def one_compartment_oral(t, D, V, ka, ke, F=1.0):
    """Oral administration"""
    return (F*D*ka)/(V*(ka-ke)) * (np.exp(-ke*t) - np.exp(-ka*t))

def one_compartment_im_sc(t, D, V, ka, ke, F=1.0):
    """IM/SC administration (similar to oral but with different ka and F)"""
    return (F*D*ka)/(V*(ka-ke)) * (np.exp(-ke*t) - np.exp(-ka*t))



def two_compartment_system(y, t, k12, k21, k10):
    """Define two-compartment system equations"""
    central, peripheral = y
    dcentral_dt = -k12*central + k21*peripheral - k10*central
    dperipheral_dt = k12*central - k21*peripheral
    return [dcentral_dt, dperipheral_dt]

def two_compartment_iv_bolus(t, D, V1, k12, k21, k10):
    """Calculate concentration for two-compartment IV bolus"""
    initial_conditions = [D/V1, 0]
    solution = odeint(two_compartment_system, initial_conditions, t, args=(k12, k21, k10))
    return solution[:, 0]  # Return central compartment concentration

def plot_concentration_time(t, concentrations, title, labels=None):
    """Create concentration-time plot"""
    if labels is None:
        labels = ['Concentration']
    
    fig = go.Figure()
    
    if isinstance(concentrations, list):
        for conc, label in zip(concentrations, labels):
            fig.add_trace(go.Scatter(
                x=t,
                y=conc,
                name=label,
                mode='lines'
            ))
    else:
        fig.add_trace(go.Scatter(
            x=t,
            y=concentrations,
            name=labels[0],
            mode='lines'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time (hours)",
        yaxis_title="Concentration (mg/L)",
        showlegend=True
    )
    
    return fig

def main():
    st.title("Pharmacokinetic Modeling")
    
    page = st.radio("Select Topic", 
        ["Interactive Models","Route Comparison", "Drug Case Studies", "Quiz"], horizontal=True)
    if page == "Interactive Models":
        model_type = st.selectbox(
            "Select Model Type",
            ["One-Compartment Model", "Two-Compartment Model"]
        )
        
        if model_type == "One-Compartment Model":
            st.markdown("""
            ### One-Compartment Model
            
            The one-compartment model assumes the body acts as a single, well-mixed compartment.
            The drug concentration follows first-order elimination:
            
            $C(t) = \\frac{D}{V}e^{-kt}$ (IV bolus)
            
            $C(t) = \\frac{FDk_a}{V(k_a-k_e)}(e^{-k_et} - e^{-k_at})$ (Oral)
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                dose = st.slider("Dose (mg)", 100, 1000, 500, 50)
                volume = st.slider("Volume of Distribution (L)", 10, 100, 50, 5)
            with col2:
                k_elim = st.slider("Elimination Rate Constant (1/hr)", 0.1, 2.0, 0.5, 0.1)
                ka = st.slider("Absorption Rate Constant (1/hr)", 0.1, 2.0, 1.0, 0.1)
            
            # Generate time points
            t = np.linspace(0, 24, 100)
            
            # Calculate concentrations
            c_iv = one_compartment_iv_bolus(t, dose, volume, k_elim)
            c_oral = one_compartment_oral(t, dose, volume, ka, k_elim)
            
            # Plot results
            fig = plot_concentration_time(t, [c_iv, c_oral], 
                "One-Compartment Model: IV vs Oral", 
                ["IV Bolus", "Oral"])
            st.plotly_chart(fig)
            
            # Calculate and display PK parameters
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cmax IV (mg/L)", f"{np.max(c_iv):.1f}")
            with col2:
                st.metric("Cmax Oral (mg/L)", f"{np.max(c_oral):.1f}")
            with col3:
                st.metric("Half-life (hr)", f"{np.log(2)/k_elim:.1f}")
            
        else:  # Two-Compartment Model
            st.markdown("""
            ### Two-Compartment Model
            
            The two-compartment model divides the body into central and peripheral compartments.
            The drug transfer between compartments follows first-order kinetics:
            
            $\\frac{dC_1}{dt} = -k_{12}C_1 + k_{21}C_2 - k_{10}C_1$
            
            $\\frac{dC_2}{dt} = k_{12}C_1 - k_{21}C_2$
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                dose = st.slider("Dose (mg)", 100, 1000, 500, 50)
                v1 = st.slider("Central Volume (L)", 10, 100, 30, 5)
            with col2:
                k12 = st.slider("k12 (1/hr)", 0.1, 2.0, 0.5, 0.1)
                k21 = st.slider("k21 (1/hr)", 0.1, 2.0, 0.3, 0.1)
            
            k10 = st.slider("k10 (1/hr)", 0.1, 2.0, 0.4, 0.1)
            
            # Generate time points
            t = np.linspace(0, 24, 100)
            
            # Calculate concentrations
            c_central = two_compartment_iv_bolus(t, dose, v1, k12, k21, k10)
            
            # Plot results
            fig = plot_concentration_time(t, c_central, 
                "Two-Compartment Model: Central Compartment", 
                ["Central Compartment"])
            st.plotly_chart(fig)
            
            # Calculate and display PK parameters
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Initial Conc. (mg/L)", f"{c_central[0]:.1f}")
            with col2:
                # Calculate distribution half-life (approximate)
                alpha = k12 + k21 + k10  # Distribution phase rate constant
                st.metric("Distribution t1/2 (hr)", f"{np.log(2)/alpha:.2f}")
    
    elif page == "Route Comparison":
        st.markdown("""
        ### Administration Route Comparison
        Compare how different administration routes affect drug concentration profiles.
        """)
        
        # Parameters
        col1, col2 = st.columns(2)
        with col1:
            dose = st.slider("Dose (mg)", 100, 1000, 500, 50)
            volume = st.slider("Volume of Distribution (L)", 10, 100, 50, 5)
        with col2:
            k_elim = st.slider("Elimination Rate (1/hr)", 0.1, 2.0, 0.5, 0.1)
            ka = st.slider("Absorption Rate (1/hr)", 0.1, 2.0, 1.0, 0.1)
        
        # Additional route-specific parameters
        infusion_time = st.slider("Infusion Time (hr)", 0.25, 4.0, 1.0, 0.25)
        infusion_rate = dose/infusion_time  # mg/hr
        
        # Bioavailability for different routes
        F_oral = 0.8  # 80% oral bioavailability
        F_im = 0.9    # 90% IM bioavailability
        F_sc = 0.85   # 85% SC bioavailability
        
        # Time points
        t = np.linspace(0, 24, 200)
        
        # Calculate profiles for different routes
        c_iv_bolus = one_compartment_iv_bolus(t, dose, volume, k_elim)
        c_iv_inf = one_compartment_infusion(t, infusion_rate, volume, k_elim, infusion_time)
        c_oral = one_compartment_oral(t, dose, volume, ka, k_elim, F_oral)
        c_im = one_compartment_im_sc(t, dose, volume, ka*1.5, k_elim, F_im)  # Faster ka for IM
        c_sc = one_compartment_im_sc(t, dose, volume, ka*0.7, k_elim, F_sc)  # Slower ka for SC
        
        # Create comparative plot
        concentrations = [c_iv_bolus, c_iv_inf, c_oral, c_im, c_sc]
        labels = ["IV Bolus", "IV Infusion", "Oral", "IM", "SC"]
        
        fig = plot_concentration_time(t, concentrations, "Route Comparison", labels)
        st.plotly_chart(fig)
        
        # Display route-specific metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("IV Bolus Cmax (mg/L)", f"{np.max(c_iv_bolus):.1f}")
            st.metric("IV Inf. Cmax (mg/L)", f"{np.max(c_iv_inf):.1f}")
        with col2:
            st.metric("Oral Cmax (mg/L)", f"{np.max(c_oral):.1f}")
            st.metric("IM Cmax (mg/L)", f"{np.max(c_im):.1f}")
        with col3:
            st.metric("SC Cmax (mg/L)", f"{np.max(c_sc):.1f}")
            st.metric("Half-life (hr)", f"{np.log(2)/k_elim:.1f}")

        st.markdown("""
        ### Routes of administration different models

        Different routes of administration can be modeled using the following equations:

        1. **IV Bolus** (Instantaneous input):
        $C(t) = \\frac{D}{V}e^{-k_{el}t}$
        where:
        - C(t) = drug concentration at time t
        - D = dose
        - V = volume of distribution
        - k_el = elimination rate constant

        2. **IV Infusion** (Constant input rate):
        $C(t) = \\frac{R}{k_{el}V}(1-e^{-k_{el}t})$ (during infusion)
        $C(t) = \\frac{R}{k_{el}V}(1-e^{-k_{el}T_{inf}})e^{-k_{el}(t-T_{inf})}$ (after infusion)
        where:
        - R = infusion rate
        - T_inf = infusion duration

        3. **Oral Administration** (First-order absorption):
        $C(t) = \\frac{FDk_a}{V(k_a-k_{el})}(e^{-k_{el}t} - e^{-k_at})$
        where:
        - F = bioavailability
        - k_a = absorption rate constant

        4. **IM/SC Administration** (First-order absorption with different bioavailability):
        $C(t) = \\frac{F_{im/sc}Dk_a}{V(k_a-k_{el})}(e^{-k_{el}t} - e^{-k_at})$
        where:
        - F_im/sc = bioavailability for IM or SC route
        - k_a = absorption rate constant (different for IM and SC)

        The key differences between routes are:
        - Bioavailability (F)
        - Absorption rate constants (k_a)
        - Input patterns (immediate vs gradual)
        """)

    elif page == "Drug Case Studies":
        drug = st.selectbox("Select Drug Case Study", 
            ["Morphine", "Lidocaine"])
        
        if drug == "Morphine":
            st.markdown("""
            ### Morphine PK Case Study
            
            Morphine can be administered through multiple routes:
            - IV (bolus and infusion)
            - IM/SC injection
            - Oral administration
            
            Key characteristics:
            - Oral bioavailability: ~30%
            - IM/SC bioavailability: ~90%
            - Terminal half-life: 2-3 hours
            """)
            
            # Morphine-specific parameters
            col1, col2 = st.columns(2)
            with col1:
                dose = st.slider("Morphine Dose (mg)", 5, 30, 10, 5)
                volume = 70  # Fixed Vd for morphine
            with col2:
                k_elim = 0.35  # Fixed elimination rate
                route = st.selectbox("Select Routes to Compare", 
                    ["All Routes", "IV vs Oral", "IV vs IM/SC"])
            
            t = np.linspace(0, 12, 200)  # 12-hour simulation
            
            # Calculate morphine concentrations
            c_iv_bolus = one_compartment_iv_bolus(t, dose, volume, k_elim)
            c_iv_inf = one_compartment_infusion(t, dose/1.0, volume, k_elim, 1.0)  # 1-hour infusion
            c_oral = one_compartment_oral(t, dose, volume, 1.2, k_elim, 0.3)  # 30% bioavailability
            c_im = one_compartment_im_sc(t, dose, volume, 1.5, k_elim, 0.9)  # 90% bioavailability
            
            if route == "All Routes":
                concentrations = [c_iv_bolus, c_iv_inf, c_oral, c_im]
                labels = ["IV Bolus", "IV Infusion (1hr)", "Oral", "IM"]
            elif route == "IV vs Oral":
                concentrations = [c_iv_bolus, c_iv_inf, c_oral]
                labels = ["IV Bolus", "IV Infusion (1hr)", "Oral"]
            else:  # IV vs IM/SC
                concentrations = [c_iv_bolus, c_im]
                labels = ["IV Bolus", "IM"]
            
            fig = plot_concentration_time(t, concentrations, 
                f"Morphine Concentration Profiles ({dose}mg dose)", labels)
            st.plotly_chart(fig)
            
        else:  # Lidocaine
            st.markdown("""
            ### Lidocaine PK Case Study
            
            Lidocaine is commonly administered through:
            - IV (bolus and infusion)
            - SC injection (local anesthesia)
            - Topical application
            
            Key characteristics:
            - High first-pass metabolism
            - Terminal half-life: 1.5-2 hours
            - Local pH effects on absorption
            """)
            
            # Lidocaine-specific parameters
            col1, col2 = st.columns(2)
            with col1:
                dose = st.slider("Lidocaine Dose (mg)", 50, 300, 100, 50)
                volume = 40  # Fixed Vd for lidocaine
            with col2:
                k_elim = 0.45  # Fixed elimination rate
                route = st.selectbox("Select Routes to Compare",
                    ["All Routes", "IV Formulations", "Local Administration"])
            
            t = np.linspace(0, 8, 200)  # 8-hour simulation
            
            # Calculate lidocaine concentrations
            c_iv_bolus = one_compartment_iv_bolus(t, dose, volume, k_elim)
            c_iv_inf = one_compartment_infusion(t, dose/0.5, volume, k_elim, 0.5)  # 30-min infusion
            c_sc = one_compartment_im_sc(t, dose, volume, 0.8, k_elim, 0.95)  # 95% local bioavailability
            
            if route == "All Routes":
                concentrations = [c_iv_bolus, c_iv_inf, c_sc]
                labels = ["IV Bolus", "IV Infusion (30min)", "SC"]
            elif route == "IV Formulations":
                concentrations = [c_iv_bolus, c_iv_inf]
                labels = ["IV Bolus", "IV Infusion (30min)"]
            else:  # Local Administration
                concentrations = [c_sc]
                labels = ["SC"]
            
            fig = plot_concentration_time(t, concentrations,
                f"Lidocaine Concentration Profiles ({dose}mg dose)", labels)
            st.plotly_chart(fig)

        # Display PK parameters
        st.markdown("### Key PK Parameters")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cmax IV Bolus (mg/L)", f"{np.max(c_iv_bolus):.1f}")
        with col2:
            st.metric("Time Above MEC (hr)", 
                f"{np.sum(c_iv_bolus > np.max(c_iv_bolus)*0.2)/len(t)*24:.1f}")
        with col3:
            st.metric("Terminal Half-life (hr)", f"{np.log(2)/k_elim:.1f}")
    
    elif page == "Quiz":
        st.header("Test Your Understanding")
        
        # Question 1
        st.subheader("Question 1")
        quiz_answer_1 = st.radio(
            "Which parameter primarily determines the initial concentration in an IV bolus one-compartment model?",
            (
                "Elimination rate constant (k)",
                "Dose/Volume ratio (D/V)",
                "Absorption rate constant (ka)"
            )
        )
        
        if quiz_answer_1 == "Dose/Volume ratio (D/V)":
            st.success("Correct! The initial concentration (C0) in an IV bolus is determined by the dose divided by the volume of distribution.")
        else:
            st.error("Not quite. In an IV bolus, the initial concentration is simply the dose divided by the volume of distribution (C0 = D/V).")
        
        # Question 2
        st.subheader("Question 2")
        quiz_answer_2 = st.radio(
            "What is the main difference between one and two-compartment models?",
            (
                "Two-compartment models show faster elimination",
                "Two-compartment models have a distribution phase and an elimination phase",
                "Two-compartment models are only used for oral administration"
            )
        )
        
        if quiz_answer_2 == "Two-compartment models have a distribution phase and an elimination phase":
            st.success("Correct! Two-compartment models show both a rapid distribution phase (α phase) and a slower elimination phase (β phase).")
        else:
            st.error("Not quite. The key difference is that two-compartment models show distinct distribution and elimination phases.")


if __name__ == "__main__":
    main()