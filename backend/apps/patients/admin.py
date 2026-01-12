"""
Admin configuration for Patient app.
"""
from django.contrib import admin
from apps.patients.models import Patient, Address, EmergencyContact


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    can_delete = False


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 1


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "national_id",
        "phone_number",
        "gender",
        "age",
        "is_active",
        "enrolled_date",
    ]
    list_filter = ["is_active", "gender", "language_preference", "enrolled_date"]
    search_fields = [
        "first_name",
        "last_name",
        "national_id",
        "phone_number",
        "email",
    ]
    readonly_fields = ["enrolled_date", "updated_at", "age"]
    inlines = [AddressInline, EmergencyContactInline]
    
    fieldsets = (
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "first_name_kinyarwanda",
                "last_name_kinyarwanda",
                "date_of_birth",
                "gender",
            )
        }),
        ("Identification & Contact", {
            "fields": (
                "national_id",
                "phone_number",
                "alt_phone_number",
                "email",
            )
        }),
        ("Medical Information", {
            "fields": ("blood_type",)
        }),
        ("Communication Preferences", {
            "fields": (
                "language_preference",
                "prefers_sms",
                "prefers_whatsapp",
            )
        }),
        ("Status & Metadata", {
            "fields": (
                "is_active",
                "enrolled_by",
                "enrolled_date",
                "updated_at",
            )
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["patient", "province", "district", "sector", "cell", "village"]
    list_filter = ["province", "district"]
    search_fields = ["patient__first_name", "patient__last_name", "village"]


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["full_name", "patient", "relationship", "phone_number", "is_primary"]
    list_filter = ["relationship", "is_primary"]
    search_fields = ["full_name", "patient__first_name", "patient__last_name"]
