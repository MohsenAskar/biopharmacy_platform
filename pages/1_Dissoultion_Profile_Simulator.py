import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set Streamlit page layout
st.set_page_config(layout="wide")

def main():
    st.title("Drug Dissolution Profile Simulator")
    st.write("Explore how different parameters affect drug dissolution kinetics")

    # Create sidebar for parameters
    st.sidebar.header("Dissolution Parameters")
    
    # Allow the user to enter either Half-life or Rate Constant
    half_life = st.sidebar.slider(
        "Half-life (T₁/₂) (hours)",
        min_value=0.1,
        max_value=10.0,
        value=2.0,
        step=0.1,
        help="Time required for 50% of the drug to dissolve"
    )
    
    # Compute k from half-life
    k = np.log(2) / half_life
    
    # Input parameters
    k = st.sidebar.slider(
        "Dissolution Rate Constant (k)",
        min_value=0.01,
        max_value=0.5,
        value=0.1,
        step=0.01,
        help="Higher values indicate faster dissolution"
    )
    
    initial_conc = st.sidebar.slider(
        "Initial Drug Amount (mg)",
        min_value=10,
        max_value=200,
        value=100,
        step=10,
        help="Total amount of drug in the formulation"
    )

    volume = st.sidebar.slider(
        "Dissolution Medium Volume (mL)",
        min_value=100,
        max_value=1000,
        value=500,
        step=50,
        help="Total volume in which the drug is dissolving"
    )

    # Time points for calculation
    time = np.linspace(0, 24, 100)
    
    # Calculate dissolution profiles
    concentration = initial_conc * (1 - np.exp(-k * time))
    percent_release = (concentration / initial_conc) * 100
    drug_conc_mL = concentration / volume  # Convert to mg/mL

    # Zero-Order Release Model
    zero_order_release = (initial_conc / max(time)) * time

    # Create interactive plot with Plotly
    fig = make_subplots(rows=1, cols=1)

    # First-order dissolution model
    fig.add_trace(
        go.Scatter(
            x=time,
            y=concentration,
            name="First-Order Drug Released (mg)",
            line=dict(color="#8884d8", width=2)
        )
    )

    # Zero-Order Model for comparison
    fig.add_trace(
        go.Scatter(
            x=time,
            y=zero_order_release,
            name="Zero-Order Release (mg)",
            line=dict(color="green", dash="dot")
        )
    )

    # Percent Release
    fig.add_trace(
        go.Scatter(
            x=time,
            y=percent_release,
            name="Percent Drug Released (%)",
            line=dict(color="orange")
        )
    )

    # Maximum drug release reference line
    fig.add_trace(
        go.Scatter(
            x=time,
            y=[initial_conc] * len(time),  
            name="Maximum Drug Release",
            line=dict(color="red", dash="dash")
        )
    )

    # Compute T50 and T90
    t_50 = -np.log(0.5) / k
    t_90 = -np.log(0.1) / k

    # Add annotations for key points
    fig.add_annotation(
        x=t_50, y=initial_conc * 0.5,
        text="T50",
        showarrow=True,
        arrowhead=2
    )

    fig.add_annotation(
        x=t_90, y=initial_conc * 0.9,
        text="T90",
        showarrow=True,
        arrowhead=2
    )

    # Update layout with interactive zoom buttons
    fig.update_layout(
        title="Drug Dissolution Profile",
        xaxis_title="Time (hours)",
        yaxis_title="Drug Released (mg)",
        hovermode='x unified',
        showlegend=True,
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=12, label="12h", step="hour", stepmode="backward"),
                    dict(count=24, label="1d", step="hour", stepmode="backward"),
                    dict(step="all")
                ]
            )
        )
    )

    # Log scale option for better visualization of slow dissolution
    if st.sidebar.checkbox("Use Log Scale for Dissolution"):
        fig.update_yaxes(type="log")

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanatory text
    st.markdown("""
    ### Understanding the Model
    
    This simulator uses a **first-order dissolution model**:
    
    $C(t) = C_0(1 - e^{-kt})$
    
    Where:
    - $C(t)$ is the amount of drug dissolved at time t
    - $C_0$ is the initial drug amount
    - $k$ is the dissolution rate constant
    - $t$ is time
    
    The **zero-order model** assumes a constant rate of release over time.
    """)

    # Add dissolution metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("T50 (hours)", f"{t_50:.2f}", 
                 help="Time to reach 50% dissolution")
    
    with col2:
        st.metric("T90 (hours)", f"{t_90:.2f}",
                 help="Time to reach 90% dissolution")
    
    with col3:
        initial_rate = k * initial_conc
        st.metric("Initial Rate (mg/hr)", f"{initial_rate:.2f}",
                 help="Initial dissolution rate")

    # Add interactive data table
    if st.checkbox("Show dissolution data table"):
        data_points = np.linspace(0, 24, 13)  # Every 2 hours
        data_conc = initial_conc * (1 - np.exp(-k * data_points))
        percent_release_data = (data_conc / initial_conc) * 100
        drug_conc_mL_data = data_conc / volume

        # Create data table
        data_table = {
            "Time (hours)": data_points,
            "Drug Released (mg)": data_conc,
            "Percent Released (%)": percent_release_data,
            "Concentration (mg/mL)": drug_conc_mL_data
        }
        
        st.dataframe(data_table)

if __name__ == "__main__":
    main()

    
    
    
