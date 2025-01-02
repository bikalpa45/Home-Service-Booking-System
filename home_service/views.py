from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate,login,logout
import datetime
from django.db.models import Q
from django.shortcuts import render
from .utlis import get_coordinates_from_db, set_ids_from_db,calculate_distances,haversine, a_star, build_graph
from django.http import JsonResponse
from .models import City, Service_Category, Service_Man, Customer,User


# Create your views here.
def notification():
    status = Status.objects.get(status='pending')
    new = Service_Man.objects.filter(status=status)
    count=0
    for i in new:
        count+=1
    d = {'count':count,'new':new}
    return d
def Home(request):
    user=""
    error=""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser1 = Service_Man.objects.all()
    ser = Service_Category.objects.all()
    for i in ser:
        count=0
        for j in ser1:
            if i.category==j.service_name:
                count+=1
        i.total = count
        i.save()
    d = {'error': error, 'ser': ser}
    return render(request,'home.html',d)

def contact(request):
    error=False
    if request.method=="POST":
        n = request.POST['name']
        e = request.POST['email']
        m = request.POST['message']
        status = Status.objects.get(status="unread")
        Contact.objects.create(status=status,name=n,email=e,message1=m)
        error=True
    d = {'error':error}
    return render(request,'contact.html',d)

def Admin_Home(request):
    dic = notification()
    cus = Customer.objects.all()
    ser = Service_Man.objects.all()
    cat = Service_Category.objects.all()
    count1=0
    count2=0
    count3=0
    for i in cus:
        count1+=1
    for i in ser:
        count2+=1
    for i in cat:
        count3+=1
    d = {'new':dic['new'],'count':dic['count'],'customer':count1,'service_man':count2,'service':count3}
    return render(request,'admin_home.html',d)

def about(request):
    return render(request,'about.html')

def Login_User(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if user:
            try:
                sign = Customer.objects.get(user=user)
            except:
                pass
            if sign:
                login(request, user)
                error = "pat1"
            else:
                stat = Status.objects.get(status="Accept")
                pure=False
                try:
                    pure = Service_Man.objects.get(status=stat,user=user)
                except:
                    pass
                if pure:
                    login(request, user)
                    error = "pat2"
                else:
                    login(request, user)
                    error="notmember"

        else:
            error="not"
    d = {'error': error}
    return render(request, 'login.html', d)

def Login_admin(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        if user.is_staff:
            login(request, user)
            error="pat"
        else:
            error="not"
    d = {'error': error}
    return render(request, 'admin_login.html', d)

def check_username_email(request):
    uname = request.POST.get('uname')
    email = request.POST.get('email')
    
    duplicate_username = User.objects.filter(username=uname).exists()
    duplicate_email = User.objects.filter(email=email).exists()

    if duplicate_username:
        return JsonResponse({'duplicate': True, 'message': 'Username already exists!'})
    elif duplicate_email:
        return JsonResponse({'duplicate': True, 'message': 'Email already exists!'})
    else:
        return JsonResponse({'duplicate': False})


def Signup_User(request):
    errors = {}
    success = ""
    
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        cp = request.POST['cpwd']
        con = request.POST['contact']
        add = request.POST['address']
        type = request.POST['type']
        im = request.FILES['image']
        lat = request.POST['latitude']
        long = request.POST['longitude']
        dat = datetime.date.today()

        # Check for password match
        if p != cp:
            errors['password'] = "Passwords do not match!"

        # Check for duplicate username or email
        duplicate_username = User.objects.filter(username=u).exists()
        duplicate_email = User.objects.filter(email=e).exists()

        if duplicate_username:
            errors['uname'] = "Username already exists!"
        if duplicate_email:
            errors['email'] = "Email already exists!"

        # Proceed if there are no errors
        if not errors:
            user = User.objects.create_user(email=e, username=u, password=p, first_name=f, last_name=l)
            
            if type == "customer":
                Customer.objects.create(user=user, contact=con, address=add, image=im, latitude=lat, longitude=long)
            else:
                stat = Status.objects.get(status='pending')
                Service_Man.objects.create(doj=dat, image=im, user=user, contact=con, address=add, status=stat, latitude=lat, longitude=long)

            success = "Account created successfully!"
    
    d = {'errors': errors, 'success': success}
    return render(request, 'signup.html', d)





def User_home(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        pass
    d = {'error':error}
    return render(request,'user_home.html',d)

def Service_home(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    d = {'error':error,'terro':terro}
    return render(request,'service_home.html',d)

def Service_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    terro=""
    if None == sign.service_name:
        terro = "message"
    else:
        if sign.status.status == "pending":
            terro="message1"
    order = Order.objects.filter(service=sign)
    d = {'error':error,'terro':terro,'order':order}
    return render(request,'service_order.html',d)

def Admin_Order(request):
    dic = notification()
    order = Order.objects.all()
    d = {'order':order,'new': dic['new'], 'count': dic['count']}
    return render(request,'admin_order.html',d)

def Customer_Order(request):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.filter(customer=sign)
    d = {'error':error,'order':order}
    return render(request,'customer_order.html',d)


def Customer_Booking(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    user = User.objects.get(id=request.user.id)
    error = ""
    conflict = False
    conflict_times = []  # To store the time range of conflicting bookings

    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass

    ser1 = Service_Man.objects.get(id=pid)
    terror = False

    if request.method == "POST":
        n = request.POST['name']
        c = request.POST['contact']
        add = request.POST['add']
        dat = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        
        # Check if the service man is already booked for the given time range
        overlapping_orders = Order.objects.filter(
            service=ser1,
            book_date=dat
        ).filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )

        if overlapping_orders.exists():
            conflict = True
            # Gather all conflicting bookings and their time ranges
            for order in overlapping_orders:
                conflict_times.append(f"{order.start_time} - {order.end_time}")
        else:
            st = Status.objects.get(status="pending")
            Order.objects.create(
                status=st,
                service=ser1,
                customer=sign,
                book_date=dat,
                start_time=start_time,
                end_time=end_time
            )
            terror = True

    d = {
        'error': error,
        'ser': sign,
        'terror': terror,
        'conflict': conflict,
        'conflict_times': conflict_times  # Pass the conflict times to the template
    }

    return render(request, 'booking.html', d)





def Booking_detail(request,pid):
    user= User.objects.get(id=request.user.id)
    error=""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
        pass
    order = Order.objects.get(id=pid)
    d = {'error':error,'order':order}
    return render(request,'booking_detail.html',d)

def All_Service(request):
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser1 = Service_Man.objects.all()
    ser = Service_Category.objects.all()
    for i in ser:
        count=0
        for j in ser1:
            if i.category==j.service_name:
                count+=1
        i.total = count
        i.save()
    d = {'error': error,'ser':ser}
    return render(request,'services.html',d)

def Explore_Service(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    user = ""
    error = ""
    try:
        user = User.objects.get(id=request.user.id)
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except:
            pass
    except:
        pass
    ser = Service_Category.objects.get(id=pid)
    sta = Status.objects.get(status="Accept")
    order = Service_Man.objects.filter(service_name=ser.category,status=sta)
    d = {'error': error,'ser':ser,'order':order}
    return render(request,'explore_services.html',d)

def Logout(request):
    logout(request)
    return redirect('home')

def Edit_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    ser = Service_Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            sign.image=i
            sign.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        sign.address = ad
        sign.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        sign.save()
        terror = True
    d = {'terror':terror,'error':error,'pro':sign,'ser':ser}
    return render(request, 'edit_profile.html',d)

def Edit_Service_Profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    ser = Service_Category.objects.all()
    city = City.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            sign.image=i
            sign.save()
        except:
            pass
        try:
            i1 = request.FILES['image1']
            sign.id_card=i1
            sign.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        se = request.POST['service']
        cit = request.POST['city']
        # ex = request.POST['exp']
        dob = request.POST['dob']
        if dob:
            sign.dob=dob
            sign.save()
        ci=City.objects.get(city=cit)
        sign.address = ad
        sign.contact=con
        sign.city=ci
        user.first_name = f
        user.last_name = l
        user.email = e
        
        # sign.experience = ex
        sign.service_name = se
        user.save()
        sign.save()
        terror = True
    d = {'city':city,'terror':terror,'error':error,'pro':sign,'ser':ser}
    return render(request, 'edit_service_profile.html',d)

def Edit_Admin_Profile(request):
    dic = notification()
    error = False
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        try:
            i = request.FILES['image']
            pro.image=i
            pro.save()
        except:
            pass
        ad = request.POST['address']
        e = request.POST['email']
        con = request.POST['contact']
        pro.address = ad
        pro.contact=con
        user.first_name = f
        user.last_name = l
        user.email = e
        user.save()
        pro.save()
        error = True
    d = {'error':error,'pro':pro,'new': dic['new'], 'count': dic['count']}
    return render(request, 'edit_admin_profile.html',d)

def profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'profile.html',d)

def service_profile(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        sign = Service_Man.objects.get(user=user)
    terror = False
    d = {'pro':sign,'error':error}
    return render(request,'service_profile.html',d)

def admin_profile(request):
    dic = notification()
    user = User.objects.get(id=request.user.id)
    pro = Customer.objects.get(user=user)
    d = {'pro':pro,'new': dic['new'], 'count': dic['count']}
    return render(request,'admin_profile.html',d)

def Change_Password(request):
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Customer.objects.get(user=user)
        error = "pat"
    except:
        pass
    terror = ""
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            terror = "yes"
        else:
            terror = "not"
    d = {'error':error,'terror':terror}
    return render(request,'change_password.html',d)

def Admin_Change_Password(request):
    terror = ""
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            terror = "yes"
        else:
            terror = "not"
    d = {'terror':terror}
    return render(request,'admin_change_password.html',d)

def New_Service_man(request):
    dic = notification()
    status = Status.objects.get(status="pending")
    ser = Service_Man.objects.filter(status=status)
    d = {'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'new_service_man.html',d)

def All_Service_man(request):
    dic = notification()
    ser = Service_Man.objects.all()
    d = {'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'all_service_man.html',d)

def All_Customer(request):
    dic = notification()
    ser = Customer.objects.all()
    d = {'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'all_customer.html',d)

def Add_Service(request):
    dic = notification()
    error=False
    if request.method == "POST":
        n = request.POST['cat']
        i = request.FILES['image']
        de = request.POST['desc']
        Service_Category.objects.create(category=n,image=i,desc=de)
        error=True
    d = {'error':error,'new': dic['new'], 'count': dic['count']}
    return render(request,'add_service.html',d)

def Add_City(request):
    dic = notification()
    error=False
    if request.method == "POST":
        n = request.POST['cat']
        City.objects.create(city=n)
        error=True
    d = {'error':error,'new': dic['new'], 'count': dic['count']}
    return render(request,'add_city.html',d)

def Edit_Service(request,pid):
    dic = notification()
    error=False
    ser = Service_Category.objects.get(id=pid)
    if request.method == "POST":
        n = request.POST['cat']
        try:
            i = request.FILES['image']
            ser.image = i
            ser.save()
        except:
            pass
        de = request.POST['desc']
        ser.category = n
        ser.desc = de
        ser.save()
        error=True
    d = {'error':error,'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'edit_service.html',d)

def View_Service(request):
    dic = notification()
    ser = Service_Category.objects.all()
    d = {'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'view_service.html',d)

def View_City(request):
    dic = notification()
    ser = City.objects.all()
    d = {'ser':ser,'new': dic['new'], 'count': dic['count']}
    return render(request,'view_city.html',d)

def accept_confirmation(request,pid):
    ser = Order.objects.get(id=pid)
    sta = Status.objects.get(status='Accept')
    ser.status = sta
    ser.save()
    return redirect('service_order')

def confirm_message(request,pid):
    ser = Contact.objects.get(id=pid)
    sta = Status.objects.get(status='read')
    ser.status = sta
    ser.save()
    return redirect('new_message')

def delete_service(request,pid):
    ser = Service_Category.objects.get(id=pid)
    ser.delete()
    return redirect('view_service')

def delete_city(request,pid):
    ser = City.objects.get(id=pid)
    ser.delete()
    return redirect('view_city')

def delete_admin_order(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('admin_order')

def delete_Booking(request,pid):
    ser = Order.objects.get(id=pid)
    ser.delete()
    return redirect('customer_order')

def delete_service_man(request,pid):
    ser = Service_Man.objects.get(id=pid)
    ser.delete()
    return redirect('all_service_man')

def delete_customer(request,pid):
    ser = Customer.objects.get(id=pid)
    ser.delete()
    return redirect('all_customer')

def Change_status(request,pid):
    dic = notification()
    error = False
    pro1 = Service_Man.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error,'new': dic['new'], 'count': dic['count']}
    return render(request,'status.html',d)

def Order_status(request,pid):
    dic = notification()
    error = False
    pro1 = Order.objects.get(id=pid)
    if request.method == "POST":
        stat = request.POST['stat']
        sta = Status.objects.get(status=stat)
        pro1.status=sta
        pro1.save()
        error=True
    d = {'pro':pro1,'error':error,'new': dic['new'], 'count': dic['count']}
    return render(request,'order_status.html',d)

def Order_detail(request,pid):
    dic = notification()
    pro1 = Order.objects.get(id=pid)
    d = {'pro':pro1,'new': dic['new'], 'count': dic['count']}
    return render(request,'order_detail.html',d)

def service_man_detail(request,pid):
    dic = notification()
    pro1 = Service_Man.objects.get(id=pid)
    d = {'pro':pro1,'new': dic['new'], 'count': dic['count']}
    return render(request,'service_man_detail.html',d)

from django.shortcuts import get_object_or_404, redirect
from .models import Order, Status

def accept_confirmation(request, pid):
    ser = get_object_or_404(Order, id=pid)
    sta = Status.objects.get(id=2) 
    ser.status = sta
    ser.save()
    return redirect('service_order')

def complete_order(request, pid):
    ser = get_object_or_404(Order, id=pid)
    sta = Status.objects.get(id=6) 
    ser.status = sta
    ser.save()
    return redirect('service_order')

def cancel_order(request, pid):
    ser = get_object_or_404(Order, id=pid)
    sta = Status.objects.get(id=3)  # Cancel status
    ser.status = sta
    ser.save()
    return redirect('service_order')


def search_cities(request):
    error = ""
    user = None   
    try:
        user = User.objects.get(id=request.user.id)
        error = ""
        try:
            sign = Customer.objects.get(user=user)
            error = "pat"
        except Customer.DoesNotExist:
            pass
    except User.DoesNotExist:
        pass

    dic = notification()
    terror = False
    pro = []
    car = City.objects.all()
    count1 = 0
    car1 = Service_Category.objects.all()
    c1 = ""

    if request.method == "POST":
        c1 = request.POST['cat']
        ser1 = Service_Category.objects.get(category=c1)
        
        if user:
            try:
                customer = Customer.objects.get(user=user)
                customer_coords = (customer.latitude, customer.longitude)

                service_providers = Service_Man.objects.filter(service_name=ser1)

                
                graph = build_graph({customer.id: customer_coords}, 
                                    {service_man.id: (service_man.latitude, service_man.longitude) for service_man in service_providers})

                
                distances = []
                for service_man in service_providers:
                    service_coords = (service_man.latitude, service_man.longitude)
                    
            
                    path = a_star(customer_coords, service_coords, graph)
                    if path:
                        total_distance = sum([haversine(path[i][0], path[i][1], path[i+1][0], path[i+1][1]) for i in range(len(path) - 1)])
                    else:
                        
                        total_distance = haversine(customer_coords[0], customer_coords[1], service_coords[0], service_coords[1])

                    distances.append((service_man, total_distance))

                
                distances.sort(key=lambda x: x[1])
                distances = distances[:5] 

                
                pro = [{'service_man': service_man, 'distance': distance} for service_man, distance in distances]
                count1 = len(pro)
                terror = True
            except Customer.DoesNotExist:
                error = "Customer not found."
        else:
            error = "User not found."

    d = {
        'c1': c1, 
        'count1': count1, 
        'car1': car1, 
        'car': car, 
        'order': pro, 
        'new': dic['new'], 
        'count': dic['count'], 
        'error': error, 
        'terror': terror
    }
    return render(request, 'search_cities.html', d)






def search_services(request):
    dic = notification()
    error=False
    pro=""
    car = Service_Category.objects.all()
    c=""
    if request.method=="POST":
        c=request.POST['cat']
        ser = Service_Category.objects.get(category=c)
        pro = Service_Man.objects.filter(service_name=ser)
        error=True
    d = {'service':c,'car':car,'order':pro,'new': dic['new'], 'count': dic['count'],'error':error}
    return render(request,'search_services.html',d)

def new_message(request):
    dic = notification()
    sta = Status.objects.get(status='unread')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1,'new': dic['new'], 'count': dic['count']}
    return render(request,'new_message.html',d)

def read_message(request):
    dic = notification()
    sta = Status.objects.get(status='read')
    pro1 = Contact.objects.filter(status=sta)
    d = {'ser':pro1,'new': dic['new'], 'count': dic['count']}
    return render(request,'read_message.html',d)

import datetime
from django.shortcuts import render
from .models import Order, Status 

def Search_Report(request):
    dic = notification()
    status = Status.objects.get(status="pending")
    reg1 = Order.objects.filter(status=status)
    total = 0
    for i in reg1:
        total += 1
    data = Order.objects.all()
    error = ""
    terror = ""
    reg = ""

    if request.method == "POST":
        terror = "found"
        i = request.POST.get('date1', '').strip()  # Safely get the date1 value
        n = request.POST.get('date2', '').strip()  # Safely get the date2 value

        # Initialize variables to hold parsed dates
        start_date = None
        end_date = None
        
        try:
            # Attempt to parse the input dates
            if i:  # Check if date1 is not empty
                start_date = datetime.datetime.fromisoformat(i)
            if n:  # Check if date2 is not empty
                end_date = datetime.datetime.fromisoformat(n)

            # Proceed if both dates are valid
            if start_date and end_date:
                for j in data:
                    day3 = j.book_date  # Assuming book_date is a date object
                    day3_datetime = datetime.datetime.combine(day3, datetime.datetime.min.time())  # Convert date to datetime

                    if start_date < day3_datetime < end_date:  # Compare datetime objects
                        j.report_status = 'active'
                        j.save()
                    else:
                        j.report_status = 'inactive'
                        j.save()
                reg = Order.objects.filter(report_status="active")
                if not reg:
                    error = "notfound"
            else:
                error = "Both dates are required."

        except ValueError:
            error = "Invalid date format. Please enter valid dates."

    d = {
        'new': dic['new'],
        'count': dic['count'],
        'order': reg,
        'error': error,
        'terror': terror,
        'reg1': reg1,
        'total': total
    }
    return render(request, 'search_report.html', d)



def distance_view(request):
    
    customer_id = None
    service_id = None
    set_ids_from_db()
      
    if not (customer_id and service_id):
        return render(request, 'error.html', {'message': 'Could not find valid IDs.'})

    
    customer_coords, service_coords = get_coordinates_from_db(customer_id, service_id)

    if not (customer_coords and service_coords):
        return render(request, 'error.html', {'message': 'Could not retrieve coordinates.'})

    lat1, lon1 = customer_coords
    lat2, lon2 = service_coords

    
    distance = haversine(lat1, lon1, lat2, lon2)

    
    return render(request, 'signup1.html', {'distance': distance})

    

def signup_view(request):
    
    error = request.GET.get('error', '')
    return render(request, 'map.html', {'error': error})

