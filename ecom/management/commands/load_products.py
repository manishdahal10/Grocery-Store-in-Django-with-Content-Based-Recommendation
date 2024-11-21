import csv
import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from ecom.models import Product, Category

class Command(BaseCommand):
    help = 'Load products data from CSV into the database'

    def handle(self, *args, **kwargs):
        # Path to your dataset CSV file (adjust if needed)
        csv_file_path = os.path.join('dataset', 'classes.csv')
        
        # Read the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Get or create the category using 'Category' choices
                category_name = row['Category'].lower()
                if category_name in dict(Category.CATEGORY_CHOICES).keys():
                    category, created = Category.objects.get_or_create(name=category_name)
                else:
                    self.stdout.write(self.style.ERROR(f"Category {category_name} is not valid. Skipping row."))
                    continue

                # Extract description file path and read its content
                description_file_path = row['Product Description Path (str)']
                
                # Remove leading '/' if it exists
                if description_file_path.startswith('/'):
                    description_file_path = description_file_path[1:]
                
                full_description_path = os.path.join('dataset', description_file_path)
                
                if os.path.exists(full_description_path):
                    with open(full_description_path, 'r', encoding='utf-8') as desc_file:
                        description = desc_file.read()
                else:
                    description = "Description not available"
                
                # Compare 'Class Name' and 'Coarse Class Name'
                class_name = row['Class Name (str)']
                coarse_class_name = row['Coarse Class Name (str)']
                
                if class_name == coarse_class_name:
                    product_name = class_name
                else:
                    product_name = f"{class_name} ({coarse_class_name})"
                
                # Set product image path
                product_image_path = row['Iconic Image Path (str)']
                
                # Remove leading '/' if it exists
                if product_image_path.startswith('/'):
                    product_image_path = product_image_path[1:]
                
                # Full image path with static/products/ folder
                full_image_path = os.path.join('dataset', product_image_path)

                # Debug: Print paths
                self.stdout.write(self.style.NOTICE(f"Product image path from CSV: {product_image_path}"))
                self.stdout.write(self.style.NOTICE(f"Full image path: {full_image_path}"))
                
                # Handle price and class_id
                class_id = int(row['Class ID (int)'])
                price = random.uniform(5.00, 100.00)  # Using random decimal for price
                
                # Create the Product record
                product = Product(
                    name=product_name,
                    description=description,
                    price=round(price, 2),
                    category=category,
                    class_id=class_id
                )
                
                # Save product first
                product.save()

                # Handle image upload
                if os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as img_file:
                        product.product_image.save(
                            os.path.basename(full_image_path),  # Set file name
                            File(img_file),
                            save=True
                        )
                else:
                    self.stdout.write(self.style.WARNING(f"Image file not found: {full_image_path}"))

        self.stdout.write(self.style.SUCCESS('Successfully loaded products into the database'))