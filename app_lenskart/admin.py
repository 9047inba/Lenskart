from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Register)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Admin)

# ----------------------------prescription-------------------------


@admin.register(prescription)
class PrescriptionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "birth_year",
        "right_sph",
        "right_cyl",
        "right_axis",
        "left_sph",
        "left_cyl",
        "left_axis",
        "created_at"
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "birth_year",
    )

# @admin.register(glass_product)
# class GlassProductAdmin(admin.ModelAdmin):

#     list_display = (
#         "id",
#         "model_name",
#         "category_type",
#         "frame_size",
#         "price",
#         "structure_style",
#         "target_audience",
#         "collection_tier",
#         "includes_adjustable_nose_pad",
#         "created_at"
#     )

#     search_fields = (
#         "model_name",
#     )

#     list_filter = (
#         "category_type",
#         "frame_size",
#         "structure_style",
#         "target_audience",
#         "collection_tier",
#     )


@admin.register(glass_product)
class glassProductAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "product_name",
        "category_type",
        "frame_size",
        "price",
        "color",
        "like",
        "rating",
        "structure_style",
        "target_audience",
        "collection_tier",
        "includes_adjustable_nose_pad",
        "applicable_for_buy_one_get_one",
        "created_at",
    ]

    list_filter = [
        "category_type",
        "frame_size",
        "structure_style",
        "target_audience",
        "collection_tier",
        "like",
        "includes_adjustable_nose_pad",
        "applicable_for_buy_one_get_one",
    ]

    search_fields = [
        "product_name",
        "category_type",
        "color",
        "target_audience",
        "collection_tier",
    ]

    ordering = [
        "-created_at"
    ]
    