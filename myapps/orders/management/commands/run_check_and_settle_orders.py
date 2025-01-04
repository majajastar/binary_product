from django.core.management.base import BaseCommand
from myapps.orders.tasks import check_and_settle_orders

class Command(BaseCommand):
    help = "Manually runs the check_and_settle_orders task"

    def handle(self, *args, **kwargs):
        result = check_and_settle_orders()
        self.stdout.write(self.style.SUCCESS(f"Task completed: {result}"))
