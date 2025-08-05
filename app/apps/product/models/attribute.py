from django.db import models


class Attribute(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название', unique=True)
    filter_name = models.CharField(max_length=100, verbose_name='Название для фильтра', unique=True, null=True, blank=True)
    priority = models.IntegerField(default=100, verbose_name='Приоритет')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values", verbose_name="Характеристика")
    value = models.CharField(max_length=100, verbose_name="Значение")

    class Meta:
        unique_together = ("attribute", "value")  # Чтобы избежать дублирования значений для одной характеристики
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttribute(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="product_attributes", verbose_name="Товар")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, related_name="product_attributes", verbose_name="Значение атрибута")

    class Meta:
        unique_together = ("product", "attribute_value")  # Запрещает дублирование одной характеристики у продукта
        verbose_name = "Атрибут продукта"
        verbose_name_plural = "Атрибуты продуктов"

    def __str__(self):
        return f"{self.product.name} — {self.attribute_value}"

class FilterAttribute(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name='filter_attributes', verbose_name='Категория')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='filter_attributes', verbose_name='Атрибут')
    is_filterable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category}: {self.attribute}"

    class Meta:
        verbose_name = 'Атрибут для фильтра'
        verbose_name_plural = 'Атрибуты для фильтров'