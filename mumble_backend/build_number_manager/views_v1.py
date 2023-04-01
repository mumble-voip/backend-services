from django.http import HttpRequest, JsonResponse
from django.db.models import Max
from django.db.utils import IntegrityError

from mumble_shared.views import authorized, parseSeries, toJsonResponse

from .models import Series, Build

MIN_COMMIT_HASH_LENGTH = 40


def version(request: HttpRequest) -> JsonResponse:
    auth_success, auth_errorResponse = authorized(request)

    if not auth_success:
        return auth_errorResponse

    return toJsonResponse(
        "Invalid API endpoint. Supported API endpoints are:\n\nPOST /<series>/<commit_hash>\nGET /<series>/<commit_hash>\nGET /<series>",
        404,
    )


def version_series(request: HttpRequest, series: str) -> JsonResponse:
    auth_success, auth_errorResponse = authorized(request)

    if not auth_success:
        return auth_errorResponse

    if request.method != "GET":
        return toJsonResponse("Invalid method", 405)

    major, minor, series_error = parseSeries(series)
    if series_error != None:
        return series_error

    return listBuildsInSeries(major, minor)


def version_series_commit(
    request: HttpRequest, series: str, commit: str
) -> JsonResponse:
    auth_success, auth_errorResponse = authorized(request)

    if not auth_success:
        return auth_errorResponse

    major, minor, series_error = parseSeries(series)
    if series_error != None:
        return series_error

    if len(commit) < MIN_COMMIT_HASH_LENGTH:
        return toJsonResponse(
            "Invalid parameter: commit. Must be at least %i characters long"
            % (MIN_COMMIT_HASH_LENGTH),
            400,
        )

    if request.method == "POST":
        return createNewBuild(major, minor, commit)
    elif request.method == "GET":
        return getExistingBuild(major, minor, commit)
    else:
        return toJsonResponse(
            "Invalid method",
            405,
        )


def createNewBuild(major: int, minor: int, commit: str) -> JsonResponse:
    series, series_created = Series.objects.get_or_create(major=major, minor=minor)

    if not series_created:
        series_status = "Known series"
    else:
        series_status = "Unknown series"

    build_number = Build.objects.filter(series=series).aggregate(Max("build_number"))[
        "build_number__max"
    ]

    if build_number == None:
        build_number = 1
    else:
        build_number = build_number + 1

    if build_number > 0xFFFF:
        return toJsonResponse(
            "New build number exceeds Mumble protocol version bits!", 422
        )

    try:
        build = Build.objects.create(
            series=series, commit_hash=commit, build_number=build_number
        )
        build_status = "New build number created"
    except IntegrityError:
        return toJsonResponse("Commit does already exist in series!", 409)

    response = {
        "commit_hash": build.commit_hash,
        "series": series.__str__(),
        "series_id": series.id,
        "build_number": build.build_number,
        "series_created": series.created_on,
        "build_created": build.created_on,
    }

    return toJsonResponse("%s. %s." % (series_status, build_status), 201, response)


def getExistingBuild(major: int, minor: int, commit: str) -> JsonResponse:
    try:
        series = Series.objects.get(major=major, minor=minor)
    except Series.DoesNotExist:
        return toJsonResponse("Unknown series!", 404)

    try:
        build = Build.objects.get(series=series, commit_hash=commit)
    except Build.DoesNotExist:
        return toJsonResponse("Unknown build!", 404)

    response = {
        "commit_hash": build.commit_hash,
        "series": series.__str__(),
        "series_id": series.id,
        "build_number": build.build_number,
        "series_created": series.created_on,
        "build_created": build.created_on,
    }

    return toJsonResponse("Found", 200, response)


def listBuildsInSeries(major, minor) -> JsonResponse:
    try:
        series = Series.objects.get(major=major, minor=minor)
    except Series.DoesNotExist:
        return toJsonResponse("Unknown series!", 404)

    result = Build.objects.filter(series=series)
    builds = []

    for build in result:
        builds.append(
            {
                "commit_hash": build.commit_hash,
                "build_number": build.build_number,
                "build_created": build.created_on,
            }
        )

    response = {
        "series": series.__str__(),
        "series_id": series.id,
        "series_created": series.created_on,
        "builds": builds,
    }

    return toJsonResponse("Found", 200, response)
