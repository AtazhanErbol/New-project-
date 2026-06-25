from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Booking
        fields = ['service', 'client_name', 'client_phone', 'client_email', 'comment']
        widgets = {
            'service': forms.HiddenInput(),
            'client_name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-input'}),
            'client_phone': forms.TextInput(attrs={'placeholder': '+7 XXX XXX XX XX', 'class': 'form-input'}),
            'client_email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Комментарий', 'class': 'form-input', 'rows': 3}),
        }

    def clean_honeypot(self):
        value = self.cleaned_data.get('honeypot')
        if value:
            raise forms.ValidationError('Bot detected')
        return value
