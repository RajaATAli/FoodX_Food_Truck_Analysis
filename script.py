import googlemaps
import pandas as pd
import time
import os
import dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load .env file
dotenv.load_dotenv("APIKEY.env")

# Get API key from environment variable for security
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("API key not found in environment variable.")

# Initialize the client with your API key
gmaps = googlemaps.Client(key=API_KEY)

def get_food_trucks_data(query, location="Indiana, USA", max_results=50):
    try:
        results = gmaps.places(query=query, location=location, type='restaurant')
        food_trucks = results.get('results', [])

        while results.get('next_page_token') and len(food_trucks) < max_results:
            time.sleep(2)
            next_page_token = results['next_page_token']
            results = gmaps.places(query=query, location=location, type='restaurant', page_token=next_page_token)
            food_trucks.extend(results.get('results', []))
        
        # Trim the results to max_results
        food_trucks = food_trucks[:max_results]

        return food_trucks
    except Exception as e:
        logging.error(f"Error fetching food truck data: {e}")
        return []

# Implement ML method if have enough time - use labeled dataset to train a text classification model or use already trained model to predict cuisine based on restaurant name
def determine_cuisine(name):
    cuisines = {
        'Mexican': ['taco', 'mexican', 'burrito', 'quesadilla'],
        'BBQ': ['bbq', 'barbecue', 'ribs'],
        'Seafood': ['seafood', 'fish', 'lobster', 'shrimp'],
        'Pizza': ['pizza', 'pizzeria'],
        'Asian': ['asian', 'chinese', 'japanese', 'korean', 'thai'],
        'Indian': ['indian', 'curry', 'masala'],
        'Italian': ['italian', 'pasta', 'spaghetti']
    }
    
    for cuisine, keywords in cuisines.items():
        for keyword in keywords:
            if keyword.lower() in name.lower():
                return cuisine
    return "Unknown"

def get_opening_hours_and_website(place_id):
    try:
        place_details = gmaps.place(place_id=place_id)
        opening_hours = place_details.get('result', {}).get('opening_hours', {}).get('weekday_text', [])
        website = place_details.get('result', {}).get('website', 'null')
        return '\n'.join(opening_hours), website
    except Exception as e:
        logging.error(f"Error fetching details for place ID {place_id}: {e}")
        return "Unknown", "null"

def extract_food_truck_info(data):
    df = pd.DataFrame(data)
    
    # Check for duplicates
    df.drop_duplicates(subset='place_id', keep='first', inplace=True)
    
    df['Cuisine Type'] = df['name'].apply(determine_cuisine)
    
    df['Opening Hours'], df['website'] = zip(*df['place_id'].apply(get_opening_hours_and_website))
    
    columns = ['name', 'formatted_address', 'rating', 'website', 'Opening Hours', 'Cuisine Type']
    df_cleaned = df[columns]
    df_cleaned.columns = ['Name', 'Address', 'Rating', 'Website', 'Opening Hours', 'Cuisine Type']
    df_cleaned.to_csv('food_trucks.csv', index=False)
    logging.info("Data saved to food_trucks.csv")

if __name__ == "__main__":
    food_trucks_data = get_food_trucks_data(query="food trucks in Indiana")
    if food_trucks_data:
        extract_food_truck_info(food_trucks_data)