from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        if self.parent:
            return f'{self.name} {self.parent.name}'
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'