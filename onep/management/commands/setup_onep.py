from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from onep.models import Urun
from decimal import Decimal
import os


class Command(BaseCommand):
    help = 'Create superuser and sample products for ONEP e-commerce'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-fixture',
            action='store_true',
            help='Load data from fixture_data.json file instead of creating new data',
        )

    def handle(self, *args, **kwargs):
        use_fixture = kwargs['use_fixture']
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='burakcantaspinar').exists():
            User.objects.create_superuser(
                username='burakcantaspinar',
                email='admin@example.com',
                password='Selam.235689.'
            )
            self.stdout.write(self.style.SUCCESS('Superuser "burakcantaspinar" başarıyla oluşturuldu!'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "burakcantaspinar" zaten mevcut.'))

        # Create sample products if there are none
        if Urun.objects.count() == 0:
            sample_products = [
                {
                    'urun_adi': 'iPhone 15 Pro Max',
                    'aciklama': 'Apple iPhone 15 Pro Max, 256GB, Titanyum Mavi. A17 Pro cip.',
                    'fiyat': Decimal('52999.99'),
                    'stok_adedi': 20,
                    'kategori': 'Telefon',
                    'resim_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400'
                },
                {
                    'urun_adi': 'MacBook Air M3',
                    'aciklama': 'Apple MacBook Air 15 inc, M3 chip, 512GB SSD, 16GB RAM.',
                    'fiyat': Decimal('42999.99'),
                    'stok_adedi': 15,
                    'kategori': 'Laptop',
                    'resim_url': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400'
                },
                {
                    'urun_adi': 'Dell XPS 13',
                    'aciklama': 'Dell XPS 13 Plus, Intel i7-13700H, 16GB RAM, 1TB SSD.',
                    'fiyat': Decimal('38999.99'),
                    'stok_adedi': 12,
                    'kategori': 'Laptop',
                    'resim_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'
                },
                {
                    'urun_adi': 'Sony WH-1000XM5',
                    'aciklama': 'Sony premium noise cancelling kulaklik. 30 saat batarya.',
                    'fiyat': Decimal('3999.99'),
                    'stok_adedi': 40,
                    'kategori': 'Kulaklik',
                    'resim_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'
                },
                {
                    'urun_adi': 'Apple Watch Series 9',
                    'aciklama': 'Apple Watch Series 9, 45mm, GPS + Cellular, Spor Kordon.',
                    'fiyat': Decimal('14999.99'),
                    'stok_adedi': 30,
                    'kategori': 'Akilli Saat',
                    'resim_url': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400'
                },
                {
                    'urun_adi': 'Nike Air Max 270',
                    'aciklama': 'Nike Air Max 270 erkek spor ayakkabi. Siyah/Beyaz renk.',
                    'fiyat': Decimal('2299.99'),
                    'stok_adedi': 50,
                    'kategori': 'Ayakkabi',
                    'resim_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'
                },
                {
                    'urun_adi': 'Samsung Galaxy S23',
                    'aciklama': 'Yeni nesil Samsung Galaxy S23 akilli telefon, 6.1 inc Dynamic AMOLED 2X ekran.',
                    'fiyat': Decimal('21999.99'),
                    'stok_adedi': 50,
                    'kategori': 'Telefon',
                    'resim_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400'
                },
                {
                    'urun_adi': 'AirPods Pro 2',
                    'aciklama': 'Apple AirPods Pro 2. nesil, aktif gurultu engelleme.',
                    'fiyat': Decimal('6999.99'),
                    'stok_adedi': 35,
                    'kategori': 'Kulaklik',
                    'resim_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400'
                },
                {
                    'urun_adi': 'iPad Pro 12.9',
                    'aciklama': 'Apple iPad Pro 12.9 inc, M2 chip, 256GB WiFi + Cellular.',
                    'fiyat': Decimal('35999.99'),
                    'stok_adedi': 18,
                    'kategori': 'Tablet',
                    'resim_url': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400'
                }
            ]

            for product_data in sample_products:
                Urun.objects.create(**product_data)
                
            self.stdout.write(self.style.SUCCESS(f'{len(sample_products)} adet ornek urun basariyla olusturuldu!'))
        else:
            self.stdout.write(self.style.WARNING(f'Veritabaninda zaten {Urun.objects.count()} adet urun mevcut.'))
