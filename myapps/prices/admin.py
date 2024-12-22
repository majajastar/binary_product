from django.contrib import admin
from .models import MinutePrice
from datetime import datetime

class MinutePriceAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'timestamp', 'open', 'high', 'low', 'close')
    search_fields = ('product_type', 'timestamp')
    list_filter = ('product_type', 'timestamp')
    ordering = ('timestamp',)
    search_help_text = "Search by date/time: Year (2024), Year-Month (2024-12), Year-Month-Day (2024-12-23), Hour (2024-12-23 15), Hour:Minute (2024-12-23 15:30)."

    def get_search_results(self, request, queryset, search_term):
        search_may_have_duplicates = False  # Set a default for duplicates check

        if search_term:
            time_formats = [
                '%Y',                     # Year
                '%Y-%m',                  # Year-Month
                '%Y-%m-%d',               # Year-Month-Day
                '%Y-%m-%d %H',            # Year-Month-Day Hour
                '%Y-%m-%d %H:%M',         # Year-Month-Day Hour:Minute
            ]

            for time_format in time_formats:
                try:
                    # Attempt to parse the input search term
                    parsed_time = datetime.strptime(search_term, time_format)
                    
                    # Filter queryset based on the granularity of the time_format
                    if time_format == '%Y':
                        queryset = queryset.filter(timestamp__year=parsed_time.year)
                    elif time_format == '%Y-%m':
                        queryset = queryset.filter(
                            timestamp__year=parsed_time.year,
                            timestamp__month=parsed_time.month
                        )
                    elif time_format == '%Y-%m-%d':
                        queryset = queryset.filter(
                            timestamp__date=parsed_time.date()
                        )
                    elif time_format == '%Y-%m-%d %H':
                        queryset = queryset.filter(
                            timestamp__year=parsed_time.year,
                            timestamp__month=parsed_time.month,
                            timestamp__day=parsed_time.day,
                            timestamp__hour=parsed_time.hour
                        )
                    elif time_format == '%Y-%m-%d %H:%M':
                        queryset = queryset.filter(
                            timestamp__year=parsed_time.year,
                            timestamp__month=parsed_time.month,
                            timestamp__day=parsed_time.day,
                            timestamp__hour=parsed_time.hour,
                            timestamp__minute=parsed_time.minute
                        )

                    # Exit loop if parsing succeeds
                    break
                except ValueError:
                    # Try the next format if parsing fails
                    continue

        # Return the filtered queryset and the flag for possible duplicates
        return queryset, search_may_have_duplicates

# Register the model with the custom admin
admin.site.register(MinutePrice, MinutePriceAdmin)