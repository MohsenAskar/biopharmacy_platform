import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
st.set_page_config(layout="wide")


def ficks_first_law(C1, C2, D, dx):
    """Calculate flux using Fick's first law"""
    return -D * (C2 - C1) / dx

def simulate_diffusion_1D(nx, nt, D, dx, dt):
    """Simulate 1D diffusion using Fick's second law"""
    # Initialize concentration array
    C = np.zeros(nx)
    C[0] = 1.0  # Source concentration
    
    # Time evolution
    for t in range(nt):
        C_new = C.copy()
        for i in range(1, nx-1):
            C_new[i] = C[i] + D * dt/dx**2 * (C[i+1] - 2*C[i] + C[i-1])
        C = C_new
        
    return C

def higuchi_release(t, D, Cs, A, h):
    """Calculate Higuchi release profile"""
    return A * np.sqrt((2*Cs*D*t)/h)

def first_order_release(t, k, M0):
    """Calculate first-order release profile"""
    return M0 * (1 - np.exp(-k*t))

def zero_order_release(t, k, M0):
    """Calculate zero-order release profile"""
    return np.minimum(k*t, M0)
def korsmeyer_peppas(t, k, n, M0):
    """Korsmeyer-Peppas model"""
    return M0 * (k*t)**n

def biphasic_release(t, k1, k2, M0, fraction):
    """Biphasic release model"""
    phase1 = fraction * M0 * (1 - np.exp(-k1*t))
    phase2 = (1-fraction) * M0 * (1 - np.exp(-k2*t))
    return phase1 + phase2

def erosion_release(t, k, M0):
    """Surface erosion model"""
    return M0 * (1 - (1-k*t)**2)

def main():
    st.title("Drug Diffusion and Release Mechanisms")
    
    page = st.radio("Select Topic", 
        ["Fick's Laws", "Release Systems Comparison", "Case Studies"], horizontal=True)
    
    if page == "Fick's Laws":
        st.markdown("""
        ### Fick's Laws of Diffusion
        
        **Fick's First Law:**
        $J = -D\\frac{\\partial C}{\\partial x}$
        
        **Fick's Second Law:**
        $\\frac{\\partial C}{\\partial t} = D\\frac{\\partial^2 C}{\\partial x^2}$
        
        where:
        - J = flux
        - D = diffusion coefficient
        - C = concentration
        - x = distance
        - t = time
        """)
        
        # Interactive Fick's First Law
        st.subheader("Fick's First Law Visualization")
        col1, col2 = st.columns(2)
        with col1:
            D = st.slider("Diffusion Coefficient (D)", 1e-6, 1e-4, 1e-5, 1e-6)
            dx = st.slider("Distance (dx, μm)", 1.0, 100.0, 10.0, 1.0)
        with col2:
            C1 = st.slider("Concentration 1 (mg/mL)", 0.0, 100.0, 100.0, 1.0)
            C2 = st.slider("Concentration 2 (mg/mL)", 0.0, 100.0, 0.0, 1.0)
        
        # Calculate and plot flux
        flux = ficks_first_law(C1, C2, D, dx*1e-6)
        
        # Create visualization
        x = np.linspace(0, dx, 100)
        C = C1 + (C2 - C1) * x/dx
        
        fig = make_subplots(rows=2, cols=1, 
                          subplot_titles=("Concentration Gradient", "Resulting Flux"))
        
        fig.add_trace(
            go.Scatter(x=x, y=C, name="Concentration"),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=[0, dx], y=[flux, flux], name="Flux"),
            row=2, col=1
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig)
        
        # Fick's Second Law
        st.subheader("Fick's Second Law Simulation")
        
        D_2 = st.slider("Diffusion Coefficient (Second Law)", 0.1, 2.0, 0.5, 0.1)
        t_max = st.slider("Simulation Time", 1, 100, 50)
        
        # Simulate diffusion
        nx = 100
        nt = t_max
        dx = 1.0
        dt = 0.1
        
        C = simulate_diffusion_1D(nx, nt, D_2, dx, dt)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=np.arange(nx), y=C, name="Concentration"))
        fig2.update_layout(
            title="Concentration Profile",
            xaxis_title="Distance",
            yaxis_title="Concentration"
        )
        st.plotly_chart(fig2)
        
    elif page == "Release Systems Comparison":
        st.markdown("""
        ### Drug Release Systems
        
        Compare different drug release mechanisms:
        
        1. **Matrix System** (Higuchi Model):
        $M_t = A\\sqrt{\\frac{2C_sD_mt}{h}}$
        
        2. **First-Order Release**:
        $M_t = M_0(1-e^{-kt})$
        
        3. **Zero-Order Release**:
        $M_t = kt$
        """)
        
        # System parameters
        col1, col2 = st.columns(2)
        with col1:
            time_points = np.linspace(0, 24, 100)
            release_type = st.selectbox("Release System", 
                ["All Systems", "Matrix", "First-Order", "Zero-Order"])
        with col2:
            total_drug = st.slider("Total Drug Load (mg)", 10, 100, 50)
        
        # Calculate release profiles
        higuchi = higuchi_release(time_points, 1e-6, 1.0, 1.0, 1e-3)
        first_order = first_order_release(time_points, 0.15, total_drug)
        zero_order = zero_order_release(time_points, total_drug/24, total_drug)
        
        fig = go.Figure()
        
        if release_type in ["All Systems", "Matrix"]:
            fig.add_trace(go.Scatter(
                x=time_points, y=higuchi/np.max(higuchi)*total_drug, 
                name="Matrix (Higuchi)"
            ))
        
        if release_type in ["All Systems", "First-Order"]:
            fig.add_trace(go.Scatter(
                x=time_points, y=first_order, 
                name="First-Order"
            ))
            
        if release_type in ["All Systems", "Zero-Order"]:
            fig.add_trace(go.Scatter(
                x=time_points, y=zero_order, 
                name="Zero-Order"
            ))
        
        fig.update_layout(
            title="Drug Release Profiles",
            xaxis_title="Time (hours)",
            yaxis_title="Cumulative Drug Released (mg)"
        )
        st.plotly_chart(fig)
        
        # System comparison
        st.markdown("""
        #### System Characteristics:
        
        **Matrix System:**
        - Drug dispersed in polymer matrix
        - Release controlled by diffusion
        - Square root of time relationship
        
        **First-Order System:**
        - Release rate proportional to remaining drug
        - Common in porous matrices
        - Exponential decay pattern
        
        **Zero-Order System:**
        - Constant release rate
        - Independent of drug concentration
        - Ideal for sustained release
        """)
        
    elif page == "Case Studies":
        case = st.selectbox("Select Case Study", [
            "Extended Release Tablet (HPMC Matrix)",
            "Transdermal Patch (Reservoir)",
            "Biodegradable Microspheres",
            "Osmotic Pump Tablet",
            "Hydrogel Drug Delivery",
            "Biphasic Drug Delivery"
        ])
            
        if case == "Extended Release Tablet (HPMC Matrix)":
            st.markdown("""
            ### Extended Release Tablet with HPMC Matrix
            
            **System Description:**
            - Hydroxypropyl methylcellulose (HPMC) matrix
            - Combined diffusion and erosion mechanism
            - Typical for oral controlled release formulations
            
            **Key Mechanisms:**
            1. Initial surface release
            2. Gel layer formation
            3. Drug diffusion through gel layer
            4. Matrix erosion
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                drug_load = st.slider("Drug Load (mg)", 50, 200, 100)
                polymer_visc = st.slider("Polymer Viscosity Grade", 1, 5, 3)
            with col2:
                ph_medium = st.slider("Dissolution Medium pH", 1.0, 7.4, 6.8)
            
            # Simulate release profile
            time = np.linspace(0, 12, 100)
            # Adjust release parameters based on inputs
            k_diff = 0.3 / polymer_visc
            k_eros = 0.1 * (7.4/ph_medium)
            
            diff_component = first_order_release(time, k_diff, drug_load)
            eros_component = erosion_release(time, k_eros, drug_load)
            total_release = 0.7*diff_component + 0.3*eros_component
            
            fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Release Profile", "Release Rate"))
            
            # Release profile
            fig.add_trace(
                go.Scatter(x=time, y=total_release, name="Total Release"),
                row=1, col=1
            )
            
            # Release rate
            release_rate = np.gradient(total_release, time)
            fig.add_trace(
                go.Scatter(x=time, y=release_rate, name="Release Rate"),
                row=1, col=2
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig)
            
            st.markdown("""
            **Formulation Considerations:**
            - Higher viscosity grades lead to slower release
            - pH affects matrix erosion rate
            - Initial burst can be controlled by surface properties
            """)
            
        elif case == "Transdermal Patch (Reservoir)":
            st.markdown("""
            ### Transdermal Patch (Reservoir System)
            
            **System Components:**
            1. Drug reservoir
            2. Rate-controlling membrane
            3. Adhesive layer
            4. Backing layer
            
            **Release Mechanism:**
            - Primarily membrane-controlled diffusion
            - Follows zero-order kinetics when optimized
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                reservoir_conc = st.slider("Reservoir Concentration (mg/mL)", 10, 100, 50)
                membrane_thick = st.slider("Membrane Thickness (μm)", 10, 100, 50)
            with col2:
                diff_coeff = st.slider("Diffusion Coefficient (cm²/hr)", 1e-6, 1e-4, 1e-5, 1e-6)
                
            time = np.linspace(0, 72, 100)  # 72-hour patch
            
            # Calculate flux and cumulative release
            flux = (diff_coeff * reservoir_conc) / (membrane_thick * 1e-4)  # Steady-state flux
            cumulative = flux * time
            
            fig = make_subplots(rows=2, cols=1,
                            subplot_titles=("Drug Flux", "Cumulative Drug Delivery"))
            
            fig.add_trace(
                go.Scatter(x=time, y=[flux]*len(time), name="Flux (μg/cm²/hr)"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=time, y=cumulative, name="Cumulative Amount (μg/cm²)"),
                row=2, col=1
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig)

        elif case == "Biodegradable Microspheres":
            st.markdown("""
            ### Biodegradable PLGA Microspheres
            
            **System Description:**
            - Poly(lactic-co-glycolic acid) microspheres
            - Combined diffusion and degradation release
            - Common in long-acting injectables
            
            **Release Phases:**
            1. Initial burst
            2. Lag phase
            3. Secondary drug release
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                lactide_ratio = st.slider("Lactide:Glycolide Ratio", 50, 100, 75)
                particle_size = st.slider("Particle Size (μm)", 10, 100, 50)
            with col2:
                drug_loading = st.slider("Drug Loading (%)", 1, 20, 10)
                
            time = np.linspace(0, 30, 100)  # 30-day release
            
            # Adjust parameters based on inputs
            k1 = 0.5  # Initial burst
            k2 = 0.05 * (75/lactide_ratio)  # Slower release
            burst_fraction = 0.3 * (drug_loading/10)
            
            release = biphasic_release(time, k1, k2, 100, burst_fraction)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time, y=release, name="Cumulative Release"))
            
            fig.update_layout(
                title="PLGA Microsphere Release Profile",
                xaxis_title="Time (days)",
                yaxis_title="Cumulative Release (%)"
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Key Factors Affecting Release:**
            - Polymer composition (lactide:glycolide ratio)
            - Particle size distribution
            - Drug loading and distribution
            - Processing conditions
            """)

        elif case == "Osmotic Pump Tablet":
            st.markdown("""
            ### Osmotic Pump Tablet
            
            **System Components:**
            1. Semi-permeable membrane
            2. Osmotic core
            3. Delivery orifice
            
            **Release Mechanism:**
            - Water influx driven by osmotic pressure
            - Zero-order release kinetics
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                osmotic_pressure = st.slider("Osmotic Pressure (atm)", 5, 50, 20)
                orifice_size = st.slider("Orifice Size (μm)", 100, 1000, 500)
            with col2:
                membrane_perm = st.slider("Membrane Permeability", 1, 10, 5)
                
            time = np.linspace(0, 24, 100)
            
            # Calculate release profile
            k_osmotic = 0.1 * osmotic_pressure * membrane_perm * (orifice_size/500)
            release = zero_order_release(time, k_osmotic, 100)
            
            # Add some realistic variability
            release += np.random.normal(0, 0.5, len(time))
            release = np.clip(release, 0, 100)
            
            fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Release Profile", "Release Rate"))
            
            fig.add_trace(
                go.Scatter(x=time, y=release, name="Cumulative Release"),
                row=1, col=1
            )
            
            release_rate = np.gradient(release, time)
            fig.add_trace(
                go.Scatter(x=time, y=release_rate, name="Release Rate"),
                row=1, col=2
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig)

        elif case == "Hydrogel Drug Delivery":
            st.markdown("""
            ### Hydrogel Drug Delivery System
            
            **System Description:**
            - Crosslinked hydrophilic polymer network
            - Swelling-controlled release
            - Responsive to environmental conditions
            
            **Release Mechanisms:**
            1. Initial water uptake
            2. Gel swelling
            3. Drug diffusion through swollen network
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                crosslink_density = st.slider("Crosslink Density (%)", 1, 10, 5)
                temperature = st.slider("Temperature (°C)", 20, 40, 37)
            with col2:
                ph_value = st.slider("pH", 2.0, 8.0, 7.4)
                
            time = np.linspace(0, 12, 100)
            
            # Calculate swelling and release
            n = 0.5 + 0.1*(10-crosslink_density)  # Diffusional exponent
            k = 0.3 * (temperature/37) * (ph_value/7.4)
            
            release = korsmeyer_peppas(time, k, n, 100)
            swelling = 100 * (1 - np.exp(-0.2*time))
            
            fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Drug Release", "Hydrogel Swelling"))
            
            fig.add_trace(
                go.Scatter(x=time, y=release, name="Drug Release"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=time, y=swelling, name="Swelling (%)"),
                row=1, col=2
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig)

        elif case == "Biphasic Drug Delivery":
            st.markdown("""
            ### Biphasic Drug Delivery System
            
            **System Description:**
            - Two distinct release phases
            - Combines immediate and sustained release
            - Common in chronotherapy
            
            **Release Phases:**
            1. Initial rapid release
            2. Controlled secondary release
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                initial_fraction = st.slider("Initial Release Fraction", 0.2, 0.8, 0.4)
                k1 = st.slider("Initial Release Rate", 0.1, 2.0, 1.0)
            with col2:
                k2 = st.slider("Secondary Release Rate", 0.05, 0.5, 0.1)
                
            time = np.linspace(0, 24, 100)
            
            release = biphasic_release(time, k1, k2, 100, initial_fraction)
            
            # Separate phases for visualization
            phase1 = initial_fraction * 100 * (1 - np.exp(-k1*time))
            phase2 = (1-initial_fraction) * 100 * (1 - np.exp(-k2*time))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time, y=phase1, name="Initial Phase"))
            fig.add_trace(go.Scatter(x=time, y=phase2, name="Secondary Phase"))
            fig.add_trace(go.Scatter(x=time, y=release, name="Total Release"))
            
            fig.update_layout(
                title="Biphasic Release Profile",
                xaxis_title="Time (hours)",
                yaxis_title="Cumulative Release (%)"
            )
            st.plotly_chart(fig)
            
            # Calculate and display key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("1hr Release (%)", f"{release[4]:.1f}")
            with col2:
                st.metric("12hr Release (%)", f"{release[50]:.1f}")
            with col3:
                st.metric("24hr Release (%)", f"{release[-1]:.1f}")
if __name__ == "__main__":
    main()