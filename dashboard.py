import streamlit as st
import pandas as pd
from cassandra.cluster import Cluster
import plotly.express as px
from datetime import datetime

# Connect to Cassandra (cached to avoid reconnecting multiple times)
@st.cache_resource
def init_connection():
    cluster = Cluster(['localhost'])
    session = cluster.connect('emotion_tracking')
    return session

session = init_connection()

# Fetch recent data
def get_recent_data(minutes=1):
    query = f"""
    SELECT * FROM emotion_data 
    WHERE timestamp > toTimestamp(now()) - {minutes}m 
    ALLOW FILTERING
    """
    rows = session.execute(query)
    return pd.DataFrame(list(rows))

# Streamlit dashboard
def create_dashboard():
    st.title("Emotion Detection Dashboard")

    # Add a button to refresh the data
    if st.sidebar.button("🔄 Refresh Data"):
        st.experimental_rerun()

    df = get_recent_data()

    # Display last update timestamp
    st.write(f"🕒 **Last updated:** {datetime.now().strftime('%H:%M:%S')}")

    if not df.empty:
        # Pie Chart (Emotion Distribution)
        emotion_counts = df['emotion'].value_counts()
        fig1 = px.pie(
            values=emotion_counts.values,
            names=emotion_counts.index,
            title='Emotion Distribution'
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Heatmap of face positions
        fig2 = px.scatter(
            df, x='bbox_x', y='bbox_y', color='emotion',
            title='Face Position Heat Map'
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Display statistics
        st.markdown(f"""
        **📊 Statistics:**
        - Total detections: `{len(df)}`
        - Dominant emotion: `{df['emotion'].mode()[0]}`
        - Average face width: `{df['bbox_width'].mean():.0f} px`
        - Average face height: `{df['bbox_height'].mean():.0f} px`
        """)

    else:
        st.warning("No data available in the last minute.")

if __name__ == "__main__":
    create_dashboard()
