# library/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Review


class UserRegisterForm(UserCreationForm):
    """
    A custom form for user registration.
    """
    email = forms.EmailField(required=True)
    bio = forms.CharField(widget=forms.Textarea, max_length=500, required=False, label="Bio")

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        """
        Overrides the save method to create a UserProfile after the User is created.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create a user profile for the new user
            UserProfile.objects.create(
                user=user,
                bio=self.cleaned_data['bio']
            )
        return user

class SignInForm(AuthenticationForm):
    """
    A custom form for user sign-in, based on Django's built-in AuthenticationForm.
    """
    pass

class ReviewForm(forms.ModelForm):
    """
    A form for users to submit a rating and review for a book.
    """
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        labels = {
            'rating': 'Your Rating (1-5)',
            'review_text': 'Your Review',
        }
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }

