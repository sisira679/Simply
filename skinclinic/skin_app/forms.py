from django import forms
from .models import CustomUser
from .models import UserProfile
from .models import Specializations
from .models import Appointment
from .models import Payment
from .models import DoctorSchedule
from django.contrib.auth import get_user_model
from .models import Category



class DoctorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password= forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name','role','gender']

class PharmacistForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password= forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name','role','gender']



class SpecializationsForm(forms.ModelForm):
    class Meta:
        model = Specializations
        fields = ['specializations'] 


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phonenumber','address','dob','age','state','bloodgroup']

    def clean_phonenumber(self):
        phonenumber = self.cleaned_data.get('phonenumber')
        if UserProfile.objects.filter(phonenumber=phonenumber).exists():
            raise forms.ValidationError("Phone number already exists. Please use a different phone number.")
        return phonenumber


# class DateSelectionForm(forms.Form):
#     date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
      

class DateSelectionForm(forms.Form):
    date = forms.DateField           
    selected_slot = forms.CharField(max_length=100, required=False)  # Make it optional
    
    # (widget=forms.DateInput(attrs={'type': 'date'}))

class AppointmentForm(forms.Form):
    User = get_user_model()

    try:
        user = User.objects.get(username='username')  # Replace 'username' with the actual username
        profile = UserProfile.objects.get(user=user)

        patient_name = forms.CharField(label='Patient Name', initial=user.first_name)
        phone_number = forms.CharField(label='Phone Number', initial=profile.phonenumber)
        email = forms.EmailField(label='Email', initial=user.email)
    except User.DoesNotExist:
        # Handle the case where the user does not exist, perhaps by redirecting to an error page
        pass

    payment_method = forms.ChoiceField(
        label='Payment Method',
        choices=[('online', 'Pay Online'), ('hospital', 'Pay at Hospital')],
        widget=forms.RadioSelect(),
    )
class EditDoctorForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender']

class EditSpecializationsForm(forms.ModelForm):
    class Meta:
        model = Specializations
        fields = ['specializations']




# # forms.py
# class AppointmentForm(forms.Form):
#     date = forms.DateField()
#     time_slot = forms.CharField(max_length=100, widget=forms.HiddenInput())
#     reason = forms.CharField(max_length=255, widget=forms.Textarea)

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time_slot', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'style': 'width: 50%;'}),
            'reason': forms.Textarea(attrs={'rows': 5, 'cols': 30, 'style': 'resize: none; padding: 8px; box-sizing: border-box;'}),
        }
from .models import DoctorLeave


class LeaveForm(forms.ModelForm):
    class Meta:
        model = DoctorLeave
        fields = ['leave_type', 'date', 'reason']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 5, 'cols': 30, 'style': 'resize: none; padding: 8px; box-sizing: border-box;'}),
        }


# from django.forms import inlineformset_factory
# from .models import Prescription, Appointment

# class PrescriptionForm(forms.ModelForm):
#     class Meta:
#         model = Prescription
#         fields = ['medicine', 'dosage', 'duration']

# # PrescriptionFormSet = inlineformset_factory(Appointment, Prescription, form=PrescriptionForm, extra=1)
# PrescriptionFormSet = inlineformset_factory(Appointment, Prescription, form=PrescriptionForm, extra=1, can_delete=False)

from django import forms
from .models import Prescription, Service

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [ 'medicine', 'dosage', 'duration']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method']


# forms.py
from django import forms
from .models import Brand

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'agent_name', 'agent_email', 'agent_phone', 'brand_logo', 'brand_license']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Category with this name already exists.")
        return name
from .models import Subcategory

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name']

from .models import Product

# forms.py
from django import forms
from .models import Product, Subcategory

from django.core.exceptions import ValidationError
from .models import Product



   
    
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields in the form
    def clean_quality(self):
        quality = self.cleaned_data.get('quality')

        # Check if quality is zero or negative
        if quality <= 0:
            raise ValidationError("Quality must be a positive integer greater than zero.")

        return quality
    
from django import forms
from .models import UserAddress

class UserAddressForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    district = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))  # Add district field
    pincode = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = UserAddress
        fields = ['address', 'city', 'state', 'district', 'pincode', 'phone_number']


# forms.py
from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'apartment_address', 'country', 'zip']

# forms.py
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()


from django import forms
from .models import DeliveryUser

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = DeliveryUser
        fields = ['name', 'email', 'phone_number', 'username']

from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

# forms.py
from django import forms
from .models import ServiceSuggest, Service

class ServiceSuggestForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label="No Treatment Needed", required=False)

    class Meta:
        model = ServiceSuggest
        fields = ['service']
# forms.py

from django import forms
from .models import TimeSlot

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['date', 'time_slot']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class DeliveryBoyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'gender', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        # Clear errors for all fields
        self._errors.clear()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DeliveryBoy'
        if commit:
            user.save()
            user.set_password(get_user_model().objects.make_random_password())
            user.save()
        return user
