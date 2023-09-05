import json
import osmnx as ox
import requests
import numpy as np

GOOGLE_ELEVATION_API_ENDPOINT = "https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={YOUR_API_KEY}"

def calculate_angle(p0, p1, p2):
    a = np.array(p0)
    b = np.array(p1)
    c = np.array(p2)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Clamp the value to the domain of arccos
    cosine_angle = np.clip(cosine_angle, -1, 1)
    
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)

def get_elevation(lat, lon):
    url = GOOGLE_ELEVATION_API_ENDPOINT.format(lat=lat, lon=lon)

    response = requests.get(url, allow_redirects=True).json() 

    elevation = response['results'][0]['elevation']
    return elevation

def find_drifting_corners(location):
    G = ox.graph_from_address(location, dist=radius, network_type='drive')
     
    main_roads = ['primary', 'secondary', 'tertiary', 'trunk']
 
    main_edges = [(u, v, k, data) for u, v, k, data in G.edges(keys=True, data=True) if data['highway'] in main_roads]
 
    curvy_sequences = []
    
    count_with_geometry = 0

    visited_corners = set()
        
    for u, v, k, data in main_edges: 
        if 'geometry' in data:
            count_with_geometry += 1
            coords = list(data['geometry'].coords)
            for i in range(1, len(coords) - 1):
                p0 = coords[i-1]
                p1 = coords[i]
                p2 = coords[i+1]

                angle = calculate_angle(p0, p1, p2)
                
                if 40 <= angle <= 140 and p1 not in visited_corners:
                    visited_corners.add(p1)
                    curvy_sequences.append((v, p1[::-1], angle))

    best_curves = sorted(curvy_sequences, key=lambda x: x[2], reverse=True)[:count]
    
    print(f"Edges with geometry: {count_with_geometry}")
    print(f"Identified curves: {len(curvy_sequences)}")
     
    return [(curve[0], curve[1]) for curve in best_curves], G

def generate_google_maps_url(lat, lon):
    return f"https://www.google.com/maps/?q={lat},{lon}"

if __name__ == '__main__':
    location = input("Please insert a location: ")
    radius = int(input("Please insert radius size (in meters): "))
    count = int(input("How many corners would you like to find: "))
    print("This may take a while...")
    
    corners, G = find_drifting_corners(location)

    print("Top " + str(count) + " drifting corners near", location)
    for node, (lat, lon) in corners:
        print(generate_google_maps_url(lat, lon))
  
    input("")
