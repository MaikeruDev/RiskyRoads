import json
import osmnx as ox
import requests

GOOGLE_ELEVATION_API_ENDPOINT = "https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={YOUR_API_KEY}"

def get_elevation(lat, lon):
    url = GOOGLE_ELEVATION_API_ENDPOINT.format(lat=lat, lon=lon)

    response = requests.get(url, allow_redirects=True).json() 

    elevation = response['results'][0]['elevation']
    return elevation

def find_drifting_corners(location):
    G = ox.graph_from_address(location, dist=radius, network_type='drive')  # Increased distance to 5km for broader search

    non_roundabouts = [x for x, y in G.nodes(data=True) if y.get('highway') != 'roundabout']

    mountain_nodes = [node for node in non_roundabouts if get_elevation(G.nodes[node]['y'], G.nodes[node]['x']) > min_elevation_threshold]

    best_corners = mountain_nodes[:count]
    
    return best_corners, G

def generate_google_maps_url(lat, lon):
    return f"https://www.google.com/maps/?q={lat},{lon}"

if __name__ == '__main__':
    location = input("Please insert a location: ")
    radius = int(input("Please insert radius size (in meters): "))
    count = int(input("How many corners would you like to find: "))
    print("This may take a while...")
    
    corners, G = find_drifting_corners(location)
    
    print("Top " + str(count) + " drifting corners near", location)
    for corner in corners:
        lat, lon = G.nodes[corner]['y'], G.nodes[corner]['x']
        print(generate_google_maps_url(lat, lon))

    input("")
