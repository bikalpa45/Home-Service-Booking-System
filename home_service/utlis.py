import math
import sqlite3
import heapq

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    km = 6371 * c
    return km

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

def set_ids_from_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM home_service_customer')
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT id FROM home_service_service_man')
    service_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    return customer_ids, service_ids

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

def build_graph(customer_coords_dict, service_coords_dict):
    graph = {}
    for customer_id, (lat1, lon1) in customer_coords_dict.items():
        graph[(lat1, lon1)] = {}
        for service_id, (lat2, lon2) in service_coords_dict.items():
            distance = haversine(lat1, lon1, lat2, lon2)
            graph[(lat1, lon1)][(lat2, lon2)] = distance
    return graph

def calculate_distances():
    customer_ids, service_ids = set_ids_from_db()
    
    if not customer_ids or not service_ids:
        print("Error: Could not find valid IDs.")
        return

    customer_coords_dict, service_coords_dict = get_coordinates_from_db(customer_ids, service_ids)
    
    if not customer_coords_dict or not service_coords_dict:
        print("Error: Could not retrieve coordinates.")
        return

    graph = build_graph(customer_coords_dict, service_coords_dict)
    
    for customer_id, (customer_lat, customer_lon) in customer_coords_dict.items():
        customer_location = (customer_lat, customer_lon)
        nearest_service = None
        shortest_path = None
        shortest_distance = float('inf')
        
        for service_id, (service_lat, service_lon) in service_coords_dict.items():
            service_location = (service_lat, service_lon)
            path = a_star(customer_location, service_location, graph)
            
            if path:
                distance = sum(haversine(path[i][0], path[i][1], path[i+1][0], path[i+1][1]) for i in range(len(path)-1))
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_service = service_id
                    shortest_path = path
        
        if nearest_service is not None:
            print(f"Customer {customer_id}'s nearest service provider is Service {nearest_service} with a distance of {shortest_distance:.2f} km.")
            print(f"Path: {shortest_path}")
        else:
            print(f"No path found for Customer {customer_id}")

# if __name__ == "__main__":
#     calculate_distances()
