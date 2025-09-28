import csv
from django.core.management.base import BaseCommand
from d3app.models import Student  # Giả sử bạn có model Student

class Command(BaseCommand):
    help = 'Import data from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Student.objects.create(
                        name=row['name'],
                        gender=row['gender']
                    )
            self.stdout.write(self.style.SUCCESS('Dữ liệu đã được nhập thành công!'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Không tìm thấy file CSV!'))