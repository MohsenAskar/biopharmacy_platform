import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

st.set_page_config(layout="wide")

def calculate_solubility(temperature, heat_of_solution, ref_solubility, ref_temp=298):
    """Calculate temperature-dependent solubility using van't Hoff equation"""
    R = 8.314  # Gas constant
    return ref_solubility * np.exp((heat_of_solution/R) * (1/ref_temp - 1/(temperature + 273.15)))

def calculate_surface_tension(concentration, gamma_0, k):
    """Calculate surface tension using simplified Gibbs equation"""
    return gamma_0 - k * np.log(1 + concentration)

def calculate_buffer_capacity(ka, buffer_conc, ph):
    """Calculate buffer capacity"""
    h = 10**(-ph)
    return (2.303 * ka * h * buffer_conc) / (ka + h)**2

def calculate_viscosity_shear(shear_rate, k, n):
    """Calculate viscosity for power law fluid"""
    return k * shear_rate**(n-1)

def calculate_degradation(time, k, c0, order=1):
    """Calculate concentration after degradation"""
    if order == 0:
        return c0 - k*time
    elif order == 1:
        return c0 * np.exp(-k*time)
    else:  # order == 2
        return 1 / (1/(c0) + k*time)

def main():
    st.title("Physical Pharmacy Interactive Module")
    
    # Navigation
    topic = st.radio("Select Topic", [
        "Solubility & Dissolution",
        "Surface Phenomena",
        "Rheology",
        "Buffer Systems",
        "Stability Testing"
    ], horizontal=True)
    
    if topic == "Solubility & Dissolution":
        st.markdown("""
        ### Solubility and Dissolution Relationships
        
        The temperature dependence of solubility follows the van't Hoff equation:
        
        $\\ln(\\frac{S_2}{S_1}) = -\\frac{\\Delta H_s}{R}(\\frac{1}{T_2} - \\frac{1}{T_1})$
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            heat_solution = st.slider("Heat of Solution (kJ/mol)", -50.0, 50.0, 20.0)
            ref_solubility = st.slider("Reference Solubility (mg/mL)", 0.1, 100.0, 10.0)
        
        # Calculate solubility vs temperature
        temp_range = np.linspace(0, 100, 100)
        solubility = calculate_solubility(temp_range, heat_solution*1000, ref_solubility)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temp_range,
            y=solubility,
            name="Solubility"
        ))
        
        fig.update_layout(
            title="Temperature-Dependent Solubility",
            xaxis_title="Temperature (°C)",
            yaxis_title="Solubility (mg/mL)"
        )
        
        st.plotly_chart(fig)
        
    elif topic == "Surface Phenomena":
        st.markdown("""
        ### Surface Tension and Interfacial Phenomena
        
        Surface tension changes with surfactant concentration according to the Gibbs equation:
        
        $\\gamma = \\gamma_0 - kT\\Gamma_\\max \\ln(1 + \\frac{c}{a})$
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            gamma_0 = st.slider("Pure Solvent Surface Tension (mN/m)", 20.0, 80.0, 72.0)
            k_surfactant = st.slider("Surfactant Coefficient", 1.0, 20.0, 10.0)
        
        # Calculate surface tension vs concentration
        conc_range = np.logspace(-3, 1, 100)
        surface_tension = calculate_surface_tension(conc_range, gamma_0, k_surfactant)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=conc_range,
            y=surface_tension,
            name="Surface Tension"
        ))
        
        fig.update_layout(
            title="Surface Tension vs Surfactant Concentration",
            xaxis_title="Concentration (mM)",
            yaxis_title="Surface Tension (mN/m)",
            xaxis_type="log"
        )
        
        st.plotly_chart(fig)
        
    elif topic == "Rheology":
        st.markdown("""
        ### Rheology of Pharmaceutical Systems
        
        Power Law model for non-Newtonian fluids:
        
        $\\tau = K\\dot{\\gamma}^n$
        
        where:
        - τ = shear stress
        - γ̇ = shear rate
        - K = consistency index
        - n = flow behavior index
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            k_value = st.slider("Consistency Index (K)", 0.1, 10.0, 1.0)
            n_value = st.slider("Flow Behavior Index (n)", 0.1, 2.0, 1.0)
        
        # Calculate viscosity vs shear rate
        shear_rates = np.logspace(-1, 3, 100)
        viscosity = calculate_viscosity_shear(shear_rates, k_value, n_value)
        
        fig = make_subplots(rows=1, cols=2,
                          subplot_titles=("Viscosity vs Shear Rate", "Flow Curve"))
        
        fig.add_trace(
            go.Scatter(x=shear_rates, y=viscosity, name="Viscosity"),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=shear_rates, y=viscosity*shear_rates, name="Shear Stress"),
            row=1, col=2
        )
        
        fig.update_layout(height=400)
        fig.update_xaxes(type="log")
        st.plotly_chart(fig)
        
    elif topic == "Buffer Systems":
        st.markdown("""
        ### Buffer Systems and pH Calculations
        
        Buffer capacity (β) is given by:
        
        $\\beta = \\frac{2.303K_aC_B[H^+]}{(K_a + [H^+])^2}$
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            pka = st.slider("pKa", 2.0, 12.0, 7.0, 0.1)
            buffer_conc = st.slider("Buffer Concentration (M)", 0.01, 0.5, 0.1, 0.01)
        
        # Calculate buffer capacity vs pH
        ph_range = np.linspace(pka-2, pka+2, 100)
        buffer_cap = [calculate_buffer_capacity(10**-pka, buffer_conc, ph) for ph in ph_range]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ph_range,
            y=buffer_cap,
            name="Buffer Capacity"
        ))
        
        fig.update_layout(
            title="Buffer Capacity vs pH",
            xaxis_title="pH",
            yaxis_title="Buffer Capacity (β)"
        )
        
        st.plotly_chart(fig)
        
    elif topic == "Stability Testing":
        st.markdown("""
        ### Stability Testing and Kinetics
        
        Drug degradation can follow different orders:
        
        Zero Order: $C = C_0 - kt$
        
        First Order: $C = C_0e^{-kt}$
        
        Second Order: $\\frac{1}{C} = \\frac{1}{C_0} + kt$
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            order = st.selectbox("Reaction Order", [0, 1, 2])
            k_rate = st.slider(f"Rate Constant (k)", 0.001, 0.1, 0.01, 0.001)
        with col2:
            initial_conc = st.slider("Initial Concentration (mg/mL)", 1.0, 100.0, 50.0)
        
        # Calculate degradation over time
        time_points = np.linspace(0, 100, 100)
        concentration = calculate_degradation(time_points, k_rate, initial_conc, order)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_points,
            y=concentration,
            name="Drug Concentration"
        ))
        
        # Add t90 and t50 lines
        if order == 0:
            t90 = 0.1 * initial_conc / k_rate
            t50 = 0.5 * initial_conc / k_rate
        elif order == 1:
            t90 = -np.log(0.9) / k_rate
            t50 = -np.log(0.5) / k_rate
        else:
            t90 = (1/0.9 - 1/initial_conc) / k_rate
            t50 = (1/0.5 - 1/initial_conc) / k_rate
        
        fig.add_vline(x=t90, line_dash="dash", annotation_text="t90")
        fig.add_vline(x=t50, line_dash="dash", annotation_text="t50")
        
        fig.update_layout(
            title=f"Drug Degradation ({order} Order Kinetics)",
            xaxis_title="Time",
            yaxis_title="Concentration (mg/mL)"
        )
        
        st.plotly_chart(fig)
        
        # Display stability metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("t90 (time to 90%)", f"{t90:.1f}")
        with col2:
            st.metric("t50 (time to 50%)", f"{t50:.1f}")
        with col3:
            st.metric("Rate Constant", f"{k_rate:.4f}")

if __name__ == "__main__":
    main()