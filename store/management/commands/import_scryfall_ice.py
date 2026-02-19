import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Set, Card, CardType, CardSubtype, CardColor, CardRarity, CardImage
from dateutil import parser

class Command(BaseCommand):
    help = 'Imports Ice Age cards from Scryfall'

    def handle(self, *args, **options):
        self.stdout.write('Starting import...')
        
        # 1. Fetch data
        # Scryfall API search for Ice Age block
        # Using pagination loop just in case, though Ice Age is small enough for a few pages
        
        url = "https://api.scryfall.com/cards/search?q=block:ice"
        has_more = True
        
        while has_more:
            response = requests.get(url)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Error fetching data: {response.status_code}'))
                return

            data = response.json()
            cards = data.get('data', [])
            
            for card_data in cards:
                try:
                    self.process_card(card_data)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing card {card_data.get('name')}: {e}"))

            has_more = data.get('has_more', False)
            url = data.get('next_page')
            
        self.stdout.write(self.style.SUCCESS('Import completed successfully'))

    def process_card(self, data):
        # Skip tokens or non-paper if necessary, but query handles most
        if data.get('layout') in ['token', 'art_series']:
            return

        # 1. Set
        set_code = data.get('set')
        set_name = data.get('set_name')
        set_id = data.get('set_id')
        release_date = data.get('released_at')
        
        set_obj, _ = Set.objects.get_or_create(
            code=set_code,
            defaults={
                'name': set_name,
                'short_name': set_code.upper(), # customized
                'set_id': set_id,
                'release_date': release_date
            }
        )
        
        # 2. Colors (Take first or Colorless)
        colors = data.get('colors', [])
        color_name = 'Colorless'
        if colors:
            # Map codes to names if desired, or just use code
            # W, U, B, R, G
            color_map = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
            color_code = colors[0]
            color_name = color_map.get(color_code, color_code)
            
        color_obj, _ = CardColor.objects.get_or_create(name=color_name)
        
        # 3. Rarity
        rarity_name = data.get('rarity', 'common').title()
        rarity_obj, _ = CardRarity.objects.get_or_create(name=rarity_name)
        
        # 4. Type & Subtype
        type_line = data.get('type_line', '')
        # Split by em-dash
        if '—' in type_line:
            parts = type_line.split('—')
            t_part = parts[0].strip()
            s_part = parts[1].strip() if len(parts) > 1 else ''
        else:
            t_part = type_line
            s_part = ''
            
        # further split types by space (Category)
        main_type = t_part.split(' ')[-1] if t_part else 'Unknown'
        type_obj, _ = CardType.objects.get_or_create(name=main_type)
        
        subtype_obj = None
        if s_part:
            main_subtype = s_part.split(' ')[0]
            subtype_obj, _ = CardSubtype.objects.get_or_create(name=main_subtype)
        else:
             # Create a dummy subtype or handle null. Model implies FK is required (no null=True in view)
             # Let's check model again. 
             # models.ForeignKey(CardSubtype, on_delete=models.CASCADE) - implied required.
             # So we need a default subtype.
             subtype_obj, _ = CardSubtype.objects.get_or_create(name='None')

        # 5. Image
        image_uris = data.get('image_uris')
        if not image_uris and 'card_faces' in data:
             # check card faces for images
             if data['card_faces'] and 'image_uris' in data['card_faces'][0]:
                 image_uris = data['card_faces'][0]['image_uris']

        image_obj = None
        if image_uris:
            image_url = image_uris.get('normal') or image_uris.get('large')
            if image_url:
                # Check if exists by name to avoid redownloading?
                # Using card name + id as unique identifier for image name
                img_name = f"{data.get('id')}.jpg"
                
                # We create a new CardImage every time or reuse?
                # The model structure is Card -> Image. 
                # Let's Create one.
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_obj = CardImage.objects.create(name=data.get('name'))
                    image_obj.image_file.save(img_name, ContentFile(response.content))
                    image_obj.save()

        if not image_obj:
            # Fallback if no image found, but field is required?
            # models.ForeignKey(CardImage, ...) -> required
            image_obj, _ = CardImage.objects.get_or_create(name='Placeholder')


        # 6. Card
        # P/T handling
        power_str = data.get('power', '0')
        toughness_str = data.get('toughness', '0')
        
        def clean_pt(val):
            try:
                return int(val)
            except:
                return 0
        
        cmc = int(data.get('cmc', 0.0))
        price_str = data.get('prices', {}).get('usd', '0')
        if not price_str: price_str = '0'
        
        Card.objects.update_or_create(
            card_id=data.get('id'),
            defaults={
                'name': data.get('name'),
                'mana_cost': data.get('mana_cost', ''),
                'cmc': cmc,
                'colors': color_obj,
                'type_line': type_line,
                'oracle_text': data.get('oracle_text', ''),
                'power': clean_pt(power_str),
                'toughness': clean_pt(toughness_str),
                'rarity': rarity_obj,
                'set': set_obj,
                'image': image_obj,
                'types': type_obj,
                'subtypes': subtype_obj,
                'price': price_str
            }
        )
        self.stdout.write(f"Processed {data.get('name')}")
