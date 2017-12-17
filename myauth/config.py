from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from mainapp.models import Product


buyer_group = Group.objects.create(name='buyer_group')
content_type = ContentType.objects.get_for_model(Product)
add_product_permission = Permission.objects.create(
    codename='can_add_product',
    name='Can Add Product',
    content_type=content_type,
)
buyer_group.permissions.add(add_product_permission)
print "TEST!!!"

seller_group = Group.objects.get_or_create(name='seller_group')