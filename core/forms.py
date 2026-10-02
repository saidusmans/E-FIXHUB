from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, AgentProfile, MechanicProfile, CustomerProfile, EWasteItem, RepairLog


# ═══════════════════════════════════════════════════════════════════
# BASE REGISTRATION FORM
# ═══════════════════════════════════════════════════════════════════

class BaseRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'input-premium'})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'example@email.com', 'class': 'input-premium'})
    )
    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '+91 9876543210', 'class': 'input-premium'})
    )
    state = forms.CharField(
        label="State",
        widget=forms.TextInput(attrs={'placeholder': 'Kerala', 'class': 'input-premium'})
    )
    district = forms.CharField(
        label="District",
        widget=forms.TextInput(attrs={'placeholder': 'Kochi', 'class': 'input-premium'})
    )
    address = forms.CharField(
        label="Full Address",
        widget=forms.Textarea(attrs={'placeholder': 'Street, City, ZIP', 'rows': 3, 'class': 'input-premium resize-none'}),
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone', 'state', 'district', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'input-premium'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'input-premium', 'placeholder': 'Create a strong password'})
        self.fields['password2'].widget.attrs.update({'class': 'input-premium', 'placeholder': 'Re-enter password'})
        self.fields['username'].widget.attrs.update({'class': 'input-premium', 'placeholder': 'Choose a username'})

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        parts = full_name.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.phone    = self.cleaned_data.get('phone')
        user.state    = self.cleaned_data.get('state')
        user.district = self.cleaned_data.get('district')
        user.address  = self.cleaned_data.get('address')
        if commit:
            user.save()
        return user


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER REGISTRATION FORM
# ═══════════════════════════════════════════════════════════════════

class CustomerRegistrationForm(BaseRegistrationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CUSTOMER'
        if commit:
            user.save()
            CustomerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': self.cleaned_data.get('full_name'),
                    'phone': self.cleaned_data.get('phone'),
                    'address': self.cleaned_data.get('address'),
                }
            )
        return user


# ═══════════════════════════════════════════════════════════════════
# AGENT REGISTRATION FORM
# ═══════════════════════════════════════════════════════════════════

class AgentRegistrationForm(BaseRegistrationForm):
    qualification   = forms.CharField(
        label="Qualification",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Diploma in Logistics', 'class': 'input-premium'})
    )
    experience      = forms.IntegerField(
        label="Years of Experience",
        widget=forms.NumberInput(attrs={'placeholder': '3', 'min': '0', 'class': 'input-premium'})
    )
    vehicle_details = forms.CharField(
        label="Vehicle Details",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Electric Van (KL-07-...)', 'class': 'input-premium'})
    )
    operation_zone = forms.CharField(
        label="Operation Zone (District)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Ernakulam', 'class': 'input-premium'})
    )
    id_proof_upload = forms.FileField(
        label="Upload ID Proof (PDF / Image)",
        required=True
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'AGENT'
        if commit:
            user.save()
            AgentProfile.objects.create(
                user=user,
                name=self.cleaned_data.get('full_name'),
                phone=self.cleaned_data.get('phone'),
                qualification=self.cleaned_data.get('qualification'),
                experience=self.cleaned_data.get('experience'),
                id_proof_upload=self.cleaned_data.get('id_proof_upload'),
                vehicle_details=self.cleaned_data.get('vehicle_details'),
                operation_zone=self.cleaned_data.get('operation_zone'),
                verification_status='Pending',
            )
        return user


# ═══════════════════════════════════════════════════════════════════
# MECHANIC REGISTRATION FORM
# ═══════════════════════════════════════════════════════════════════

class MechanicRegistrationForm(BaseRegistrationForm):
    specialization  = forms.CharField(
        label="Specialization",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Mobile Phones, Laptops', 'class': 'input-premium'})
    )
    qualification   = forms.CharField(
        label="Qualification",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. ITI Electronics', 'class': 'input-premium'})
    )
    workshop_address = forms.CharField(
        label="Workshop Address",
        widget=forms.Textarea(attrs={'placeholder': 'Full workshop address', 'rows': 3, 'class': 'input-premium resize-none'})
    )
    workstation_images = forms.ImageField(
        label="Workstation / Workshop Image",
        required=False
    )
    id_proof_upload = forms.FileField(
        label="Upload ID Proof (PDF / Image)",
        required=True
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'MECHANIC'
        if commit:
            user.save()
            MechanicProfile.objects.create(
                user=user,
                name=self.cleaned_data.get('full_name'),
                phone=self.cleaned_data.get('phone'),
                specialization=self.cleaned_data.get('specialization'),
                qualification=self.cleaned_data.get('qualification'),
                workshop_address=self.cleaned_data.get('workshop_address'),
                workstation_images=self.cleaned_data.get('workstation_images'),
                id_proof_upload=self.cleaned_data.get('id_proof_upload'),
                verification_status='Pending',
            )
        return user


# ═══════════════════════════════════════════════════════════════════
# E-WASTE UPLOAD FORM
# ═══════════════════════════════════════════════════════════════════

class EWasteUploadForm(forms.ModelForm):
    class Meta:
        model = EWasteItem
        fields = ['title', 'category', 'description', 'condition', 'image', 'collection_district', 'collection_address']
        widgets = {
            'title':               forms.TextInput(attrs={'placeholder': 'e.g. Industrial Rack Server A-100', 'class': 'input-premium'}),
            'category':            forms.Select(attrs={'class': 'input-premium'}),
            'description':         forms.Textarea(attrs={'placeholder': 'Provide detailed technical specifications and known failures...', 'rows': 4, 'class': 'input-premium resize-none'}),
            'condition':           forms.TextInput(attrs={'placeholder': 'e.g. Broken screen, no power', 'class': 'input-premium'}),
            'collection_district': forms.TextInput(attrs={'placeholder': 'e.g. Kochi', 'class': 'input-premium'}),
            'collection_address':  forms.Textarea(attrs={'placeholder': 'Complete street address for agent pickup...', 'rows': 3, 'class': 'input-premium resize-none'}),
        }


# ═══════════════════════════════════════════════════════════════════
# REPAIR LOG FORM (FOR MECHANICS)
# ═══════════════════════════════════════════════════════════════════

class RepairLogForm(forms.ModelForm):
    class Meta:
        model = RepairLog
        fields = ['repair_notes', 'cost']
        widgets = {
            'repair_notes': forms.Textarea(attrs={'placeholder': 'Describe what was repaired...', 'rows': 5, 'class': 'input-premium resize-none'}),
            'cost':         forms.NumberInput(attrs={'placeholder': 'e.g. 1500.00', 'step': '0.01', 'class': 'input-premium'}),
        }
