# Google Maps Lead Getter

Fetch details about businesses from given location and save them into .CSV using Google Places API and Streamlit

## Prerequisites

- Python 3.x
- Google Places API Key

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install streamlit pandas requests python-dotenv folium streamlit-folium
```

3. Create a `.env` file in the root directory and add your Google Places API key:

```bash
GOOGLE_PLACES_API_KEY=your_api_key_here
```

## Running the Application

To run the application:

```bash
streamlit run main.py
```
or
```bash
python3 -m streamlit run main.py
```

## Features

- Search for places using text queries
- Set search radius using a slider
- Select location bias by clicking on an interactive map
- View results in a table format
- Export results to CSV
- Includes detailed information like:
  - Name
  - Address
  - Rating
  - Number of ratings
  - Phone number
  - Website
  - Location coordinates
  - Place types

## Usage

1. Enter your search query (e.g., "restaurants in New York")
2. Adjust the search radius using the slider
3. Click on the map to set the location bias
4. Click "Search" to get results
5. Download results as CSV using the download button

## Note

Make sure you have a valid Google Places API key with the following APIs enabled:
- Text Search API
- Text Search (New) API