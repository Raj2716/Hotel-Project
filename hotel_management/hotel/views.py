from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Q
import datetime


def home(request):
    return render(request, 'home.html')

def user_dashboard(request):
        return render(request,"user_dashboard.html")

def hotelier_dashboard(request):
        hotels = Hotel.objects.filter(hotelier=request.user)
        return render(request,"hotelier_dashboard.html",{'hotels': hotels})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return home(request)
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

def register_hotelier(request):
    if request.method == 'POST':
        form = HotelierRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_hotelier = True  
            user.save()
            return home(request)
    else:
        form = HotelierRegistrationForm()
    return render(request, 'register_hotelier.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                if not hasattr(user, 'is_hotelier') or not user.is_hotelier:
                    login(request, user)
                    return user_dashboard(request) 
                else:
                    form.add_error(None, "You cannot log in as a user.")  
            else:
                form.add_error(None, "Invalid username or password.") 
                login(request, user)
                return user_dashboard(request) 
    else:
        form = AuthenticationForm()
    return render(request, 'user_login.html', {'form': form})       
   
def hotelier_login(request):
     if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None :
                if hasattr(user, 'is_hotelier') and user.is_hotelier:
                    login(request, user)
                    return hotelier_dashboard(request)  
                else:
                    form.add_error(None, "You cannot log in as a hotelier.")  
            else:
                form.add_error(None, "Invalid username or password.")
     else:
        form = AuthenticationForm()
     return render(request, 'hotelier_login.html', {'form': form})     

def logouts(request):
    if request.user.is_authenticated:
        logout(request)
        return home(request)

def add_hotel(request):
    if request.method == 'POST':
        form = HotelForm(request.POST,request.FILES) 
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.hotelier = request.user
            hotel.save()
            return hotelier_dashboard(request)
    else:
        form = HotelForm()
    return render(request, 'add_hotel.html', {'form': form})

def update_hotel(request,hotel_id): 
    h=Hotel.objects.get(id=hotel_id) 
    if request.method == "POST":
        form=HotelForm(request.POST,request.FILES,instance = h)
        if form.is_valid():
            form.save()
            return hotelier_dashboard(request)
    else:
        form = HotelForm(instance=h)
    return render(request,"update_hotel.html",{'form':form})

def delete_hotel(request,hotel_id):
    hotel=Hotel.objects.get(id=hotel_id)
    if request.method=='POST':
            hotel.delete()
            return hotelier_dashboard(request)
    return render(request,"delete_hotel.html",{'hotel_delete':hotel})

def add_room(request, hotel_id):
    hotel=Hotel.objects.get(id=hotel_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.room_number = request.POST.get('room_numbers') 
            room.save()
            return hotelier_dashboard(request)
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form, 'hotel': hotel})

def update_room(request, room_id):
    room = Room.objects.get(id=room_id)
    form = RoomForm(instance=room)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return hotelier_dashboard(request) 
        form = RoomForm(instance=room)
    return render(request, 'update_room.html', {'form': form, 'room': room})

def delete_room(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        room.delete()
        return hotelier_dashboard(request)
    return render(request, 'delete_room.html', {'room': room})
 
def edit_profile_hotelier(request):
    user = request.user 
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  
            return redirect('hotel:hotelier_dashboard')  
        else:
            print("Form errors:", form.errors)
    else:
        form = EditUserProfileForm(instance=user)
    
    return render(request, 'edit_profile_hotelier.html', {'form': form, 'user': user})


def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    current_date = timezone.now().date()
    existing_bookings = bookings.filter(check_in__lte=current_date, check_out__gte=current_date)
    upcoming_bookings = bookings.filter(check_in__gte=current_date)
    past_bookings = bookings.filter(check_out__lt=current_date)

    return render(request, 'user_dashboard.html', {
       'upcoming_bookings': upcoming_bookings,
        'existing_bookings': existing_bookings,  
        'past_bookings': past_bookings,
        'bookings_exist': bookings.exists() 
    })


def edit_profile_user(request):
    user = request.user  
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  
            return redirect('hotel:user_dashboard')  
        else:
            print("Form errors:", form.errors)
    else:
        form = EditUserProfileForm(instance=user)
    
    return render(request, 'edit_profile_user.html', {'form': form, 'user': user})

def extend_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = ExtendBookingForm(request.POST)
        if form.is_valid():
            new_checkout_date = form.cleaned_data['new_checkout_date']
            overlapping_bookings = Booking.objects.filter(
                room=booking.room,
                check_in__lt=new_checkout_date,
                check_out__gt=booking.check_out  
            ).exclude(id=booking.id)  
            
            if not overlapping_bookings.exists():
                booking.check_out = new_checkout_date
                booking.save()
                return redirect('hotel:user_dashboard')
            else:
                form.add_error(None, "The room is not available for the selected period.")
    
    else:
        form = ExtendBookingForm()

    return render(request, 'extend_booking.html', {
        'form': form,
        'booking': booking
    })

def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    if request.method == "POST":
        booking.delete()
        return user_dashboard(request) 
    return render(request, 'cancel_booking.html', {'booking': booking})
    
def search_hotels(request):
    today = timezone.now().date()  
    if request.method == 'POST':
        location = request.POST.get('location')
        check_in = request.POST.get('check_in')  
        check_out = request.POST.get('check_out')  
        num_members = int(request.POST.get('num_members'))
        check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()  
        check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()  
        if check_in_date < today or check_out_date < today:
            return render(request, 'search_hotels.html', {'error': 'Check-in and check-out dates cannot be in the past.'})
        if check_out_date <= check_in_date:
            return render(request, 'search_hotels.html', {'error': 'Check-out date must be after check-in date.'})
        hotels = Hotel.objects.filter(location__icontains=location)
        available_hotels = []
        for hotel in hotels:
            rooms = hotel.room_set.filter(max_members__gte=num_members)
            available_rooms = []
            for room in rooms:
                overlapping_bookings = Booking.objects.filter(
                    Q(check_in__lt=check_out_date, check_out__gt=check_in_date),
                    room=room  
                )

                booked_rooms_count = overlapping_bookings.count()
                available_room_count = room.total_rooms - booked_rooms_count

                if available_room_count > 0:
                    room.available_room_count = available_room_count  
                    available_rooms.append(room)

            if available_rooms:
                hotel.available_rooms = available_rooms  
                available_hotels.append(hotel)

        return render(request, 'available_hotels.html', {'available_hotels': available_hotels})

    return render(request, 'search_hotels.html', {'today_date': today})


def confirm_booking(request, room_id):
    if request.method == 'POST':
        if 'confirm_booking' not in request.POST:
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            num_members = int(request.POST.get('num_members'))
            total_rooms_needed = int(request.POST.get('total_rooms_needed'))
            room = Room.objects.get(id=room_id)
            hotel = room.hotel  
            check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
            num_nights = (check_out_date - check_in_date).days
            price_per_room = room.price
            total_price = price_per_room * total_rooms_needed * num_nights
            hotel_facilities = hotel.hotel_facilities.split(',')
            room_facilities = room.amenities.split(',')
            print(f"Rendering confirmation page with the provided data: "
                  f"Check-in: {check_in}, Check-out: {check_out}, Members: {num_members}, "
                  f"Rooms needed: {total_rooms_needed}, Price: {total_price}")

            return render(request, 'confirm_booking.html', {
                'hotel': hotel,
                'room': room,
                'check_in': check_in,
                'check_out': check_out,
                'num_members': num_members,
                'total_rooms_needed': total_rooms_needed,
                'total_price': total_price,
                'hotel_facilities': hotel_facilities,
                'room_facilities': room_facilities,
            })
        
        else:
            print("Finalizing the booking...")
            room = Room.objects.get(id=room_id)
            hotel = room.hotel

            # Retrieve form data for booking
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            num_members = int(request.POST.get('num_members'))
            total_rooms_needed = int(request.POST.get('total_rooms_needed'))

            check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
            selected_hotel_facilities = request.POST.getlist('hotel_facilities')
            selected_room_facilities = request.POST.getlist('room_facilities')
            # Try to create the booking and print debug statements
            try:
                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    check_in=check_in_date,
                    check_out=check_out_date,
                    num_members=num_members,
                )
                print("Booking successfully created!")
            except Exception as e:
                print(f"Error occurred while creating the booking: {e}")

            # Render the success page after booking
            return render(request, 'booking_success.html', {
                'hotel': hotel,
                'location': hotel.location,
                'check_in': check_in,
                'check_out': check_out,
                'num_members': num_members,
                'total_rooms_needed': total_rooms_needed,
                'total_price': room.price * total_rooms_needed * ((check_out_date - check_in_date).days),
                'selected_hotel_facilities': selected_hotel_facilities,
            'selected_room_facilities': selected_room_facilities,
            })

    return redirect('hotel:search_hotels')  




def booking_success(request):
    if request.method == 'POST':
        hotel_name = request.POST.get('hotel_name')
        location = request.POST.get('location')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        num_members = int(request.POST.get('num_members'))
        total_rooms_needed = int(request.POST.get('total_rooms_needed'))
        total_price = float(request.POST.get('total_price'))
        selected_hotel_facilities = request.POST.getlist('hotel_facilities')
        selected_room_facilities = request.POST.getlist('room_facilities')

        return render(request, 'booking_success.html', {
            'hotel': hotel_name,
            'location': location,
            'check_in': check_in,
            'check_out': check_out,
            'num_members': num_members,
            'total_rooms_needed': total_rooms_needed,
            'total_price': total_price,
            'selected_hotel_facilities': selected_hotel_facilities,
            'selected_room_facilities': selected_room_facilities,
        })

    return redirect('hotel:search_hotels') 


def view_bookings(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    current_date = timezone.now().date()
    upcoming_bookings = Booking.objects.filter(room__hotel=hotel, check_in__gt=current_date)
    current_bookings = Booking.objects.filter(room__hotel=hotel, check_in__lte=current_date, check_out__gte=current_date)
    past_bookings = Booking.objects.filter(room__hotel=hotel, check_out__lt=current_date)

    return render(request, 'view_bookings.html', {
        'hotel': hotel,
        'upcoming_bookings': upcoming_bookings,
        'current_bookings': current_bookings,
        'past_bookings': past_bookings,
    })