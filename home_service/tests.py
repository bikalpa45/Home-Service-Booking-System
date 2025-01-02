import math
import sqlite3
import heapq
import csv
import os
import requests

# Haversine formula to calculate distance between two points in kilometers
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    km = 6371 * c
    return km

# A* algorithm to find the shortest path
def a_star(start, goal, graph):
    open_list = []
    heapq.heappush(open_list, (0, start))
    
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = haversine(start[0], start[1], goal[0], goal[1])
    
    while open_list:
        _, current = heapq.heappop(open_list)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor, travel_cost in graph.get(current, {}).items():
            tentative_g_score = g_score[current] + travel_cost
            
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + haversine(neighbor[0], neighbor[1], goal[0], goal[1])
                
                if neighbor not in [i[1] for i in open_list]:
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
                    
    return None

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

# Retrieve customer and service IDs from the database
def set_ids_from_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM home_service_customer')
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT id FROM home_service_service_man')
    service_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    return customer_ids, service_ids

# Get coordinates (latitude and longitude) from the database for customers and service personnel
def get_coordinates_from_db(customer_ids, service_ids):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('SELECT id, latitude, longitude FROM home_service_customer WHERE id IN ({seq})'.format(
        seq=','.join(['?']*len(customer_ids))), customer_ids)
    customer_coords_dict = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    cursor.execute('SELECT id, latitude, longitude FROM home_service_service_man WHERE id IN ({seq})'.format(
        seq=','.join(['?']*len(service_ids))), service_ids)
    service_coords_dict = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

    conn.close()

    return customer_coords_dict, service_coords_dict

# Build graph structure with distances between customers and service personnel
def build_graph(customer_coords_dict, service_coords_dict):
    graph = {}
    for customer_id, (lat1, lon1) in customer_coords_dict.items():
        graph[(lat1, lon1)] = {}
        for service_id, (lat2, lon2) in service_coords_dict.items():
            distance = haversine(lat1, lon1, lat2, lon2)
            graph[(lat1, lon1)][(lat2, lon2)] = distance
    return graph

# Calculate distances using Google Maps Distance Matrix API
def calculate_absolute_distance(customer_location, service_location):
    api_key = 'YOUR_GOOGLE_MAPS_API_KEY'
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={customer_location[0]},{customer_location[1]}&destinations={service_location[0]},{service_location[1]}&mode=driving&units=metric&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        distance_text = data['rows'][0]['elements'][0]['distance']['text']
        distance_value = data['rows'][0]['elements'][0]['distance']['value']
        return distance_value / 1000  # Convert meters to kilometers
    else:
        print(f"Error fetching data from Google Maps API: {data['status']}")
        return None

# Calculate distances using Haversine and A* and export to CSV
def calculate_distances_and_export_to_csv():
    customer_ids, service_ids = set_ids_from_db()
    
    if not customer_ids or not service_ids:
        print("Error: Could not find valid IDs.")
        return

    customer_coords_dict, service_coords_dict = get_coordinates_from_db(customer_ids, service_ids)
    
    if not customer_coords_dict or not service_coords_dict:
        print("Error: Could not retrieve coordinates.")
        return

    graph = build_graph(customer_coords_dict, service_coords_dict)

    csv_filename = 'distances_with_astar_haversine_googlemaps.csv'
    csv_file_path = os.path.abspath(csv_filename)

    # Open CSV file for writing
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow([
            'Customer ID', 
            'Customer Latitude',
            'Customer Longitude',
            'Service ID',
            'Service Latitude',
            'Service Longitude',
            'Calculated Distance (A* + Haversine)',
            'Absolute Distance (Google Maps API)'
        ])
        
        # Iterate through customer-service pairs and calculate distances
        for customer_id, (customer_lat, customer_lon) in customer_coords_dict.items():
            customer_location = (customer_lat, customer_lon)
            
            for service_id, (service_lat, service_lon) in service_coords_dict.items():
                service_location = (service_lat, service_lon)

                # Haversine distance
                haversine_distance = haversine(customer_lat, customer_lon, service_lat, service_lon)
                
                # A* distance using the graph
                path = a_star(customer_location, service_location, graph)
                if path:
                    a_star_distance = sum(haversine(path[i][0], path[i][1], path[i+1][0], path[i+1][1]) for i in range(len(path)-1))
                else:
                    a_star_distance = None

                # Calculated distance: use either A* or Haversine (we will use Haversine if no path is found by A*)
                calculated_distance = a_star_distance if a_star_distance is not None else haversine_distance
                
                # Absolute distance using Google Maps API
                absolute_distance = calculate_absolute_distance(customer_location, service_location)

                # Write data to CSV
                writer.writerow([
                    customer_id, 
                    customer_lat, 
                    customer_lon, 
                    service_id, 
                    service_lat, 
                    service_lon, 
                    round(calculated_distance, 2) if calculated_distance else "No Path", 
                    round(absolute_distance, 2) if absolute_distance is not None else "API Error"
                ])
                
                # Print results to terminal (optional)
                print(f"Customer {customer_id}, Service {service_id}")
                print(f"Calculated Distance: {calculated_distance:.2f} km")
                print(f"Absolute Distance (Google Maps API): {absolute_distance:.2f} km" if absolute_distance else "API Error")
                if path:
                    print(f"A* Path: {path}")
                else:
                    print("No path found using A*")
                print()

    # Print CSV file location
    print(f"Data has been successfully written to '{csv_file_path}'.")

# Run the script to calculate distances
if __name__ == "__main__":
    calculate_distances_and_export_to_csv()
