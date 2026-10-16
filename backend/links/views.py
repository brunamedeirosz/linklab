import secrets
import string

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import throttle_classes
from django.views.decorators.http import require_safe
from rest_framework.response import Response
from .models import ShortLink
from .serializers import ShortLinkSerializer
from django.db.models import F
from .throttles import CreateLinkThrottle, StatisticsThrottle

ALPHABET = string.ascii_letters + string.digits
RESERVED_CODES = {'api', 'admin', 'static', 'media', 'health', 'assets'}


def generate_short_code():
    return "".join(secrets.choice(ALPHABET) for _ in range(7))


@api_view(["POST"])
@throttle_classes([CreateLinkThrottle])
def create_short_link(request):
    serializer = ShortLinkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    for _ in range(5):
        code = generate_short_code()
        if code.lower() in RESERVED_CODES:
            continue
        try:
            with transaction.atomic():
                link = ShortLink.objects.create(
                    original_url=serializer.validated_data["original_url"],
                    short_code=code,
                )
            break
        except IntegrityError:
            if ShortLink.objects.filter(short_code=code).exists():
                continue
            raise
    else:
        return Response(
            {"detail": "Não foi possível gerar um código único."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    response_data = ShortLinkSerializer(link, context={'request': request}).data

    return Response(
        response_data,
        status=status.HTTP_201_CREATED,
    )


@require_safe
def redirect_short_link(request, code):
    link = get_object_or_404(ShortLink, short_code=code)

    if request.method == 'GET':
        ShortLink.objects.filter(pk=link.pk).update(click_count=F('click_count') + 1)

    response = redirect(link.original_url)
    response['Cache-Control'] = 'no-store'
    return response

@api_view(["GET"])
@throttle_classes([StatisticsThrottle])
def link_statistics(request, code):
    link = get_object_or_404(
        ShortLink,
        short_code=code
    )

    serializer = ShortLinkSerializer(link, context={'request': request})

    return Response(serializer.data)
