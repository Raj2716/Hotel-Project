from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .import views 
app_name = 'hotel'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/hotelier/', views.register_hotelier, name='register_hotelier'),
    path('login/user/', views.user_login, name='user_login'),
    path('login/hotelier/', views.hotelier_login, name='hotelier_login'),
    path('logout/', views.logouts, name='user_logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('hotelier/dashboard/', views.hotelier_dashboard, name='hotelier_dashboard'),
    path('hotelier/add-hotel/', views.add_hotel, name='add_hotel'),
    path('hotelier/add-room/<int:hotel_id>/', views.add_room, name='add_room'),
    path('hotelier/update-hotel/<int:hotel_id>/', views.update_hotel, name='update_hotel'),
    path('hotelier/delete-hotel/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('hotelier/update-room/<int:room_id>/', views.update_room, name='update_room'),
    path('hotelier/delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('user/search-hotels/', views.search_hotels, name='search_hotels'),
    path('confirm_booking/<int:room_id>/', views.confirm_booking, name='confirm_booking'),
    path('extend-booking/<int:booking_id>/', views.extend_booking, name='extend_booking'),
    path('edit-user-profile/', views.edit_profile_user, name='edit_profile_user'),
    path('edit-hotelier-profile/', views.edit_profile_hotelier, name='edit_profile_hotelier'),
    path('booking_success/',views.booking_success,name='booking_success'),
    path('hotel/<int:hotel_id>/bookings/', views.view_bookings, name='view_bookings'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)