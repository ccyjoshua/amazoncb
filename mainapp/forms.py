from django.forms import ModelForm
from mainapp.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'orig_price', 'discount', 'description', 'image', 'order_requirement',
                  'must_review', 'review_requirement', 'amazon_link', 'how_to_find', 'stock', 'limit_per_day', ]

