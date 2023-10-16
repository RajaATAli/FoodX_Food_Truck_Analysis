import googlemaps
import pandas as pd
import time
import os
import dotenv

# Load .env file
dotenv.load_dotenv("APIKEY.env")

# Get API key from environment variable for security
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("API key not found in environment variable.")

# Initialize the client with your API key
gmaps = googlemaps.Client(key=API_KEY)

def get_food_trucks_data(query, location="Indiana, USA", max_results=2):
    try:
        results = gmaps.places(query=query, location=location, type='restaurant')
        food_trucks = results.get('results', [])

        while results.get('next_page_token') and len(food_trucks) < max_results:
            time.sleep(2)
            next_page_token = results['next_page_token']
            results = gmaps.places(query=query, location=location, type='restaurant', page_token=next_page_token)
            food_trucks.extend(results.get('results', []))

        return food_trucks
    except Exception as e:
        print(f"Error fetching food truck data: {e}")
        return []

def determine_cuisine(name):
    cuisines = {
        'Mexican': ['taco', 'mexican', 'burrito', 'quesadilla'],
        'BBQ': ['bbq', 'barbecue', 'ribs'],
        'Seafood': ['seafood', 'fish', 'lobster', 'shrimp'],
        'Pizza': ['pizza', 'pizzeria'],
    }
    
    for cuisine, keywords in cuisines.items():
        for keyword in keywords:
            if keyword.lower() in name.lower():
                return cuisine
    return "Unknown"

def get_opening_hours(place_id):
    try:
        place_details = gmaps.place(place_id=place_id)
        opening_hours = place_details.get('result', {}).get('opening_hours', {}).get('weekday_text', [])
        return '\n'.join(opening_hours)
    except Exception as e:
        print(f"Error fetching opening hours for place ID {place_id}: {e}")
        return "Unknown"

def extract_food_truck_info(data):
    df = pd.DataFrame(data)
    df['Cuisine Type'] = df['name'].apply(determine_cuisine)
    if 'website' not in df.columns:
        df['website'] = 'null'
    else:
        df['website'].fillna('null', inplace=True)
    df['Opening Hours'] = df['place_id'].apply(get_opening_hours)
    columns = ['name', 'formatted_address', 'rating', 'website', 'Opening Hours', 'Cuisine Type']
    df_cleaned = df[columns]
    df_cleaned.columns = ['Name', 'Address', 'Rating', 'Website', 'Opening Hours', 'Cuisine Type']
    df_cleaned.to_csv('food_trucks.csv', index=False)
    print("Data saved to food_trucks.csv")

if __name__ == "__main__":
    food_trucks_data = get_food_trucks_data(query="food trucks in Indiana")
    if food_trucks_data:
        extract_food_truck_info(food_trucks_data)


