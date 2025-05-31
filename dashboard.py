import streamlit as st
import pandas as pd
import subprocess

st.set_page_config(page_title="Creator Credibility Dashboard", layout="wide")

st.title("🔍 Media Creator Discovery Tool")
st.markdown("Enter your topic and keywords, then crawl YouTube creators and analyze engagement.")

# Inputs
query = st.text_input("Search Topic", value="personal finance")
keywords_input = st.text_input("Credibility Keywords (comma-separated)", value="money, investing, wealth")

if st.button("Run YouTube Crawler"):
    # Run your crawler script and wait for CSV
    with st.spinner("Crawling and analyzing creators..."):
        result = subprocess.run(["python", "youtube_crawler.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Crawl completed and CSV saved!")
        else:
            st.error("Something went wrong. Check the terminal.")
            st.text(result.stderr)

# Load and display CSV
try:
    df = pd.read_csv("youtube_creators.csv")
    st.dataframe(df)
except FileNotFoundError:
    st.info("Run the crawler to generate data.")
