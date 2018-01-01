from django.forms import ModelForm
from mainapp.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'orig_price', 'discount', 'description', 'image', 'requirement', 'amazon_link', 'how_to_find', 'stock',
                  'limit_per_day', ]

