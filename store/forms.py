from django import forms
from .models import Card, CardImage

class CardModelForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)

    class Meta:
        model = Card
        exclude = ['image']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            self.add_error('price', 'O preço deve ser maior do que 0.')
        return price

    def save(self, commit=True):
        card = super().save(commit=False)
        image_file = self.cleaned_data.get('image_file')

        if image_file:
            card_image = CardImage.objects.create(image_file=image_file, name=card.name)
            card.image = card_image
        
        if commit:
            card.save()

        return card