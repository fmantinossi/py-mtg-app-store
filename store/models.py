import uuid
from django.db import models

class Set(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    set_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=10)
    code = models.CharField(max_length=10)
    release_date = models.DateField()
    
    def __str__(self):
        return str(self.name)

class CardType(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    card_type_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.name)

class CardSubtype(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    card_subtype_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.name)

class CardColor(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    card_color_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.name)

class CardRarity(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    card_rarity_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.name)

class CardImage(models.Model):
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    card_image_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    image_file = models.ImageField(upload_to='card_images/', null=True, blank=True)
    
    def __str__(self):
        return str(self.name)
        
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    objects = models.Manager()
    card_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    mana_cost = models.CharField(max_length=200)
    cmc = models.IntegerField()
    colors = models.ForeignKey(CardColor, on_delete=models.CASCADE)
    type_line = models.CharField(max_length=200)
    oracle_text = models.TextField()
    power = models.IntegerField()
    toughness = models.IntegerField()
    rarity = models.ForeignKey(CardRarity, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    image = models.ForeignKey(CardImage, on_delete=models.CASCADE)
    types = models.ForeignKey(CardType, on_delete=models.CASCADE)
    subtypes = models.ForeignKey(CardSubtype, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.name)