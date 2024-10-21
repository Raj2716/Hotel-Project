from django.contrib import admin
from .models import CustomUser, Hotel, Room, Booking


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'email', 'is_hotelier', 'mobile_number')
    search_fields = ('name', 'username', 'gmail_id')
    list_filter = ('is_hotelier',)


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'ratings', 'hotelier')
    search_fields = ('name', 'location')
    list_filter = ('ratings',)
    
    def delete_model(self, request, obj):
        if obj.room_set.exists():  
            self.message_user(request, "Cannot delete this hotel because it has associated rooms.", level='error')
        else:
            super().delete_model(request, obj)


class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'id','bed_type', 'price', 'max_members')
    search_fields = ('hotel__name', 'bed_type', 'price')
    list_filter = ('bed_type', 'hotel')

    def delete_model(self, request, obj):
        if obj.booking_set.exists():  
            self.message_user(request, "Cannot delete this room because it has associated bookings.", level='error')
        else:
            super().delete_model(request, obj)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'num_members')
    search_fields = ('user__name', 'room__hotel__name')
    list_filter = ('check_in', 'check_out')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
