from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from onep.models import Urun
from django.db import connection


class Command(BaseCommand):
    help = 'Check database status and content'

    def handle(self, *args, **kwargs):
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✅ Database connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {e}'))
            return

        # Check tables exist
        tables = connection.introspection.table_names()
        required_tables = ['onep_urun', 'auth_user']
        
        for table in required_tables:
            if table in tables:
                self.stdout.write(self.style.SUCCESS(f'✅ Table {table}: EXISTS'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Table {table}: MISSING'))

        # Check users
        try:
            user_count = User.objects.count()
            self.stdout.write(f'👥 Users in database: {user_count}')
            
            for user in User.objects.all():
                self.stdout.write(f'  - {user.username} (superuser: {user.is_superuser})')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ User check failed: {e}'))

        # Check products
        try:
            product_count = Urun.objects.count()
            self.stdout.write(f'🛍️ Products in database: {product_count}')
            
            for product in Urun.objects.all()[:5]:  # Show first 5
                self.stdout.write(f'  - {product.urun_adi} (Price: {product.fiyat} TL)')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Product check failed: {e}'))

        # Check migrations
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            plan = executor.migration_plan(targets)
            
            if plan:
                self.stdout.write(self.style.WARNING(f'⚠️ Pending migrations: {len(plan)}'))
                for migration in plan:
                    self.stdout.write(f'  - {migration[0]}.{migration[1]}')
            else:
                self.stdout.write(self.style.SUCCESS('✅ All migrations applied'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration check failed: {e}'))
