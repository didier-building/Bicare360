"""
Serializers for Patient app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.patients.models import Patient, Address, EmergencyContact

User = get_user_model()


class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyContact model."""

    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "full_name",
            "relationship",
            "phone_number",
            "alt_phone_number",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model."""

    class Meta:
        model = Address
        fields = [
            "id",
            "province",
            "district",
            "sector",
            "cell",
            "village",
            "latitude",
            "longitude",
            "street_address",
            "landmarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """Validate GPS coordinates if provided."""
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if (latitude is not None and longitude is None) or (
            latitude is None and longitude is not None
        ):
            raise serializers.ValidationError(
                "Both latitude and longitude must be provided together."
            )

        return data


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for patient lists."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "full_name",
            "national_id",
            "phone_number",
            "age",
            "gender",
            "is_active",
            "enrolled_date",
        ]


class PatientDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for patient with nested relationships."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    address = AddressSerializer(required=False, allow_null=True)
    emergency_contacts = EmergencyContactSerializer(many=True, required=False)
    enrolled_by_username = serializers.CharField(
        source="enrolled_by.username", read_only=True
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "first_name_kinyarwanda",
            "last_name_kinyarwanda",
            "full_name",
            "date_of_birth",
            "age",
            "gender",
            "national_id",
            "phone_number",
            "alt_phone_number",
            "email",
            "blood_type",
            "is_active",
            "enrolled_date",
            "updated_at",
            "enrolled_by_username",
            "prefers_sms",
            "prefers_whatsapp",
            "language_preference",
            "address",
            "emergency_contacts",
        ]
        read_only_fields = ["id", "enrolled_date", "updated_at", "enrolled_by_username"]

    def create(self, validated_data):
        """Create patient with nested address and emergency contacts."""
        address_data = validated_data.pop("address", None)
        emergency_contacts_data = validated_data.pop("emergency_contacts", [])

        # Set enrolled_by from request context
        validated_data["enrolled_by"] = self.context["request"].user

        patient = Patient.objects.create(**validated_data)

        # Create address if provided
        if address_data:
            Address.objects.create(patient=patient, **address_data)

        # Create emergency contacts if provided
        for contact_data in emergency_contacts_data:
            EmergencyContact.objects.create(patient=patient, **contact_data)

        return patient

    def update(self, instance, validated_data):
        """Update patient with nested address and emergency contacts."""
        address_data = validated_data.pop("address", None)
        emergency_contacts_data = validated_data.pop("emergency_contacts", None)

        # Update patient fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create address
        if address_data is not None:
            if hasattr(instance, "address"):
                for attr, value in address_data.items():
                    setattr(instance.address, attr, value)
                instance.address.save()
            else:
                Address.objects.create(patient=instance, **address_data)

        # Update emergency contacts if provided
        if emergency_contacts_data is not None:
            # Delete existing contacts and create new ones
            instance.emergency_contacts.all().delete()
            for contact_data in emergency_contacts_data:
                EmergencyContact.objects.create(patient=instance, **contact_data)

        return instance


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new patient (minimal fields)."""

    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "first_name_kinyarwanda",
            "last_name_kinyarwanda",
            "date_of_birth",
            "gender",
            "national_id",
            "phone_number",
            "alt_phone_number",
            "email",
            "blood_type",
            "prefers_sms",
            "prefers_whatsapp",
            "language_preference",
        ]

    def create(self, validated_data):
        """Create patient with enrolled_by from request."""
        validated_data["enrolled_by"] = self.context["request"].user
        return Patient.objects.create(**validated_data)

    def validate_national_id(self, value):
        """Validate national ID uniqueness."""
        if Patient.objects.filter(national_id=value).exists():
            raise serializers.ValidationError(
                "A patient with this National ID already exists."
            )
        return value
