from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils import timezone


class UserRegistrationForm(UserCreationForm):
    name=models.CharField(max_length=255)
    mobile_number = forms.CharField(max_length=15)
    gmail_id = models.EmailField(max_length=254)
    class Meta:
        model = CustomUser
        fields = ['name','username', 'mobile_number','gmail_id', 'password1', 'password2']

class EditUserProfileForm(forms.ModelForm):  
    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'mobile_number', 'gmail_id'] 

class HotelierRegistrationForm(UserCreationForm):
    name=models.CharField(max_length=255)
    mobile_number = forms.CharField(max_length=15)
    gmail_id = models.EmailField(max_length=254)
    class Meta:
        model = CustomUser
        fields = ['name','username', 'mobile_number','gmail_id', 'password1', 'password2']


class EditHotelierProfileForm(forms.ModelForm):  
    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'mobile_number', 'gmail_id'] 


class HotelForm(forms.ModelForm):
    FACILITY_CHOICES = [
         ('WIFI', 'WIFI'),
        ('PARKING', 'PARKING'),
        ('POOL', 'POOL'),
        ('RESTAURANT', 'RESTAURANT'),
        ('GYM', 'GYM'),
    ]

    predefined_facilities = forms.MultipleChoiceField(
        choices=FACILITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    custom_facilities = forms.CharField(
        max_length=255,
        required=False,
        help_text="Add any other facilities (comma-separated, no leading/trailing spaces)."
    )

    class Meta:
        model = Hotel
        fields = ['name', 'location', 'ratings', 'image']  # 'hotel_facilities' excluded

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # When editing an existing hotel
            existing_facilities = [facility.strip() for facility in self.instance.hotel_facilities.split(',') if facility.strip()]

            # Pre-populate predefined facilities
            self.fields['predefined_facilities'].initial = [
                facility for facility in existing_facilities if facility in dict(self.FACILITY_CHOICES)
            ]

            # Pre-populate custom facilities (facilities not in predefined list)
            custom_facilities_initial = [
                facility for facility in existing_facilities if facility not in dict(self.FACILITY_CHOICES)
            ]
            self.fields['custom_facilities'].initial = ', '.join(custom_facilities_initial)

    def clean(self):
        cleaned_data = super().clean()

        predefined_facilities = cleaned_data.get('predefined_facilities', [])
        custom_facilities = cleaned_data.get('custom_facilities', '').strip()

        # Combine predefined and custom facilities into one string for saving to hotel_facilities
        combined_facilities = ', '.join(predefined_facilities)  # Start with predefined facilities
        if custom_facilities:
            combined_facilities = f"{combined_facilities}, {custom_facilities}" if combined_facilities else custom_facilities

        # Ensure the combined facilities are stored in the form's cleaned_data, ready to be saved to the instance
        cleaned_data['hotel_facilities'] = combined_facilities

        return cleaned_data

    def save(self, commit=True):
        # Override the save method to ensure hotel_facilities is updated correctly
        instance = super().save(commit=False)
        instance.hotel_facilities = self.cleaned_data['hotel_facilities']
        if commit:
            instance.save()
        return instance
        

class RoomForm(forms.ModelForm):
    ROOM_FACILITY_CHOICES = [
        ('AC', 'AC'),
        ('TELEVISION', 'TELEVISION'),
        ('BALCONY', 'BALCONY'),
        ('PRIVATE BATHROOM', 'PRIVATE BATHROOM'),
        ('VIEW', 'VIEW'),
    ]

    predefined_facilities = forms.MultipleChoiceField(
        choices=ROOM_FACILITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    custom_facilities = forms.CharField(
        max_length=255,
        required=False,
        help_text="Add any other facilities (comma-separated)."
    )
    room_number = forms.CharField(widget=forms.HiddenInput(), required=False)  # Now uses room_number from the model

    class Meta:
        model = Room
        fields = ['price', 'max_members', 'total_rooms', 'room_number', 'bed_type', 'image', 'predefined_facilities', 'custom_facilities']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # When editing an existing room
            # Split the existing amenities into a list
            existing_facilities = [facility.strip() for facility in self.instance.amenities.split(', ') if facility.strip()]

            # Pre-populate predefined facilities (those that match ROOM_FACILITY_CHOICES)
            self.fields['predefined_facilities'].initial = [
                facility for facility in existing_facilities if facility in dict(self.ROOM_FACILITY_CHOICES)
            ]

            # Pre-populate custom facilities (those that don't match predefined choices)
            custom_facilities_initial = [
                facility for facility in existing_facilities if facility not in dict(self.ROOM_FACILITY_CHOICES)
            ]
            self.fields['custom_facilities'].initial = ', '.join(custom_facilities_initial)

            # Pre-populate room numbers
            self.fields['room_number'].initial = self.instance.room_number
            self.fields['bed_type'].initial = self.instance.bed_type

    def clean(self):
        cleaned_data = super().clean()

        predefined_facilities = cleaned_data.get('predefined_facilities', [])
        custom_facilities = cleaned_data.get('custom_facilities', '').strip()

        # Combine predefined and custom facilities into a single string
        combined_facilities = ', '.join(predefined_facilities)  # Start with predefined facilities
        if custom_facilities:
            combined_facilities = f"{combined_facilities}, {custom_facilities}" if combined_facilities else custom_facilities

        # Store the combined facilities in the 'amenities' field
        cleaned_data['amenities'] = combined_facilities

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.amenities = self.cleaned_data['amenities']
        instance.room_number = self.cleaned_data['room_number']  # Save room numbers
        if commit:
            instance.save()
        return instance
    

class ExtendBookingForm(forms.Form):
    new_checkout_date = forms.DateField(widget=forms.SelectDateWidget, required=True)

    def clean_new_checkout_date(self):
        new_checkout_date = self.cleaned_data['new_checkout_date']
        if new_checkout_date <= timezone.now().date():
            raise forms.ValidationError("The new checkout date must be in the future.")
        return new_checkout_date
