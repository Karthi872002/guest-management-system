from rest_framework import serializers

from gms.models import Guest


class GuestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guest
        fields = (
            "_id",
            "name",
            "email",
            "phone_number",
            "identification_number",
            "identification_type",
        )
        read_only_fields = ("_id",)
