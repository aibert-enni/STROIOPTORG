from apps.product.models import AttributeValue

def get_nested_categories(categories, parent=None):
    nested = []
    for category in categories:
        if category.parent == parent:
            children = get_nested_categories(categories, parent=category)
            nested.append({
                'id': category.id,
                'name': category.name,
                'url': category.slug,
                'children': children
            })
    return nested

def get_filter(attribute, products):
    return AttributeValue.objects.filter(attribute=attribute, product_attributes__product__in=products).only('value').distinct()
