"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('createLibrary/', views.create_library),
    path('createRoom/', views.create_room),
    path('registerStudent/', views.register_student),
    path('createReservation/', views.create_reservation),
    path('deleteReservation/', views.delete_reservation),
    path('checkRoomAvailability/<slug:roomId>/', views.check_room_availability),
    path('getAllRooms/', views.get_all_rooms),
    path('getAvailableRooms/<str:start_time>/<str:end_time>/', views.get_available_rooms),
    path('myReservationsTimeRange/<str:start_time>/<str:end_time>/',views.get_reservations_for_student_in_time_range),
    path('myReservations/', views.get_all_reservations_for_a_student),
    path('getAllReservations/', views.get_all_reservations),
    path('getReservationsInTimeRange/',views.get_reservations_in_time_range),
    path('clearExpiredTimeSlots',views.clear_expired_time_slots),
]
