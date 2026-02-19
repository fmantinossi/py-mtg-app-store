from django.views.generic import View
from django.shortcuts import render, redirect
from store.models import Card
from store.forms import CardModelForm


class CardsView(View):
    
    def get(self, request):
        cards = Card.objects.all().order_by('name')
        search_query = request.GET.get('search')
        if search_query:
            cards = cards.filter(name__icontains=search_query)
        return render(request, 'cards.html', {'cards': cards})

def new_card_view(request):
    if request.method == "POST":
        new_card_form = CardModelForm(request.POST, request.FILES)
        if new_card_form.is_valid():
            new_card_form.save()
            return redirect('cards')
    else:
        new_card_form = CardModelForm()
        
    return render(request, 'new_card.html', {'new_card_form': new_card_form})