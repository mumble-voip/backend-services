from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from mumble_shared.views import toJsonResponse

from . import views_v1 as V1

SUPPORTED_API_VERSIONS = {1: V1}


@csrf_exempt
def nothing(request: HttpRequest) -> JsonResponse:
    return toJsonResponse("Invalid API version", 400)


@csrf_exempt
def version(request: HttpRequest, version) -> JsonResponse:
    if not version in SUPPORTED_API_VERSIONS:
        return toJsonResponse("Invalid API version", 400)

    return SUPPORTED_API_VERSIONS[version].version(request)


@csrf_exempt
def version_series(request: HttpRequest, version, series: str) -> JsonResponse:
    if not version in SUPPORTED_API_VERSIONS:
        return toJsonResponse("Invalid API version", 400)

    return SUPPORTED_API_VERSIONS[version].version_series(request, series)


@csrf_exempt
def version_series_commit(
    request: HttpRequest, version, series: str, commit: str
) -> JsonResponse:
    if not version in SUPPORTED_API_VERSIONS:
        return toJsonResponse("Invalid API version", 400)

    return SUPPORTED_API_VERSIONS[version].version_series_commit(
        request, series, commit
    )
