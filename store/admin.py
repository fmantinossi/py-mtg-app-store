from django.contrib import admin
from .models import Set, CardType, CardSubtype, CardColor, CardRarity, CardImage, Card

#Quando se usa o @admin.register, não precisa usar o admin.site.register no final do arquivo
@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'code', 'release_date')
    list_filter = ('release_date',)
    search_fields = ('name', 'short_name', 'code')

@admin.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(CardSubtype)
class CardSubtypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(CardColor)
class CardColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(CardRarity)
class CardRarityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(CardImage)
class CardImageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'mana_cost', 'cmc', 'colors', 'type_line', 'oracle_text', 'power', 'toughness', 'rarity', 'set', 'image', 'types', 'subtypes')
    list_filter = ('colors', 'rarity', 'set', 'types', 'subtypes')
    search_fields = ('name', 'mana_cost', 'type_line', 'oracle_text')
