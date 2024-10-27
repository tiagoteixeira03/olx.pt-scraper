import streamlit as st
import json 
import requests
from PIL import Image

# Create a title for the web app.
st.title("Olx.pt Marketplace Scraper")

# Take user input for the query and max price.
query = st.text_input("Query", "Macbook Pro")
max_price = st.text_input("Max Price", "1000")
num_pages = st.text_input("Number of pages", "1")

# Create a button to submit the form.
submit = st.button("Submit")

# If the button is clicked.
if submit:
    # TODO - Remove any commas from the max_price before sending the request.
    if "," in max_price:
        max_price = max_price.replace(",", "")
    else:
        pass
    res = requests.get(f"http://127.0.0.1:8000/crawl_olx?query={query}&max_price={max_price}&num_pages={num_pages}"
    )
    
    # Convert the response from json into a Python list.
    results = res.json()
    
    # Display the length of the results list.
    st.write(f"Number of results: {len(results)}")
    
    # Iterate over the results list to display each item.
    for item in results:
        st.header(item["title"])

        # Check if img_url is missing or points to OLX's default "no image" path
        img_url = item.get("image")
        if not img_url or 'no_thumbnail' in img_url:
            img_url = "placeholder.svg"  

        # Display image with valid URL or placeholder
        st.image(img_url, width=200)

        st.write(item["price"])
        st.write(item["location"])
        st.write(f"https://www.olx.pt{item['link']}")
        st.write("----")