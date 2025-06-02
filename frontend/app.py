import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import scrape_maps  #  Import function from backend/main.py(backend not locating that why use import sys)
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Google Maps Scraper", layout="centered")

st.title("Google Maps Scraper")

query = st.text_input("enter value to scrape details","company")
max_results = st.slider("Number of results", 5, 100, 25)
button=st.button("Start Scraping")
if button:
    with st.spinner("Scraping in progress..."):
        try:
            pd = scrape_maps(query, max_results)
            st.success("Scraping complete!")
            st.dataframe(pd)

            # for download
            csv = pd.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "results.csv", "text/csv")

        except Exception as e:
            st.error(f"An error occurred: {e}")
