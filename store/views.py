from django.views.generic import ListView, CreateView, DetailView, UpdateView,DeleteView
from django.urls import reverse_lazy
from store.models import Card
from store.forms import CardModelForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from decimal import Decimal

class CardsView(ListView):
    model = Card
    template_name = 'cards.html'
    context_object_name = 'cards'
    paginate_by = 40
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dollar = Decimal(str(5.20))
        for card in context["cards"]:
            card.price = (card.price * dollar).quantize(Decimal("0.01"))

        return context
    
    def get_queryset(self):
        cards = super().get_queryset().order_by('name')
        search_query = self.request.GET.get('search')
        if search_query:
            cards = cards.filter(name__icontains=search_query)
        return cards

class DetailCardView(DetailView):
    model = Card
    template_name = 'detail_card.html'
    context_object_name = 'card'

class NewCardView(CreateView):
    model = Card
    form_class = CardModelForm
    template_name = 'new_card.html'
    success_url = reverse_lazy("cards")

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class UpdateCardView(UpdateView):
    model = Card
    form_class = CardModelForm
    template_name = 'update_card.html'

    def get_success_url(self):
        return reverse_lazy('card_detail', kwargs={'pk': self.object.pk})

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
class DeleteCardView(DeleteView):
    model = Card
    template_name = 'delete_card.html'
    success_url = reverse_lazy("cards")

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
