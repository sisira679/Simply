from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField


class CustomUser(AbstractUser):
    # Add any additional fields you need
    role = models.CharField(max_length=100, default="")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender_choices = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=6, choices=gender_choices, blank=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phonenumber = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    bloodgroup = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    
    def _str_(self):
        return self.username


class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    id_proof_image = models.ImageField(upload_to='id_proof_images/', blank=True, null=True)
    phonenumber = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255,blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city=models.CharField(max_length=100,blank=True, null=True)
    pdf_certificate_1 = models.FileField(upload_to='pdf_certificates/', blank=True, null=True)
    pdf_certificate_2 = models.FileField(upload_to='pdf_certificates/', blank=True, null=True)
    pdf_certificate_3 = models.FileField(upload_to='pdf_certificates/', blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Add this line






     
    def is_profile_complete(self):
        # Define your logic to check if the profile is complete.
        # For example, check if essential fields are filled.
        return all([self.phonenumber, self.address, self.dob, self.age, self.state, self.city])


        
class Specializations(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='specializations')
    # Rest of the fields...
    options = [
        ('medical_dermatology', 'Medical Dermatology'),
        ('cosmetic_dermatology', 'Cosmetic Dermatology'),
        ('laser_dermatology', 'Laser Dermatology'),
        ('hair_treatment', 'Hair Treatment'),
        #Add more specialization options here if needed
    ]
    specializations = models.CharField(max_length=100, choices=options,blank=True)

    def __str__(self):
        return f"{self.get_specialization_display()} for {self.user.username}"

class DoctorSchedule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.time_slot}"


class Appointment(models.Model):
    doctor_profile = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments', blank=True, null=True)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=100)
    reason = models.TextField()


    def __str__(self):
        return f"{self.user.first_name} - {self.doctor.first_name} - {self.date} - {self.time_slot}"

class DoctorLeave(models.Model):
    LEAVE_CHOICES = [
        ('full_day', 'Full Day'),
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ]

    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICES)
    date = models.DateField()
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)  # Add this field

    def __str__(self):
        return f"{self.doctor.username} - {self.leave_type} Leave - {self.date}"



class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    method_choices = [('hospital', 'Hospital Method'), ('online', 'Online Method')]
    method = models.CharField(max_length=100, choices=method_choices)
    otp = models.CharField(max_length=6)
    
    # Add other fields related to the payment, such as transaction ID, amount, etc.

    def __str__(self):
        return f"{self.appointment.user.first_name} - {self.appointment.date} - {self.method}"
    

  
class Brand(models.Model):
    brand_logo = models.ImageField(upload_to='brand_logos/')
    brand_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    agent_email = models.EmailField()
    agent_phone = models.CharField(max_length=15)
    brand_license = models.FileField(upload_to='brand_licenses/', default='default_license.pdf')

    def __str__(self):
     return self.brand_name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class SkinConcern(models.Model):
    SKIN_CONCERN_CHOICES = [
        ('dryness', 'Dryness'),
        ('oiliness', 'Oiliness'),
        ('sensitivity', 'Sensitivity'),
        ('acne', 'Acne'),
        ('Eczema','Eczema'),
        ('Wrinkles','Wrinkles'),
        ('Pigmentation','Pigmentation'),
        ('Sun Damage','Sun Damage'),
        ('Dryness','Dryness'),
        ('Dull Skin','Dull Skin'),
        ('Dark Circles','Dark Circles'),
        ('Age spots','Age spots'),
        ('Acne Scars','Acne Scars'),
        ('Oily scalp','Oily scalp'),
        ('Dry hair','Dry hair'),
        ('Dandruff','Dandruff'),
        ('Breakage and split ends','Breakage and split ends'),

        # Add more options as needed
    ]

    name = models.CharField(max_length=200, choices=SKIN_CONCERN_CHOICES)

    def __str__(self):
        return self.name

from django.core.exceptions import ValidationError
from django.db.models import Sum

class Product(models.Model):
    image = models.ImageField(upload_to='products/', default='assets/img/product_default.png')
    name = models.CharField(max_length=100)
    quality = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.TextField(default=True)  # New field for ingredients
    description = models.TextField()
    weight = models.CharField(max_length=50,default=True)  # Add the weight field
    created_date = models.DateTimeField(auto_now_add=True)  # New field for creation date
    highlights = models.CharField(max_length=100,default=True)
    SKIN_TYPE_CHOICES = [
        ('dry', 'Dry'),
        ('oily', 'Oily'),
        ('normal', 'Normal'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('mature', 'Mature'),
        ('all skintype','all skintype'),


    ]
    skin_type = models.CharField(max_length=50, choices=SKIN_TYPE_CHOICES, default='normal')  # Add skin type field
    skin_concerns = MultiSelectField(max_length=50,choices=SkinConcern.SKIN_CONCERN_CHOICES,default=True)
    
    AGE_LIMIT_CHOICES = [
        ('above_10', 'Above 10'),
        ('below_5', 'Below 5'),
        ('above_18', 'Above 18'),
        ('above_15', 'Above 15'),
        ('below_12', 'Below 12'),
        ('above_21', 'Above 21'),
        ('all', 'All'),
    ]
    age_limit = models.CharField(max_length=50,choices=AGE_LIMIT_CHOICES,default=True)

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def clean(self):
        super().clean()
        # Ensure that only jpg, png, and jpeg files are allowed for the image field
        if self.image:
            if not self.image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Only JPG, JPEG, and PNG files are allowed for the image.')
   

    def __str__(self):
        return self.name

      
    
 
    
from django.utils import timezone


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    def is_out_of_stock(self):
        return self.quantity > self.product.remaining_quantity()

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"

CustomUser.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
CustomUser.cart = property(lambda u: Cart.objects.get_or_create(user=u)[0])


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    ]


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='PENDING')

    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    

class UserAddress(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.address
    

from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField()
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.street_address}"
    
# models.py

from django.db import models

class DeliveryUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)  # We will store the password hash here
    def __str__(self):
        return self.username


# models.py
from django.db import models

class Service(models.Model):
    image = models.ImageField(upload_to='service_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    procedure = models.TextField()
    post_procedure = models.TextField()
    highlights = models.CharField(max_length=100)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=500)  # Adding advance_payment field

    def __str__(self):
        return self.name


class Prescription(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.ForeignKey(Product, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
   

    def __str__(self):
        return f"Prescription for {self.appointment.user.first_name} - {self.appointment.doctor.first_name} - {self.appointment.date} - {self.appointment.time_slot}"
    
from django.db import models
from .models import Appointment, Service

class ServiceSuggest(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='suggested_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE,default='no treatment needed')

    def __str__(self):
        return f"Suggested Service for {self.appointment.user.first_name} by {self.appointment.doctor.first_name}: {self.service.name}"
    
class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.booking_date} - {self.time_slot}"

class TimeSlot(models.Model):
    
    date = models.DateField()
    time_slot = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.service.name} - {self.date} - {self.time_slot}"
    

class servicePayment(models.Model):
    PENDING = 'pending'
    COMPLETE = 'complete'
    PAYMENT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)  # You may adjust the length as per your requirements
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"Payment for {self.service.name} by {self.user.username}"
    

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content}"