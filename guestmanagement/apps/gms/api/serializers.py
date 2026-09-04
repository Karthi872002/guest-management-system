from rest_framework import serializers

from gms.models import Guest, Invitation, Visit


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


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'  # Includes all model fields
        read_only_fields = ['created_at', 'status', 'invitation_code']


class VisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visit
        fields = '__all__'  # Includes all model fields
        read_only_fields = ['created_at',
                            'check_in_time', 'check_out_time', 'status']
