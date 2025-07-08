import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Home Energy Calculator",
    page_icon="⚡",
    layout="wide"
)

# Title and header
st.title("⚡ Home Energy Usage Calculator")
st.markdown("Calculate your daily energy consumption based on your home appliances")

# Sidebar for basic information
st.sidebar.header("📋 Basic Information")
name = st.sidebar.text_input("Enter your name:", placeholder="John Doe")
age = st.sidebar.number_input("Enter your age:", min_value=1, max_value=120, value=25)
area = st.sidebar.text_input("Enter your area:", placeholder="Downtown")
city = st.sidebar.text_input("Enter your city:", placeholder="Mumbai")


# Home details
st.sidebar.header("🏠 Home Details")
home_type = st.sidebar.selectbox("Choose type of House:", ["Flat", "Tenament"])
room_type = st.sidebar.selectbox("Choose room type:", ["1BHK", "2BHK", "3BHK"])

# Set fans and lights based on room type
fans_lights_config = {
    "1BHK": {"fans": 2, "lights": 2},
    "2BHK": {"fans": 3, "lights": 3},
    "3BHK": {"fans": 4, "lights": 4}
}

fans = fans_lights_config[room_type]["fans"]
lights = fans_lights_config[room_type]["lights"]

# Display configuration
st.sidebar.markdown("### 💡 Your Configuration:")
st.sidebar.write(f"**Fans:** {fans}")
st.sidebar.write(f"**Lights:** {lights}")

# Main content area
if name:
    st.header(f"Welcome {name}! 👋")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📅 Daily Input", "📊 Summary", "📈 Analytics"])
    
    with tab1:
        st.subheader("Enter your daily appliance usage")
        
        # Initialize session state for storing daily data
        if 'daily_data' not in st.session_state:
            st.session_state.daily_data = {}
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        for i, day in enumerate(days):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"### {day}")
                
                # Create a container for each day
                with st.container():
                    # Base energy calculation (fans + lights)
                    base_energy = (fans * 0.4) + (lights * 0.8)
                    
                    # AC usage
                    ac_usage = st.checkbox(f"Do you use AC on {day}?", key=f"ac_{day}")
                    ac_count = 0
                    if ac_usage:
                        ac_count = st.number_input(f"How many ACs?", min_value=1, max_value=5, value=1, key=f"ac_count_{day}")
                    
                    # Fridge usage
                    fridge_usage = st.checkbox(f"Do you use fridge on {day}?", key=f"fridge_{day}")
                    
                    # Washing machine usage
                    washing_usage = st.checkbox(f"Do you use washing machine on {day}?", key=f"washing_{day}")
                    
                    # Calculate total energy
                    total_energy = base_energy
                    if ac_usage:
                        total_energy += ac_count * 3
                    if fridge_usage:
                        total_energy += 4
                    if washing_usage:
                        total_energy += 2
                    
                    # Store data in session state
                    st.session_state.daily_data[day] = {
                        'base_energy': base_energy,
                        'ac_usage': ac_usage,
                        'ac_count': ac_count,
                        'fridge_usage': fridge_usage,
                        'washing_usage': washing_usage,
                        'total_energy': total_energy
                    }
                    
                    # Display energy usage
                    st.metric(f"Daily Energy Usage", f"{total_energy:.1f} kWh")
                    
                    st.markdown("---")
    
    with tab2:
        st.subheader("📊 Weekly Energy Summary")
        
        if st.session_state.daily_data:
            # Create summary dataframe
            summary_data = []
            for day, data in st.session_state.daily_data.items():
                summary_data.append({
                    'Day': day,
                    'Base (Fans + Lights)': data['base_energy'],
                    'AC': data['ac_count'] * 3 if data['ac_usage'] else 0,
                    'Fridge': 4 if data['fridge_usage'] else 0,
                    'Washing Machine': 2 if data['washing_usage'] else 0,
                    'Total Energy (kWh)': data['total_energy']
                })
            
            df = pd.DataFrame(summary_data)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_weekly = df['Total Energy (kWh)'].sum()
                st.metric("Weekly Total", f"{total_weekly:.1f} kWh")
            
            with col2:
                avg_daily = df['Total Energy (kWh)'].mean()
                st.metric("Daily Average", f"{avg_daily:.1f} kWh")
            
            with col3:
                max_day = df.loc[df['Total Energy (kWh)'].idxmax(), 'Day']
                max_usage = df['Total Energy (kWh)'].max()
                st.metric("Peak Day", f"{max_day}", f"{max_usage:.1f} kWh")
            
            with col4:
                # Estimated monthly cost (assuming ₹5 per kWh)
                monthly_cost = total_weekly * 4.33 * 5
                st.metric("Est. Monthly Cost", f"₹{monthly_cost:.0f}")
            
            # Display detailed table
            st.subheader("Detailed Breakdown")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Please fill in the daily usage data in the 'Daily Input' tab first.")
    
    with tab3:
        st.subheader("📈 Energy Analytics")
        
        if st.session_state.daily_data:
            # Create charts
            df = pd.DataFrame([
                {
                    'Day': day,
                    'Base Energy': data['base_energy'],
                    'AC Energy': data['ac_count'] * 3 if data['ac_usage'] else 0,
                    'Fridge Energy': 4 if data['fridge_usage'] else 0,
                    'Washing Machine Energy': 2 if data['washing_usage'] else 0,
                    'Total Energy': data['total_energy']
                }
                for day, data in st.session_state.daily_data.items()
            ])
            
            # Line chart for daily energy usage
            fig_line = px.line(df, x='Day', y='Total Energy', 
                              title='Daily Energy Consumption Trend',
                              markers=True)
            fig_line.update_layout(xaxis_title="Day", yaxis_title="Energy (kWh)")
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Stacked bar chart for energy breakdown
            fig_bar = go.Figure(data=[
                go.Bar(name='Base (Fans + Lights)', x=df['Day'], y=df['Base Energy']),
                go.Bar(name='AC', x=df['Day'], y=df['AC Energy']),
                go.Bar(name='Fridge', x=df['Day'], y=df['Fridge Energy']),
                go.Bar(name='Washing Machine', x=df['Day'], y=df['Washing Machine Energy'])
            ])
            fig_bar.update_layout(
                barmode='stack',
                title='Energy Consumption Breakdown by Appliance',
                xaxis_title="Day",
                yaxis_title="Energy (kWh)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Pie chart for total weekly energy distribution
            weekly_totals = {
                'Base (Fans + Lights)': df['Base Energy'].sum(),
                'AC': df['AC Energy'].sum(),
                'Fridge': df['Fridge Energy'].sum(),
                'Washing Machine': df['Washing Machine Energy'].sum()
            }
            
            fig_pie = px.pie(
                values=list(weekly_totals.values()),
                names=list(weekly_totals.keys()),
                title='Weekly Energy Distribution by Appliance Type'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Energy saving tips
            st.subheader("💡 Energy Saving Tips")
            
            # Calculate potential savings
            ac_energy = df['AC Energy'].sum()
            if ac_energy > 0:
                st.info(f"🌡️ **AC Usage:** You're using {ac_energy:.1f} kWh/week on AC. Try setting temperature to 24°C to save up to 20% energy.")
            
            if df['Fridge Energy'].sum() > 0:
                st.info("❄️ **Fridge Usage:** Keep your fridge at optimal temperature (3-4°C) and avoid frequent opening to save energy.")
            
            if df['Washing Machine Energy'].sum() > 0:
                st.info("👕 **Washing Machine:** Use cold water for washing when possible - it can save up to 90% of energy used for heating water.")
            
            high_usage_days = df[df['Total Energy'] > df['Total Energy'].mean()]['Day'].tolist()
            if high_usage_days:
                st.warning(f"⚠️ **High Usage Days:** {', '.join(high_usage_days)} show higher than average consumption. Consider reducing appliance usage on these days.")
        
        else:
            st.info("Please fill in the daily usage data in the 'Daily Input' tab first.")

else:
    st.info("👈 Please enter your name in the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown("**Note:** Energy consumption values are estimates based on typical appliance ratings. Actual consumption may vary based on appliance efficiency, usage patterns, and local conditions.")