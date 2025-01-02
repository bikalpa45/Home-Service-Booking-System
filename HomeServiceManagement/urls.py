from django.contrib import admin
from django.urls import path
from home_service.views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',Home,name="home"),
    path('user_home',User_home,name="user_home"),
    path('admin_home/',Admin_Home,name="admin_home"),
    path('service_home',Service_home,name="service_home"),
    path('service',All_Service,name="service"),
    path('profile',profile,name="profile"),
    path('service_profile',service_profile,name="service_profile"),
    path('admin_profile',admin_profile,name="admin_profile"),
    path('edit_profile',Edit_Profile,name="edit_profile"),
    path('edit_service_profile',Edit_Service_Profile,name="edit_service_profile"),
    path('edit_admin_profile',Edit_Admin_Profile,name="edit_admin_profile"),
    path('contact',contact,name="contact"),
    path('about',about,name="about"),
    path('login',Login_User,name="login"),
    path('admin_login',Login_admin,name="admin_login"),
    path('logout',Logout,name="logout"),
    path('signup',Signup_User,name="signup"),
    path('change_password',Change_Password,name="change_password"),
    path('admin_change_password',Admin_Change_Password,name="admin_change_password"),
    path('new_service_man',New_Service_man,name="new_service_man"),
    path('all_service_man',All_Service_man,name="all_service_man"),
    path('all_customer',All_Customer,name="all_customer"),
    path('add_service',Add_Service,name="add_service"),
    path('add_city',Add_City,name="add_city"),
    path('view_service',View_Service,name="view_service"),
    path('view_city',View_City,name="view_city"),
    path('service_order',Service_Order,name="service_order"),
    path('customer_order',Customer_Order,name="customer_order"),
    path('admin_order',Admin_Order,name="admin_order"),
    path('search_report',Search_Report,name="search_report"),
    path('new_message',new_message,name="new_message"),
    path('read_message',read_message,name="read_message"),
    path('search_cities',search_cities,name="search_cities"),
    path('search_services',search_services,name="search_services"),
    path('confirm_message(<int:pid>)',confirm_message,name="confirm_message"),
    path('status(<int:pid>)',Change_status,name="status"),
    path('edit_service(<int:pid>)',Edit_Service,name="edit_service"),
    path('delete_service(<int:pid>)',delete_service,name="delete_service"),
    path('delete_customer(<int:pid>)',delete_customer,name="delete_customer"),
    path('explore_services(<int:pid>)',Explore_Service,name="explore_services"),
    path('booking(<int:pid>)',Customer_Booking,name="booking"),
    path('delete_service_man(<int:pid>)',delete_service_man,name="delete_service_man"),
    path('delete_Booking(<int:pid>)',delete_Booking,name="delete_Booking"),
    path('accept_confirmation(<int:pid>)',accept_confirmation,name="accept_confirmation"),
    path('Booking_detail(<int:pid>)',Booking_detail,name="Booking_detail"),
    path('delete_admin_order(<int:pid>)',delete_admin_order,name="delete_admin_order"),
    path('order_status(<int:pid>)',Order_status,name="order_status"),
    path('order_detail(<int:pid>)',Order_detail,name="order_detail"),
    path('service_man_detail(<int:pid>)',service_man_detail,name="service_man_detail"),
    path('delete_city(<int:pid>)',delete_city,name="delete_city"),
    path('signup1',distance_view,name="signup1"),
    path('check-username-email/', check_username_email, name='check_username_email'),
    path('signup/', Signup_User, name='signup'),
    path('cancel_order/<int:pid>/', cancel_order, name='cancel_order'),
    path('complete_order/<int:pid>/', complete_order, name='complete_order'),
    

    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
