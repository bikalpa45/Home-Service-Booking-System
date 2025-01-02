import math
from django.db.models import Avg, F, ExpressionWrapper, fields
from django.utils import timezone
from .models import Order, Service_Man, Customer

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance

def calculate_system_metrics():
    # Calculate average response time
    avg_response_time = Order.objects.annotate(
        response_time=ExpressionWrapper(
            F('start_time') - F('book_date'),
            output_field=fields.DurationField()
        )
    ).aggregate(avg_response_time=Avg('response_time'))['avg_response_time']

    # Calculate service completion rate
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status__status='Completed').count()
    completion_rate = completed_orders / total_orders if total_orders > 0 else 0

    # Calculate average distance between service man and customer
    orders_with_distance = []
    for order in Order.objects.all():
        distance = haversine_distance(
            order.customer.latitude, order.customer.longitude,
            order.service.latitude, order.service.longitude
        )
        orders_with_distance.append(distance)
    
    avg_distance = sum(orders_with_distance) / len(orders_with_distance) if orders_with_distance else 0

    return {
        'avg_response_time': avg_response_time,
        'completion_rate': completion_rate,
        'avg_distance': avg_distance
    }

def calculate_algorithm_accuracy():
    # Assuming you have a way to store the predicted route and actual route taken
    # You'll need to modify your Order model to include these fields
    orders = Order.objects.filter(status__status='Completed')
    
    total_deviation = 0
    for order in orders:
        predicted_distance = haversine_distance(
            order.customer.latitude, order.customer.longitude,
            order.service.latitude, order.service.longitude
        )
        # Actual distance should be stored when the service is completed
        actual_distance = order.actual_distance  # You need to add this field to your Order model
        
        deviation = abs(predicted_distance - actual_distance) / actual_distance
        total_deviation += deviation
    
    accuracy = 1 - (total_deviation / len(orders)) if len(orders) > 0 else 0
    return accuracy

def generate_report():
    metrics = calculate_system_metrics()
    algorithm_accuracy = calculate_algorithm_accuracy()
    
    report = f"""
    System Performance Report
    -------------------------
    Average Response Time: {metrics['avg_response_time']}
    Service Completion Rate: {metrics['completion_rate']:.2%}
    Average Distance between Service Provider and Customer: {metrics['avg_distance']:.2f} km
    
    Algorithm Accuracy: {algorithm_accuracy:.2%}
    """
    
    return report

# You can call this function periodically or on-demand to generate the report
print(generate_report())