import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import lognorm
st.set_page_config(layout="wide")

def generate_particle_distribution(mean, std, n_particles=1000):
    """Generate lognormal particle size distribution"""
    return lognorm.rvs(s=std, scale=np.exp(mean), size=n_particles)

def plot_particle_distribution(sizes, title="Particle Size Distribution"):
    """Create histogram of particle sizes"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=sizes,
        nbinsx=30,
        name="Frequency",
        histnorm='probability'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Particle Size (μm)",
        yaxis_title="Frequency",
        showlegend=True
    )
    
    return fig

def calculate_dissolution_profile(sizes, time_points):
    """Calculate dissolution profile based on particle size distribution"""
    # Constants for Noyes-Whitney equation
    D = 1e-6  # Diffusion coefficient
    Cs = 1.0  # Saturation solubility
    h = 1e-3  # Diffusion layer thickness
    
    # Calculate surface area for each particle (assuming spherical particles)
    surface_areas = 4 * np.pi * (sizes/2)**2
    
    # Calculate dissolution rate for each particle
    dissolution_rates = (D * surface_areas * Cs) / (h * sizes)
    
    # Calculate cumulative dissolution over time
    dissolution_profile = []
    total_amount = len(sizes)
    
    for t in time_points:
        # Amount dissolved for each particle at time t
        dissolved = np.minimum(dissolution_rates * t, 1.0)
        total_dissolved = np.sum(dissolved) / total_amount * 100
        dissolution_profile.append(total_dissolved)
    
    return dissolution_profile

def plot_dissolution_comparison(particles):
    """Plot dissolution profiles"""
    time_points = np.linspace(0, 60, 100)  # 60 minute dissolution test
    
    # Calculate dissolution profile
    dissolution_profile = calculate_dissolution_profile(particles, time_points)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=dissolution_profile,
        mode='lines',
        name='Dissolution Profile'
    ))
    
    fig.update_layout(
        title="Predicted Dissolution Profile",
        xaxis_title="Time (minutes)",
        yaxis_title="Percent Dissolved (%)",
        showlegend=True,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def main():
    st.title("Particle Size Distribution in Pharmaceutical Formulations")
    
    # Main navigation
    page = st.radio("Select Topic", 
        ["Interactive Simulator", "Case Studies", "Quiz"], horizontal=True)
    
    if page == "Interactive Simulator":
        st.markdown("""
        ### Understanding Particle Size Distribution
        
        Particle size distribution is crucial in pharmaceutical formulations as it affects:
        - Dissolution rate
        - Bioavailability
        - Content uniformity
        - Flow properties
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            mean_size = st.slider("Mean Particle Size (μm)", 1.0, 100.0, 20.0, 0.5)
        with col2:
            std_dev = st.slider("Standard Deviation", 0.1, 1.0, 0.4, 0.1)
        
        # Generate and plot distribution
        particles = generate_particle_distribution(np.log(mean_size), std_dev)
        
                # Create tabs for different visualizations
        tab1, tab2 = st.tabs(["Size Distribution", "Dissolution Profile"])
        
        with tab1:
            st.plotly_chart(plot_particle_distribution(particles))
            
            # Display key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Median Size (μm)", f"{np.median(particles):.1f}")
            with col2:
                st.metric("D10 (μm)", f"{np.percentile(particles, 10):.1f}")
            with col3:
                st.metric("D90 (μm)", f"{np.percentile(particles, 90):.1f}")
        
        with tab2:
            st.markdown("""
            ### Dissolution Profile
            
            Based on the Noyes-Whitney equation:
            
            $\\frac{dC}{dt} = \\frac{DA(C_s - C)}{h}$
            
            The dissolution profile shows how quickly the drug dissolves over time.
            """)
            
            st.plotly_chart(plot_dissolution_comparison(particles))
            
            # Calculate and display dissolution metrics
            dissolution_profile = calculate_dissolution_profile(particles, [15, 30, 45])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("T15 (%)", f"{dissolution_profile[0]:.1f}")
            with col2:
                st.metric("T30 (%)", f"{dissolution_profile[1]:.1f}")
            with col3:
                st.metric("T45 (%)", f"{dissolution_profile[2]:.1f}")

        st.markdown("""
        ### Key Observations:
        - Smaller mean particle size leads to faster dissolution
        - Higher standard deviation means more variable dissolution rates
        - Initial dissolution rate is highly dependent on surface area
        """)

        st.plotly_chart(plot_particle_distribution(particles))
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Size (μm)", f"{np.median(particles):.1f}")
        with col2:
            st.metric("D10 (μm)", f"{np.percentile(particles, 10):.1f}")
        with col3:
            st.metric("D90 (μm)", f"{np.percentile(particles, 90):.1f}")
        
        st.markdown("""
        ### Effects on Dissolution
        
        The Noyes-Whitney equation shows that dissolution rate is inversely proportional 
        to particle size:
        
        $\\frac{dC}{dt} = \\frac{DA(C_s - C)}{h}$
        
        where:
        - D = diffusion coefficient
        - A = surface area (affected by particle size)
        - Cs = saturation solubility
        - C = concentration
        - h = diffusion layer thickness
        """)
        
        st.plotly_chart(plot_dissolution_comparison(np.linspace(1, 100, 100)))

    elif page == "Case Studies":
        drug = st.selectbox("Select Case Study", 
            ["Griseofulvin", "Ibuprofen", "Micronized vs Non-micronized"])
        
        if drug == "Griseofulvin":
            st.markdown("""
            ### Griseofulvin: Impact of Micronization
            
            Griseofulvin is a poorly soluble antifungal drug where particle size 
            significantly affects bioavailability.
            """)
            
            col1, col2 = st.columns(2)
            
            # Generate distributions for regular and micronized
            regular = generate_particle_distribution(np.log(50), 0.4)
            micronized = generate_particle_distribution(np.log(5), 0.3)
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Regular", "Micronized"))
            
            fig.add_trace(
                go.Histogram(x=regular, nbinsx=30, name="Regular"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Histogram(x=micronized, nbinsx=30, name="Micronized"),
                row=1, col=2
            )
            
            fig.update_layout(title="Comparison of Regular vs Micronized Griseofulvin")
            st.plotly_chart(fig)
            
            st.markdown("""
            **Clinical Implications:**
            - Micronized form shows 50% higher bioavailability
            - Faster onset of action
            - Lower dose required
            """)

        elif drug == "Ibuprofen":
            st.markdown("""
            ### Ibuprofen: Dissolution Rate Enhancement
            
            Ibuprofen's dissolution rate and absorption can be optimized through 
            particle size control.
            """)
            
            # Generate different grades
            fine = generate_particle_distribution(np.log(10), 0.3)
            coarse = generate_particle_distribution(np.log(50), 0.4)
            
            fig = make_subplots(rows=1, cols=2, 
                subplot_titles=("Fine Grade", "Coarse Grade"))
            
            fig.add_trace(
                go.Histogram(x=fine, nbinsx=30, name="Fine Grade"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Histogram(x=coarse, nbinsx=30, name="Coarse Grade"),
                row=1, col=2
            )
            
            fig.update_layout(title="Comparison of Ibuprofen Grades")
            st.plotly_chart(fig)
            
            st.markdown("""
            **Formulation Considerations:**
            - Fine grade for rapid release formulations
            - Coarse grade for controlled release
            - Impact on flow properties and compression
            """)

        elif drug == "Micronized vs Non-micronized":
            st.markdown("""
            ### Impact of Micronization on Drug Properties
            
            Micronization affects multiple aspects of drug behavior:
            """)
            
            # Create comparison visualization
            properties = ["Dissolution Rate", "Bioavailability", 
                        "Flow Properties", "Content Uniformity"]
            micronized = [80, 75, 40, 85]
            non_micronized = [30, 35, 70, 45]
            
            fig = go.Figure(data=[
                go.Bar(name="Micronized", x=properties, y=micronized),
                go.Bar(name="Non-micronized", x=properties, y=non_micronized)
            ])
            
            fig.update_layout(
                title="Property Comparison: Micronized vs Non-micronized",
                yaxis_title="Relative Performance (%)"
            )
            
            st.plotly_chart(fig)
            
            st.markdown("""
            **Key Considerations:**
            - Increased surface area improves dissolution
            - May require flow enhancers
            - Better content uniformity in low-dose formulations
            """)

    elif page == "Quiz":
        st.header("Test Your Understanding")
        
        # Question 1
        st.subheader("Question 1")
        quiz_answer_1 = st.radio(
            "How does reducing particle size affect drug dissolution rate?",
            (
                "Decreases dissolution rate due to particle aggregation",
                "Increases dissolution rate due to increased surface area"
            )
        )
        
        if quiz_answer_1 == "Increases dissolution rate due to increased surface area":
            st.success("Correct! Smaller particles have a larger surface area per unit mass, " 
                      "leading to faster dissolution.")
        else:
            st.error("Not quite. While aggregation can occur, the primary effect of " 
                    "reducing particle size is increased surface area and faster dissolution.")
        
        # Question 2
        st.subheader("Question 2")
        quiz_answer_2 = st.radio(
            "What parameter is most important in the Noyes-Whitney equation for particle size effects?",
            (
                "Surface area (A)",
                "Diffusion coefficient (D)",
                "Concentration gradient (Cs - C)"
            )
        )
        
        if quiz_answer_2 == "Surface area (A)":
            st.success("Correct! Surface area, which is directly affected by particle size, " 
                      "is the key parameter relating particle size to dissolution rate.")
        else:
            st.error("Not quite. While all parameters are important, surface area (A) is " 
                    "the parameter directly affected by particle size changes.")

if __name__ == "__main__":
    main()