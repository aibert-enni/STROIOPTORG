from django_elasticsearch_dsl import Document, TextField, NestedField, IntegerField

from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer

from apps.product.models import Product


autocomplete_analyzer = analyzer('autocomplete_analyzer',
            tokenizer=tokenizer('trigram', 'ngram', min_gram=2, max_gram=10),
            filter=['lowercase']
        )

@registry.register_document
class ProductDocument(Document):
    name = TextField(analyzer=autocomplete_analyzer)

    product_attributes = NestedField(
        properties={
            'attribute_value': TextField()
        }
    )

    price = IntegerField()

    class Index:
        name = 'product'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_ngram_diff': 20
        }

    class Django:
        model = Product
        fields = ['created_at']

    def prepare_price(self, instance):
        return instance.get_discount_price

    def prepare_product_attributes(self, instance):
        return [
            {
                'attribute_value': attr.attribute_value.value
            }
            for attr in instance.product_attributes.all()
        ]