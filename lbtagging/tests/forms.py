from django import forms

from lbtagging.tests.models import Food, DirectFood, CustomPKFood, OfficialFood


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        exclude = ['tags_txt']

class DirectFoodForm(forms.ModelForm):
    class Meta:
        model = DirectFood
        exclude = ['tags_txt']

class CustomPKFoodForm(forms.ModelForm):
    class Meta:
        model = CustomPKFood
        exclude = ['tags_txt']

class OfficialFoodForm(forms.ModelForm):
    class Meta:
        model = OfficialFood
        exclude = ['tags_txt']
