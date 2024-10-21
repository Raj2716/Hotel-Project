from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    name=models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    gmail_id = models.EmailField(max_length=254)
    is_hotelier = models.BooleanField(default=False) 

    def __str__(self):
        return self.name

class Hotel(models.Model):

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    ratings = models.DecimalField(max_digits=3, decimal_places=1)
    hotel_facilities = models.TextField(null=True, blank=True) 
    image = models.ImageField(upload_to='hotels/')  
    hotelier = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default=1)

    def save(self, *args, **kwargs):
        self.hotel_facilities = self.hotel_facilities.upper()
        self.name = self.name.upper()
        self.location = self.location.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.location}"

class Room(models.Model):
    SINGLE = 'Single'
    DOUBLE = 'Double'
    KING = 'King'
    QUEEN = 'Queen'

    BED_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (KING, 'King'),
        (QUEEN, 'Queen'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE,default=1)
    price = models.IntegerField()
    max_members = models.IntegerField()
    amenities = models.TextField()
    total_rooms = models.IntegerField(default=0)  
    room_number = models.CharField(max_length=50,default='None')
    bed_type = models.CharField(max_length=50,choices=BED_TYPE_CHOICES, null=False, blank=False)
    image = models.ImageField(upload_to='rooms/')

    def save(self, *args, **kwargs):
        self.amenities = self.amenities.upper()
        self.bed_type = self.bed_type.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room {self.room_number} in {self.hotel.name} ({self.bed_type})"


class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    num_members = models.IntegerField(default=1) 

    def __str__(self):
        return f"Booking by {self.user.name} for {self.room} from {self.check_in} to {self.check_out}"






