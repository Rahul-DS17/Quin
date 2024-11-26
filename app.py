import streamlit as st
import pandas as pd
from PIL import Image
import re
import os
import time

# Constants
BASE_PATH = os.getcwd()
FAQ_FILE = os.path.join(BASE_PATH, "faq_streamlit_genai", "faq_sheet.csv")
LOGO_PATH = os.path.join(BASE_PATH, "Warner_Bros._Games_logo_(December_2023).svg.png")


# Functions
def add_logo(logo_path, width, height):
    """Load and resize a logo image."""
    try:
        logo = Image.open(logo_path)
        return logo.resize((width, height))
    except Exception as e:
        st.error(f"Error loading logo: {e}")
        return None

def add_plot(plot_path):
    """Load and return the plot image."""
    try:
        return Image.open(plot_path)
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading plot: {e}")
        return None

def load_dataframe(file_path):
    """Load a dataframe from a CSV file."""
    try:
        return pd.read_csv(file_path, encoding='latin1')
    except FileNotFoundError:
        st.error(f"Dataframe file not found at {file_path}.")
        return None
    except Exception as e:
        st.error(f"Error loading dataframe: {e}")
        return None

# Streamlit UI Setup
st.markdown(
    "<h1 style='color:Blue; text-align:center;'>Quick Insights on Gaming Data</h1>",
    unsafe_allow_html=True,
)

# Add Sidebar Logo
my_logo = add_logo(logo_path=LOGO_PATH, width=200, height=200)
if my_logo:
    st.sidebar.image(my_logo)

# Sidebar Radio Button
radio_choice = st.sidebar.radio(
    "Choose a flow",
    ["Insights Assistant"]
)

# Load FAQ Data
faq_df = load_dataframe(FAQ_FILE)

if faq_df is not None:
    # User Input for Query
    query = st.text_input("Enter your query (e.g., What is the MAU (Monthly Active Users) for 2024):")

    # Handle Query
    if query:
        with st.spinner("Analyzing your query..."):
            time.sleep(1)
        try:
            # Escape special characters for regex search
            escaped_query = re.escape(query)
            
            # Search for matching row in the DataFrame
            matched_rows = faq_df[faq_df["User Query"].str.contains(escaped_query, case=False, na=False)]
            
            if not matched_rows.empty:
                row = matched_rows.iloc[0]
                
                # Extract values from the matched row
                st.session_state.sql_query = row.get('SQL Query', '')
                df_path = str(row.get('Insights Dataframe', '')).replace('"', '').split("\\")[-1]
                plt_path = str(row.get('Modified Plot', '')).replace('"', '').split("\\")[-1]
                dataframe_path = os.path.join(BASE_PATH, "faq_streamlit_genai", "insights_data", df_path)
                insights = row.get('Modified Response', 'No insights available.')
                st.session_state.plot_path = os.path.join(BASE_PATH,  "faq_streamlit_genai", "plots", plt_path)
                
                with st.spinner("Generating insights..."):
                    time.sleep(1)
                    
                
                # Display DataFrame
                st.subheader("Dataframe")
                df = load_dataframe(dataframe_path)
                if df is not None:
                    st.dataframe(df)
                else:
                    st.warning("No dataframe available.")

                # Display Insights
                st.subheader("Insights")
                st.markdown(insights)
                # st.markdown("**\*Data Source:** Sample data", unsafe_allow_html=True)  # Footer note

                # Buttons for SQL Query and Plot
                if st.button("Show SQL Query"):
                    st.subheader("SQL Query")
                    st.code(st.session_state.sql_query if st.session_state.sql_query else "No SQL query available.")
                
                if st.button("Generate Plot"):
                    st.subheader("Visualization")
                    plot_image = add_plot(st.session_state.plot_path)
                    if plot_image:
                        st.image(st.session_state.plot_path, caption="Visualization", use_column_width=True)
                        st.markdown("**\*Data Source:** Sample data", unsafe_allow_html=True)  # Footer note
                    else:
                        st.warning("No visualization available.")
            else:
                st.error("No matching query found. Please try a different query.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    # else:
    #     st.info("Please enter a query to get insights.")
else:
    st.error("Failed to load the FAQ dataset. Please check the file path.")
