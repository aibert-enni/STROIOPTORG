from django.contrib import admin

from apps.order.models import Order, OrderItem

# Создаем inline для отображения товаров в заказе
class OrderItemInline(admin.TabularInline):  # Можно использовать StackedInline для вертикального отображения
    model = OrderItem
    extra = 1  # Количество пустых форм для добавления новых товаров
    fk_name = 'order'  # Связь с моделью Order по полю foreign key

# Настройка админки для модели Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'created_at']  # Показать необходимые поля в списке
    inlines = [OrderItemInline]  # Добавляем inline с товарами

# Регистрация моделей в админке
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)