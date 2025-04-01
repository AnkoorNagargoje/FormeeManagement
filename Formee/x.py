import os
import django

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Formee.settings')

# Initialize Django
django.setup()

# Import your models
from Stock.models import Product

# Fetch all Product objects and update them
products = Product.objects.all()
for product in products:
    if 'Puri' in product.name:
        product.name = product.name.replace('Puri', 'Mathri')
        product.save()

print("Replacement complete.")
