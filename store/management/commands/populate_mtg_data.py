import os
import requests
import uuid
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Set, Card, CardColor, CardType, CardSubtype, CardRarity, CardImage

class Command(BaseCommand):
    help = 'Populate database with MTG cards from 1994 sets via Scryfall API'

    def handle(self, *args, **options):
        sets_to_import = [
            {'code': 'atq', 'name': 'Antiquities'},
            {'code': '3ed', 'name': 'Revised Edition'},
            {'code': 'leg', 'name': 'Legends'},
            {'code': 'drk', 'name': 'The Dark'},
            {'code': 'fem', 'name': 'Fallen Empires'}
        ]

        for set_info in sets_to_import:
            self.stdout.write(self.style.SUCCESS(f"Importing set: {set_info['name']} ({set_info['code']})"))
            
            # Fetch set data
            set_resp = requests.get(f"https://api.scryfall.com/sets/{set_info['code']}")
            if set_resp.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch set {set_info['code']}"))
                continue
            
            set_data = set_resp.json()
            
            # Create or update Set
            mtg_set, created = Set.objects.get_or_create(
                code=set_data['code'],
                defaults={
                    'name': set_data['name'],
                    'short_name': set_data['code'],
                    'release_date': datetime.strptime(set_data['released_at'], '%Y-%m-%d').date()
                }
            )

            # Fetch cards for the set
            cards_url = set_data['search_uri']
            while cards_url:
                cards_resp = requests.get(cards_url)
                if cards_resp.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"      Failed to fetch cards from {cards_url}"))
                    break
                
                cards_data = cards_resp.json()
                total_cards = len(cards_data.get('data', []))
                for idx, card_data in enumerate(cards_data.get('data', []), 1):
                    # Skip cards without images
                    if 'image_uris' not in card_data:
                        continue
                    
                    self.stdout.write(f"  [{idx}/{total_cards}] Processing : {card_data['name']}")
                    
                    try:
                        # Colors
                        color_names = {
                            'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'
                        }
                        colors = card_data.get('colors', [])
                        if len(colors) == 0:
                            color_name = 'Colorless'
                        elif len(colors) > 1:
                            color_name = 'Multicolor'
                        else:
                            color_name = color_names.get(colors[0], 'Unknown')
                        
                        card_color, _ = CardColor.objects.get_or_create(name=color_name)

                        # Rarity
                        card_rarity, _ = CardRarity.objects.get_or_create(name=card_data['rarity'].capitalize())

                        # Types and Subtypes
                        type_line = card_data.get('type_line', '')
                        parts = type_line.split(' — ')
                        types_part = parts[0]
                        subtypes_part = parts[1] if len(parts) > 1 else 'None'
                        
                        # Using first type found
                        main_type = types_part.split(' ')[0]
                        card_type, _ = CardType.objects.get_or_create(name=main_type)
                        
                        # First subtype
                        main_subtype = subtypes_part.split(' ')[0]
                        card_subtype, _ = CardSubtype.objects.get_or_create(name=main_subtype)

                        # Download Image
                        image_url = card_data['image_uris']['normal']
                        image_name = f"{card_data['id']}.jpg"
                        
                        card_image, _ = CardImage.objects.get_or_create(name=card_data['name'])
                        if not card_image.image_file:
                            try:
                                img_resp = requests.get(image_url, timeout=10)
                                if img_resp.status_code == 200:
                                    card_image.image_file.save(image_name, ContentFile(img_resp.content), save=True)
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"    Failed to download image for {card_data['name']}: {e}"))

                        # Create Card
                        Card.objects.get_or_create(
                            name=card_data['name'],
                            set=mtg_set,
                            defaults={
                                'mana_cost': card_data.get('mana_cost', ''),
                                'cmc': int(card_data.get('cmc', 0)),
                                'colors': card_color,
                                'type_line': type_line,
                                'oracle_text': card_data.get('oracle_text', ''),
                                'power': int(card_data.get('power', 0)) if card_data.get('power', '').isdigit() else 0,
                                'toughness': int(card_data.get('toughness', 0)) if card_data.get('toughness', '').isdigit() else 0,
                                'rarity': card_rarity,
                                'image': card_image,
                                'types': card_type,
                                'subtypes': card_subtype,
                                'price': float(card_data.get('prices', {}).get('usd', 0) or 0)
                            }
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    Error processing {card_data['name']}: {e}"))

                cards_url = cards_data.get('next_page')

        self.stdout.write(self.style.SUCCESS("MTG data population complete!"))
