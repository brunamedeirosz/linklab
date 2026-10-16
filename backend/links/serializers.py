from rest_framework import serializers
from django.conf import settings
from django.core.validators import URLValidator
from django.urls import reverse
from urllib.parse import urlsplit
from .models import ShortLink


class ShortLinkSerializer(serializers.ModelSerializer):
    original_url = serializers.CharField(max_length=2048, validators=[
        URLValidator(schemes=['http', 'https'], message='Informe uma URL HTTP ou HTTPS válida.')
    ])
    short_url = serializers.SerializerMethodField()

    def validate_original_url(self, value):
        parsed = urlsplit(value)
        if parsed.username is not None or parsed.password is not None:
            raise serializers.ValidationError('Não inclua credenciais na URL.')
        return value

    def get_short_url(self, obj):
        path = reverse('redirect-short-link', args=[obj.short_code])
        if settings.SHORT_URL_BASE:
            return f'{settings.SHORT_URL_BASE}{path}'
        return self.context['request'].build_absolute_uri(path)

    class Meta:
        model = ShortLink

        fields = [
            "id",
            "original_url",
            "short_code",
            "created_at",
            "click_count",
            "short_url",
        ]

        read_only_fields = [
            "id",
            "short_code",
            "created_at",
            "click_count",
        ]
