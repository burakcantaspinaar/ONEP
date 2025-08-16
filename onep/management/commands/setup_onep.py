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
        
        if use_fixture:
            # Load data from fixture file
            fixture_path = 'fixture_data.json'
            if os.path.exists(fixture_path):
                self.stdout.write('Fixture dosyasından veriler yükleniyor...')
                call_command('loaddata', fixture_path)
                self.stdout.write(self.style.SUCCESS('Fixture verileri başarıyla yüklendi!'))
                return
            else:
                self.stdout.write(self.style.ERROR('Fixture dosyası bulunamadı, yeni veriler oluşturuluyor...'))
        
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
                    'urun_adi': 'Samsung Galaxy S23',
                    'aciklama': 'Yeni nesil Samsung Galaxy S23 akıllı telefon, 6.1 inç Dynamic AMOLED 2X ekran, 50MP kamera.',
                    'fiyat': Decimal('21999.99'),
                    'stok_adedi': 50,
                    'kategori': 'Elektronik',
                    'resim_url': 'https://images.samsung.com/is/image/samsung/p6pim/tr/2302/gallery/tr-galaxy-s23-s911-sm-s911bzgctur-534848783'
                },
                {
                    'urun_adi': 'Apple MacBook Pro M3',
                    'aciklama': 'Yeni Apple M3 işlemcili MacBook Pro, 16GB RAM, 512GB SSD ve 14 inç Retina ekran.',
                    'fiyat': Decimal('49999.99'),
                    'stok_adedi': 25,
                    'kategori': 'Bilgisayar',
                    'resim_url': 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/mbp14-spacegray-select-202310?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1697230830200'
                },
                {
                    'urun_adi': 'Sony WH-1000XM5',
                    'aciklama': 'Sony WH-1000XM5 gürültü engelleme özellikli kablosuz kulaklık. 30 saat pil ömrü.',
                    'fiyat': Decimal('7499.99'),
                    'stok_adedi': 100,
                    'kategori': 'Ses Sistemleri',
                    'resim_url': 'https://www.sony.com.tr/image/e9acc5f42e3d356efef9d3cc46d6f265?fmt=pjpeg&wid=330&bgcolor=FFFFFF&bgc=FFFFFF'
                },
                {
                    'urun_adi': 'Dyson V12 Detect Slim',
                    'aciklama': 'Dyson V12 Detect Slim Absolute kablosuz süpürge. Güçlü emiş ve lazer toz algılama.',
                    'fiyat': Decimal('14999.99'),
                    'stok_adedi': 30,
                    'kategori': 'Ev Aletleri',
                    'resim_url': 'https://dyson-h.assetsadobe2.com/is/image/content/dam/dyson/images/products/primary/394958-01.png'
                },
                {
                    'urun_adi': 'Nike Air Zoom Pegasus 40',
                    'aciklama': 'Nike Air Zoom Pegasus 40 koşu ayakkabısı. Reaktif yastıklama ve nefes alabilen üst malzeme.',
                    'fiyat': Decimal('2799.99'),
                    'stok_adedi': 75,
                    'kategori': 'Spor',
                    'resim_url': 'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/c08de082-0bd1-4ca6-9456-599d071636dd/pegasus-40-yol-koşu-ayakkabısı-jkV5Xq.png'
                },
            ]

            for product_data in sample_products:
                Urun.objects.create(**product_data)
                
            self.stdout.write(self.style.SUCCESS(f'{len(sample_products)} adet örnek ürün başarıyla oluşturuldu!'))
        else:
            self.stdout.write(self.style.WARNING('Veritabanında zaten ürünler mevcut.'))
