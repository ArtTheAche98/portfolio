from django import forms


class TranslateForm(forms.Form):
    term = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter a medical term"})
    )
    target_language = forms.ChoiceField(
        choices=[
            ("ka", "Georgian"),
            ("lat", "Latin"),
            ("en", "English"),
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
