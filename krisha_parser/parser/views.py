import logging
from json import JSONDecodeError

import requests
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from krisha_parser.parser.enum import RecordState
from krisha_parser.parser.models import Record


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def random_id(request):
    try:
        p = Record.objects.only("id", "kid").filter(state=RecordState.PENDING).order_by('?').first()
        return JsonResponse(
            {
                "kid": p.kid,
            },
            status=200,
        )
    except (Record.DoesNotExist, AttributeError):
        raise Http404("Record does not exist")


@require_http_methods(["GET"])
def random_approved_id(request):
    try:
        p = Record.objects.only("id", "kid").filter(state=RecordState.APPROVED).order_by('?').first()
        return JsonResponse(
            {
                "kid": p.kid,
            },
            status=200,
        )
    except (Record.DoesNotExist, AttributeError):
        raise Http404("Record does not exist")


@require_http_methods(["GET"])
def record_data(request, record_id):
    try:
        p = Record.objects.get(kid=record_id)
        resp = requests.get(f"https://m.krisha.kz/analytics/aPriceAnalysis/?id={p.kid}").json()

    except Record.DoesNotExist:
        raise Http404("Record does not exist")
    except JSONDecodeError:
        resp = {}
    return JsonResponse(
        {
            "id": p.id,
            "state": p.state,
            "photo": resp.get("advert", {}).get("photo", {}).get("3x"),
            "title": resp.get("advert", {}).get("title", "No data"),
            "kid": p.kid,
            "krisha_link": p.plain_link,
            "residential_complex": p.residential_complex,
            "floor": p.floor,
            "max_floor": p.max_floor,
            "post_date": p.post_date,
            "krisha_created_at": p.krisha_created_at,
            "full_address": p.full_address,
            "area": p.area,
            "description": p.description,
            "data": p.data,
            "comment": p.comment,
        },
        status=200,
    )


@require_http_methods(["PUT"])
@csrf_exempt
def like(request, record_id):
    try:
        p = Record.objects.only('id', "state").get(kid=record_id)
        p.state = RecordState.APPROVED
        p.save(update_fields=["state"])
    except Record.DoesNotExist:
        raise Http404("Record does not exist")
    return JsonResponse({"state": p.state}, status=200)


@require_http_methods(["PUT"])
@csrf_exempt
def dislike(request, record_id):
    try:
        p = Record.objects.only('id', "state").get(kid=record_id)
        p.state = RecordState.REJECTED
        logger.debug(f"Record found {p.__dict__}")
        p.save(update_fields=["state"])
    except Record.DoesNotExist:
        raise Http404("Record does not exist")
    return JsonResponse({"state": p.state}, status=200)
