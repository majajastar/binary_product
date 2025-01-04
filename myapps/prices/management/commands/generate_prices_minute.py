from django.core.management.base import BaseCommand
from myapps.prices.tasks import generate_prices_task

class Command(BaseCommand):
    help = "Generate day and minute price data for a given date range and store it in the database."

    def add_arguments(self, parser):
        parser.add_argument('product_type', type=str, help='Product name')
        parser.add_argument('start_date', type=str, help='Start date in format YYYY-MM-DD')

    def handle(self, *args, **kwargs):
        product_type = kwargs['product_type']
        start_date = kwargs['start_date']
        
        # Call the Celery task
        generate_prices_task.delay()
        self.stdout.write(self.style.SUCCESS(f"Task to generate prices for {product_type} starting from {start_date} has been queued."))
