import os
import sys

# Ensure the root directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual Streamlit UI module
# This will execute the top-level st.set_page_config calls
import ui.streamlit_app

# Run the main Streamlit application
if __name__ == "__main__":
    ui.streamlit_app.main()
