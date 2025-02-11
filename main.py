import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import time  # Importing time module for waiting between paginated requests

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv("GOOGLE_PLACES_API_KEY")

# Set page config
st.set_page_config(page_title="Google Places Search", layout="wide")

# Add title and description
st.title("Google Places Text Search")
st.write("Search for places using the Google Places API and save the results as CSV")

# Display the API key status
if len(api_key) > 0:
    st.success("API Key loaded successfully.")
else:
    st.error("API Key not found. Please check your .env file.")

# Input field for the search query
search_query = st.text_input("Enter your search query (e.g., 'restaurants in New York')")

# Add slider for the search radius.
# This slider value will be used both in the API request and for drawing the circle overlay.
radius = st.slider("Search Radius (meters)", min_value=1000, max_value=50000, value=5000, step=1000)

# Define a default location (if no click has been made)
default_location = {"lat": 37.7937, "lng": -122.3965}  # Default to San Francisco

# Initialize session state with default location if not already set
if "lat" not in st.session_state:
    st.session_state["lat"] = default_location["lat"]
if "lng" not in st.session_state:
    st.session_state["lng"] = default_location["lng"]

st.subheader("Select Location Bias")

# Build a folium map centered at the last-clicked (or default) location.
m = folium.Map(location=[st.session_state["lat"], st.session_state["lng"]], zoom_start=11)
# Add a click popup so users can click on the map.
m.add_child(folium.LatLngPopup())

# Add a circle overlay centered at the location.
# Since you want the circle's diameter to equal the slider value,
# we use radius/2 for drawing the circle.
folium.Circle(
    location=[st.session_state["lat"], st.session_state["lng"]],
    radius=radius / 2,  # This gives a circle whose diameter equals the slider value
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.2
).add_to(m)

# Render the map. The returned data will contain click information from the user.
map_data = st_folium(m, height=300, width=700)

# If the user clicked on the map, update the session state with the new center.
if map_data and map_data.get("last_clicked"):
    st.session_state["lat"] = map_data["last_clicked"]["lat"]
    st.session_state["lng"] = map_data["last_clicked"]["lng"]

# Display the current latitude and longitude
st.write(f"Current Latitude: {st.session_state['lat']}, Current Longitude: {st.session_state['lng']}")

# If both the API key and search query are provided, process the search.
if api_key and search_query:
    center_lat = st.session_state["lat"]
    center_lng = st.session_state["lng"]
    st.write(f"Using location bias center at: ({center_lat}, {center_lng}) with radius: {radius} meters")
    
    # For the Google Places Text Search API, location bias is set using the 'location' and 'radius' parameters.
    params = {
        "query": search_query,
        "key": api_key,
        "location": f"{center_lat},{center_lng}",
        "radius": radius
    }
    
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    if st.button("Search"):
        try:
            response = requests.get(base_url, params=params)
            results = response.json()

            # Display JSON response from the API for the first page
            st.subheader("API Response")
            st.json(results)

            all_places = []
            if results.get("results"):
                # Extend the list with results from the first page.
                all_places.extend(results["results"])
                
                # Check for additional pages using next_page_token
                next_page_token = results.get("next_page_token")
                while next_page_token:
                    # Wait for the next_page_token to become active
                    time.sleep(2)
                    next_params = {
                        "pagetoken": next_page_token,
                        "key": api_key
                    }
                    response_page = requests.get(base_url, params=next_params)
                    results_page = response_page.json()
                    
                    if results_page.get("results"):
                        all_places.extend(results_page["results"])
                    
                    # Update next_page_token for any further pages, or exit the loop.
                    next_page_token = results_page.get("next_page_token")

                # Process each place and also retrieve additional details (phone number and website)
                places_data = []
                for place in all_places:
                    place_id = place.get("place_id", "")
                    
                    # Make a request to the Places Details API for phone number and website
                    details_params = {
                        "place_id": place_id,
                        "key": api_key,
                        "fields": "formatted_phone_number,website"
                    }
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_response = requests.get(details_url, params=details_params)
                    details_result = details_response.json().get("result", {})

                    place_info = {
                        "name": place.get("name", ""),
                        "address": place.get("formatted_address", ""),
                        "rating": place.get("rating", ""),
                        "user_ratings_total": place.get("user_ratings_total", ""),
                        "place_id": place_id,
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"],
                        "types": ", ".join(place.get("types", [])),
                        "phone_number": details_result.get("formatted_phone_number", ""),
                        "website": details_result.get("website", "")
                    }
                    places_data.append(place_info)

                df = pd.DataFrame(places_data)

                st.subheader("Results Table")
                st.dataframe(df)

                # Create a download button for CSV export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="places_results.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

else:
    st.warning("Please enter both an API key and a search query.")
