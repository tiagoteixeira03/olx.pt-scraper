# Description: This file contains the code for Olx.pt Marketplace Scraper API.
# Usage: python app.py

# Import the necessary libraries.

# Playwright is used to crawl the Facebook Marketplace.
from playwright.sync_api import sync_playwright
# The time library is used to add a delay to the script.
import time
# The BeautifulSoup library is used to parse the HTML.
from bs4 import BeautifulSoup
# The FastAPI library is used to create the API.
from fastapi import HTTPException, FastAPI
# The uvicorn library is used to run the API.
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
                 
# Create an instance of the FastAPI class.
app = FastAPI()
# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Create a route to the root endpoint.
@app.get("/")
# Define a function to be executed when the endpoint is called.
def root():
    # Return a message.
    return {"message": "Welcome to the Olx.pt Marketplace Scrapper API."}

# Create a route to the return_data endpoint.
@app.get("/crawl_olx")
def crawl_olx(query: str, max_price: int, num_pages: int):
    parsed = []
    
    # Initialize the session using Playwright outside the loop
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        for page_nr in range(1, num_pages + 1):  # Loop through pages
            print(f"Scraping page: {page_nr}")
            
            # Define the URL for the current page
            marketplace_url = f'https://www.olx.pt/ads/q-{query}/?page={page_nr}&search%5Bfilter_float_price%3Ato%5D={max_price}'
            
            # Open a new page for each URL
            page = browser.new_page()
            page.goto(marketplace_url)
            time.sleep(2)  # Allow time for the page to load

            # Scroll to the bottom of the page to ensure all elements are loaded
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the lazy-loaded content

            # Get the HTML content and parse it
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all listings on the current page
            listings = soup.find_all('div', class_='css-1sw7q4x')
            for listing in listings:
                try:
                    # Get data from each listing
                    image = listing.find('img', class_='css-8wsg1m')['src'] if listing.find('img', class_='css-8wsg1m') else None
                    title = listing.find('h6', class_='css-1wxaaza').text if listing.find('h6', class_='css-1wxaaza') else None
                    price = listing.find('p', class_='css-13afqrm').text if listing.find('p', class_='css-13afqrm') else None
                    post_url = listing.find('a', class_='css-z3gu2d')['href'] if listing.find('a', class_='css-z3gu2d') else None
                    location_date = listing.find('p', class_='css-1mwdrlh').text if listing.find('p', class_='css-1mwdrlh') else None
                    
                    # Append the parsed data to the list
                    parsed.append({
                        'image': image,
                        'title': title,
                        'price': price,
                        'post_url': post_url,
                        'location_date': location_date
                    })
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    pass

            # Close the page after scraping its content
            page.close()
        
        # Close the browser after all pages are scraped
        browser.close()
    
    # Format the parsed data for output
    result = []
    for item in parsed:
        result.append({
            'name': item.get('title'),
            'price': item.get('price'),
            'location': item.get('location_date'),
            'title': item.get('title'),
            'image': item.get('image'),
            'link': item.get('post_url')
        })
    return result

# Create a route to the return_html endpoint.
@app.get("/return_ip_information")
# Define a function to be executed when the endpoint is called.
def return_ip_information():
    # Initialize the session using Playwright.
    with sync_playwright() as p:
        # Open a new browser page.
        browser = p.chromium.launch()
        page = browser.new_page()
        # Navigate to the URL.
        page.goto('https://www.ipburger.com/')
        # Wait for the page to load.
        time.sleep(5)
        # Get the HTML content of the page.
        html = page.content()
        # Beautify the HTML content.
        soup = BeautifulSoup(html, 'html.parser')
        # Find the IP address.
        ip_address = soup.find('span', id='ipaddress1').text
        # Find the country.
        country = soup.find('strong', id='country_fullname').text
        # Find the location.
        location = soup.find('strong', id='location').text
        # Find the ISP.
        isp = soup.find('strong', id='isp').text
        # Find the Hostname.
        hostname = soup.find('strong', id='hostname').text
        # Find the Type.
        ip_type = soup.find('strong', id='ip_type').text
        # Find the version.
        version = soup.find('strong', id='version').text
        # Close the browser.
        browser.close()
        # Return the IP information as JSON.
        return {
            'ip_address': ip_address,
            'country': country,
            'location': location,
            'isp': isp,
            'hostname': hostname,
            'type': ip_type,
            'version': version
        }

if __name__ == "__main__":

    # Run the app.
    uvicorn.run(
        # Specify the app as the FastAPI app.
        'app:app',
        host='127.0.0.1',
        port=8000
    )
