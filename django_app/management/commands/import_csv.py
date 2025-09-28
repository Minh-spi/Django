import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django_app.models import Customer, ProductGroup, Product, Order, OrderDetail

class Command(BaseCommand):
    help = 'Imports data from a specified CSV file into the database'

    def add_arguments(self, parser):
        # Thiết lập để lệnh nhận một tham số là đường dẫn file CSV
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be imported')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        # Xóa dữ liệu cũ để đảm bảo không bị trùng lặp khi chạy lại script
        # Thứ tự xóa rất quan trọng: xóa các bảng con trước, bảng cha sau.
        self.stdout.write('Clearing old data from the database...')
        OrderDetail.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        ProductGroup.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared old data.'))

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                self.stdout.write('Starting data import...')

                for row in reader:
                    # Bước 1: Tạo hoặc lấy Nhóm hàng (ProductGroup)
                    # Dùng get_or_create để tránh tạo bản ghi trùng lặp
                    group, _ = ProductGroup.objects.get_or_create(
                        group_code=row['Mã nhóm hàng'],
                        defaults={'group_name': row['Tên nhóm hàng']}
                    )

                    # Bước 2: Tạo hoặc lấy Khách hàng (Customer)
                    customer, _ = Customer.objects.get_or_create(
                        customer_id=row['Mã khách hàng'],
                        defaults={
                            'name': row['Tên khách hàng'],
                            'segment_code': row['Mã PKKH']
                        }
                    )

                    # Bước 3: Tạo hoặc lấy Mặt hàng (Product)
                    product, _ = Product.objects.get_or_create(
                        product_code=row['Mã mặt hàng'],
                        defaults={
                            'name': row['Tên mặt hàng'],
                            'group': group,
                            'unit_price': int(row['Đơn giá']) # Chuyển đổi sang số nguyên
                        }
                    )
                    
                    # Bước 4: Tạo hoặc lấy Đơn hàng (Order)
                    # Chuyển đổi chuỗi thời gian từ CSV thành đối tượng datetime
                    order_time_obj = datetime.strptime(row['Thời gian tạo đơn'], '%Y-%m-%d %H:%M:%S')
                    order, _ = Order.objects.get_or_create(
                        order_id=row['Mã đơn hàng'],
                        defaults={
                            'customer': customer,
                            'order_time': order_time_obj
                        }
                    )

                    # Bước 5: Tạo Chi tiết đơn hàng (OrderDetail)
                    # Dùng update_or_create để xử lý trường hợp một sản phẩm xuất hiện nhiều lần trong CSV cho cùng một đơn hàng
                    OrderDetail.objects.update_or_create(
                        order=order,
                        product=product,
                        defaults={'quantity': int(row['SL'])} # Cập nhật hoặc tạo với số lượng
                    )

            self.stdout.write(self.style.SUCCESS('Data has been successfully imported!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found at path: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))