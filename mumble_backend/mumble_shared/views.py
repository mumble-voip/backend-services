from django.http import HttpRequest, JsonResponse
from django.apps import apps

import hashlib


def hash_token(token: str) -> str:
    digest = hashlib.blake2b(digest_size=64)
    digest.update(str.encode(token))
    return digest.hexdigest()


def toJsonResponse(message: str, status: int = 200, obj: dict = dict()) -> JsonResponse:
    return JsonResponse(
        dict(obj, **{"message": message, "status": status}), status=status
    )


# Returns a tuple containing a bool, whether or not the connection is authorized.
# And additionally an error JsonResponse, if it is not.
def authorized(request: HttpRequest) -> tuple[bool, JsonResponse]:
    token = request.GET.get("token", None)

    if not token:
        return False, toJsonResponse("Unauthorized", 401)

    if not hash_token(token) in apps.get_app_config("mumble_shared").AUTHORIZED_HASHES:
        return False, toJsonResponse("Unauthorized", 401)

    return True, None


# Returns a tuple containing the major and minor version components parsed from the string
# If parsing failes, major and minor will be None and the third element in the tuple will
# contain an error JsonResponse.
def parseSeries(series: str) -> tuple[int, int, JsonResponse]:
    if series.count(".") != 1:
        return (
            None,
            None,
            toJsonResponse("Invalid parameter: series. Format: <major>.<minor>", 400),
        )

    major, minor = series.split(".")

    if not major.isnumeric() or not minor.isnumeric():
        return (
            None,
            None,
            toJsonResponse("Invalid parameter: series. Format: <major>.<minor>", 400),
        )

    major = int(major)
    minor = int(minor)

    return major, minor, None
