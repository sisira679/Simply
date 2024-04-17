from django.contrib import admin
from django.urls import path,include
from.import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
# from .views import book_appointment
from .views import scheduling, delete_schedule
from .views import edit_doctor, doctor_list
from .views import apply_leave, doctor_leave, admin_dashboard, approve_leave, reject_leave
from .views import today_appointments
from .views import add_prescription
#  view_prescription, download_prescription_pdf
from .views import book_appointment, payment, verify_payment, payment_success
from .views import view_patient_history
# # from .views import doctor_prescription_view
from .views import  view_prescription
from .views import view_appointment_details, download_prescription
from .views import  view_appointment_details
from .views import appointment_list
from .views import add_pharmacist






urlpatterns = [
   path('',views.user_login,name="login"),
   path('register.html',views.register, name="register"),
   path('login.html', views.user_login, name="login"),
   path('logout/', views.logout, name='logout'),
   path('indexadmin.html', views.indexadmin, name="indexadmin"),
   path('booking/',views.booking_view, name="booking"),
   path('add-doctor.html',views.add_doctor,name="add-doctor"),
   path('add-pharmacist.html',views.add_pharmacist,name="add-pharmacist"),
   path('pharmacistdashboard.html',views.pharmacistdashboard,name="pharmacistdashboard"),
   path('pharmacist-list.html',views.pharmacist_list,name="pharmacist-list"),
#    # path('doctor-list.html',views.doctor_list,name="doctor-list"),
   path('doctor-list.html', doctor_list, name='doctor-list'), 
   path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete-doctor'),
   path('doctordashboard.html',views.doctor_dashboard,name='doctordashboard'),

   path('profileuser.html',views.profile_user,name='profileuser'),
   path('profile.html', views.profile, name='profile'),
   path('changepassword.html', views.changepassword, name='changepassword'),
   path('userdashboard.html', views.userdashboard, name='userdashboard'),
   path('doctorprofile.html', views.doctorprofile, name='doctorprofile'),
   path('doctordetails.html', views.doctordetails, name='doctordetails'),
   path('specializations.html', views.specializations, name='specializations'),
   path('alldoctorlist.html', views.alldoctor, name='alldoctorlist'),
   path('scheduling.html', views.scheduling, name='scheduling'),
   path('appointment.html', views.appointment, name='appointment'),
   path('confirm_booking.html', views.confirm_booking, name='confirm_booking'),
#    # path('timescheduling.html', views.timescheduling, name='timescheduling'),
    path('booking/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('doctorprofile_list.html', views.doctorprofile_list, name='doctorprofile_list'),
    path('edit_doctor/<int:doctor_id>/', edit_doctor, name='edit_doctor'),
    path('delete_schedule/<int:schedule_id>/', delete_schedule, name='delete_schedule'),
    path('appointment_confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
   
    path('update_profile.html', views.update_profile, name='update_profile'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('doctor_dashboard.html', views.doctordashboard, name='doctor_dashboard'),
    path('appointment_confirmation/<int:appointment_id>/', views.appointment_confirmation, name='appointment_confirmation'),
    path('get_time_slots/<str:selected_date>/',views.get_time_slots, name='get_time_slots'),
    path('apply_leave.html', views.apply_leave, name='apply_leave'),
    path('doctor_leave.html', views.doctor_leave, name='doctor_leave'),
  

    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('process_payment/<int:appointment_id>/', views.process_payment, name='process_payment'),
#     # Add the URL pattern for the success page
  
    path('today_appointments.html', views.today_appointments, name='today_appointments'),
    path('add_prescription/<int:appointment_id>/', add_prescription, name='add_prescription'),
   
#     # path('view_prescription/<int:appointment_id>/', view_prescription, name='view_prescription'),
#     # path('download_prescription_pdf/<int:appointment_id>/', download_prescription_pdf, name='download_prescription_pdf'),
    path('payment/<int:appointment_id>/', payment, name='payment'),
    path('verify_payment/<int:appointment_id>/', verify_payment, name='verify_payment'),
    path('payment_success/', payment_success, name='payment_success'),
#     # path('view_patient_history/<int:user_id>/', view_patient_history, name='view_patient_history'),

#     #  path('view_history/<int:user_id>/', view_history, name='view_history'),
#     # path('doctor_prescription_view/<int:appointment_id>/', doctor_prescription_view, name='doctor_prescription_view'),
#     #  path('view_patient_history/<int:user_id>/', view_patient_history, name='view_patient_history'),
    path('view_patient_history/<int:patient_id>/', view_patient_history, name='view_patient_history'), 
    path('view_appointment_details/<int:appointment_id>/', view_appointment_details, name='view_appointment_details'),
    path('download_prescription/<int:appointment_id>/', views.download_prescription, name='download_prescription'),
    path('view_prescription/<int:appointment_id>/', views.view_prescription, name='view_prescription'),
    path('doctorprofile/view_more/<int:doctor_id>/', views.view_more, name='view_more'),
    path('appointments/', appointment_list, name='appointment_li'),
    path('add_product.html', views.add_product, name='add_product'),
    path('product_list.html', views.product_list, name='product_list'),
    path('add_brand.html', views.add_brand, name='add_brand'),
    path('brand_list.html', views.brand_list, name='brand_list'),
    path('add_category.html', views.add_category, name='add_category'),
    path('add-subcategory/<int:category_id>/', views.add_subcategory, name='add_subcategory'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('get_subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update/<int:product_id>/', views.update_product, name='update_product'),
    path('display_product/', views.display_product, name='display_product'), 
    path('whatsapp-chat/<str:agent_phone>/', views.whatsapp_chat, name='whatsapp_chat'),
     path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
     path('product/<int:product_id>/', views.product_details, name='product_details'),
      path('update-cart-item/', views.update_cart_item, name='update-cart-item'),
       path('deliveryregister/', views.deliveryregister, name='deliveryregister'),
      



   
   
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('add-to-cart/<int:product_id>/',views. add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:product_id>/',views. remove_from_cart, name='remove-from-cart'),
    path('cart/', views.view_cart, name='cart'),
    path('increase-cart-item/<int:product_id>/', views.increase_cart_item, name='increase-cart-item'),
    path('decrease-cart-item/<int:product_id>/', views.decrease_cart_item, name='decrease-cart-item'),
    path('fetch-cart-count/', views.fetch_cart_count, name='fetch-cart-count'),
    path('create-order/', views.create_order, name='create-order'),
    path('handle-payment/', views.handle_payment, name='handle-payment'),
    path('checkout/', views.checkout, name='checkout'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
   
    path('order_summary/', views.order_summary, name='order_summary'),
 
    path('search/', views.search_products, name='search_products'),
    path('billinvoice/',views.bill_invoice, name='bill_invoice'),
    path('delete_appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    
    path('delete_prescription/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
    path('add-service/', views.add_service, name='add_service'),
    path('suggest-service/<int:appointment_id>/', views.suggest_service, name='suggest_service'),
    path('services/', views.service_list, name='service_list'),
    path('book-service/<int:service_id>/', views.book_service, name='book_service'),


    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services_list/',views.services_list, name='services_list'),
    path('add-time-slot/<int:service_id>/', views.add_time_slot, name='add_time_slot'),
    path('delete-time-slot/<int:time_slot_id>/', views.delete_time_slot, name='delete_time_slot'),
    path('delete-service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('get-time-slots/', views.get_time_slots, name='get_time_slots'),
    path('book/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('products/', views.product_admin, name='product_admin'),
    path('admin_dashboard.html', views.admin_dashboard, name='admin_dashboard'),
    path('user_list.html',views.user_list,name='user_list.html'),
    path('chatgpt/', views.chatgpt, name='chatgpt'),
    path('generate-response/',views.generate_response, name='generate_response'),
    path('register/delivery-boy/', views.register_delivery_boy, name='register_delivery_boy'),
   path('chat/', views.chat_room, name='chat_room'),





   

    

]

    
    
   


   