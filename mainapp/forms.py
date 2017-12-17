from django.forms import ModelForm
from mainapp.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'requirement', 'stock',
                  'limit_per_day', 'must_review', ]

