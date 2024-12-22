from django.db import models

class MinutePrice(models.Model):
    product_type = models.CharField(max_length=100)  # Add product_type field
    timestamp = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    class Meta:
        unique_together = ['product_type', 'timestamp']  # Ensures product_type + timestamp is unique

    def __str__(self):
        return f"{self.product_type} - {self.timestamp} - {self.open} - {self.close}"

class FiveMinutePrice(models.Model):
    product_type = models.CharField(max_length=100)  # Add product_type field
    timestamp = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    class Meta:
        unique_together = ['product_type', 'timestamp']  # Ensures product_type + timestamp is unique

    def __str__(self):
        return f"{self.product_type} - {self.timestamp} - {self.open} - {self.close}"

class FifteenMinutePrice(models.Model):
    product_type = models.CharField(max_length=100)  # Add product_type field
    timestamp = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    class Meta:
        unique_together = ['product_type', 'timestamp']  # Ensures product_type + timestamp is unique

    def __str__(self):
        return f"{self.product_type} - {self.timestamp} - {self.open} - {self.close}"

class HourPrice(models.Model):
    product_type = models.CharField(max_length=100)  # Add product_type field
    timestamp = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    class Meta:
        unique_together = ['product_type', 'timestamp']  # Ensures product_type + timestamp is unique

    def __str__(self):
        return f"{self.product_type} - {self.timestamp} - {self.open} - {self.close}"

class DayPrice(models.Model):
    product_type = models.CharField(max_length=100)  # Add product_type field
    timestamp = models.DateTimeField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    class Meta:
        unique_together = ['product_type', 'timestamp']  # Ensures product_type + timestamp is unique

    def __str__(self):
        return f"{self.product_type} - {self.timestamp} - {self.open} - {self.close}"
