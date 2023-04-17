from django.test import TestCase
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.db import transaction
from .models import Series, Build

import json

AUTH_PASSWORD = "testpassword"
AUTH_URLPARAM = "?token=testpassword"

COMMIT_HASH_1 = "931ad6480dce38486a221119bccd0a35e5cdbb81"
COMMIT_HASH_2 = "784ec286c3b0292b2aece78a2300c55143932360"
COMMIT_HASH_3 = "3e273e617a0adba491e9879f6aabf7915db0f432"

BASE_URL_API_V1 = "/build-number/v1"


def authorizedURL(url):
    return url + AUTH_URLPARAM


class Test_Model(TestCase):
    # Expect constraints to be enforced
    def test_constraint1(self):
        series = Series.objects.create(major=1, minor=1)
        Build.objects.create(
            series=series,
            commit_hash=COMMIT_HASH_1,
            build_number=1,
        )

        with self.assertRaises(IntegrityError):
            Build.objects.create(
                series=series,
                commit_hash=COMMIT_HASH_1,
                build_number=1,
            )

    def test_constraint2(self):
        series = Series.objects.create(major=1, minor=1)

        with self.assertRaises(IntegrityError):
            Series.objects.create(major=1, minor=1)

    # Expect delete protection for series with builds
    def test_delete_protection(self):
        series = Series.objects.create(major=1, minor=1)
        Build.objects.create(
            series=series,
            commit_hash=COMMIT_HASH_1,
            build_number=1,
        )

        with self.assertRaises(ProtectedError):
            Series.objects.filter(id=series.id).delete()


class Test_HTTP(TestCase):
    # Expect a 400 error on invalid API version
    def test_url_routing1(self):
        urls = [
            "/build-number",
            "/build-number/",
            "/build-number/v0",
            "/build-number/v0/",
            "/build-number/v0/series",
            "/build-number/v0/series/",
            "/build-number/v0/series/hash",
            "/build-number/v0/series/hash/",
        ]
        for url in urls:
            response = self.client.get(authorizedURL(url))
            self.assertEqual(response.status_code, 400)

    # Expect to reach all API endpoints with a 401 error, if not authorized
    def test_url_routing2(self):
        urls = [
            "/build-number/v1",
            "/build-number/v1/",
            "/build-number/v1/series",
            "/build-number/v1/series/",
            "/build-number/v1/series/hash",
            "/build-number/v1/series/hash/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401)

    # Expect no 401 error on any endpoint, if we are authorized
    def test_url_routing3(self):
        urls = [
            "/build-number/v1",
            "/build-number/v1/",
            "/build-number/v1/series",
            "/build-number/v1/series/",
            "/build-number/v1/series/hash",
            "/build-number/v1/series/hash/",
        ]
        for url in urls:
            response = self.client.get(authorizedURL(url))
            self.assertNotEqual(response.status_code, 401)

    # Expect no 404 error on any valid endpoint
    def test_url_routing3(self):
        urls = [
            "/build-number/v1/series",
            "/build-number/v1/series/",
            "/build-number/v1/series/hash",
            "/build-number/v1/series/hash/",
        ]
        for url in urls:
            response = self.client.get(authorizedURL(url))
            self.assertNotEqual(response.status_code, 404)

    # Expect to only reach valid version endpoints
    def test_api_version(self):
        response = self.client.get(authorizedURL("/build-number/1"))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(authorizedURL("/build-number/a"))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(authorizedURL("/build-number/v"))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(authorizedURL("/build-number/va"))
        self.assertEqual(response.status_code, 400)

        # This should succeed
        response = self.client.post(authorizedURL("/build-number/v1"))
        self.assertNotEqual(response.status_code, 400)


class API_InsertNewBuild(TestCase):
    # Expect argument parsing to only accept valid arguments
    def test_argument_parsing(self):
        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "11", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.a", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            authorizedURL("%s/%s/SHORT" % (BASE_URL_API_V1, "1.1"))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

    # Unknown series, unknown commit
    def test_db_1(self):
        self.assertEqual(len(Series.objects.all()), 0)
        self.assertEqual(len(Build.objects.all()), 0)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

    # Known series, unknown commit
    def test_db_2(self):
        self.assertEqual(len(Series.objects.all()), 0)
        self.assertEqual(len(Build.objects.all()), 0)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_2))
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 2)

    # Commit already exists in series
    def test_db_3(self):
        self.assertEqual(len(Series.objects.all()), 0)
        self.assertEqual(len(Build.objects.all()), 0)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

        with transaction.atomic():
            response = self.client.post(
                authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
            )
            self.assertEqual(response.status_code, 409)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

    # Unknown series, known commit
    def test_db_4(self):
        self.assertEqual(len(Series.objects.all()), 0)
        self.assertEqual(len(Build.objects.all()), 0)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.2", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(Series.objects.all()), 2)
        self.assertEqual(len(Build.objects.all()), 2)

    # Expect correct database values after insertion
    def test_db_content_1(self):
        self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )

        series = Series.objects.all()[0]
        build = Build.objects.all()[0]

        self.assertEqual(series.major, 1)
        self.assertEqual(series.minor, 1)
        self.assertEqual(build.series, series)
        self.assertEqual(build.commit_hash, COMMIT_HASH_1)
        self.assertEqual(build.build_number, 1)

    def test_db_content_2(self):
        self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_2))
        )

        series = Series.objects.all()[0]
        build = Build.objects.all()[1]

        self.assertEqual(series.major, 1)
        self.assertEqual(series.minor, 1)
        self.assertEqual(build.series, series)
        self.assertEqual(build.commit_hash, COMMIT_HASH_2)
        self.assertEqual(build.build_number, 2)

    # Expect to fail if the new build number exceeds two bytes
    def test_db_fail(self):
        self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        series = Series.objects.all()[0]

        Build.objects.create(
            series=series,
            commit_hash=COMMIT_HASH_2,
            build_number=0xFFFF,
        )

        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_3))
        )
        self.assertEqual(response.status_code, 422)

        self.assertEqual(len(Build.objects.all()), 2)

    # Expect the JSON response to match the arguments
    def test_response(self):
        response = self.client.post(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        response = json.loads(response.content)

        self.assertEqual(response["series"], "1.1.x")
        self.assertEqual(response["series_id"], 1)
        self.assertEqual(response["commit_hash"], COMMIT_HASH_1)
        self.assertEqual(response["build_number"], 1)
        self.assertEqual("build_created" in response, True)
        self.assertEqual("series_created" in response, True)
        self.assertEqual(
            response["message"], "Unknown series. New build number created."
        )
        self.assertEqual(response["status"], 201)


class API_GetExistingBuild(TestCase):
    def setup(self):
        series = Series.objects.create(major=1, minor=1)

        build = Build.objects.create(
            series=series, commit_hash=COMMIT_HASH_1, build_number=1
        )

        return series, build

    # Expect argument parsing to only accept valid arguments
    def test_argument_parsing(self):
        series, build = self.setup()

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "11", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.a", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            authorizedURL("%s/%s/SHORT" % (BASE_URL_API_V1, "1.1"))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 200)

    # Test side-effect free retrieval
    def test_db(self):
        series, build = self.setup()

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

    # Expect to fail if the commit is not known
    def test_db_fail_1(self):
        series, build = self.setup()

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_2))
        )

        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

    # Expect to fail if the series is not known
    def test_db_fail_2(self):
        series, build = self.setup()

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.2", COMMIT_HASH_1))
        )

        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 1)

    # Expect the JSON response to match the arguments
    def test_response(self):
        series, build = self.setup()

        response = self.client.get(
            authorizedURL("%s/%s/%s" % (BASE_URL_API_V1, "1.1", COMMIT_HASH_1))
        )
        response = json.loads(response.content)

        self.assertEqual(response["series"], series.__str__())
        self.assertEqual(response["series_id"], series.id)
        self.assertEqual(response["commit_hash"], build.commit_hash)
        self.assertEqual(response["build_number"], build.build_number)
        self.assertEqual("build_created" in response, True)
        self.assertEqual("series_created" in response, True)
        self.assertEqual(response["message"], "Found")
        self.assertEqual(response["status"], 200)


class API_ListBuildsInSeries(TestCase):
    def setup(self):
        series = Series.objects.create(major=1, minor=1)

        build1 = Build.objects.create(
            series=series, commit_hash=COMMIT_HASH_1, build_number=1
        )

        build2 = Build.objects.create(
            series=series, commit_hash=COMMIT_HASH_2, build_number=2
        )

        return series, [build1, build2]

    # Expect argument parsing to only accept valid arguments
    def test_argument_parsing(self):
        series, builds = self.setup()

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "11")))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.a")))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.1")))
        self.assertEqual(response.status_code, 405)

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.1")))
        self.assertEqual(response.status_code, 200)

    # Test side-effect free retrieval
    def test_db(self):
        series, builds = self.setup()

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 2)

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.1")))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 2)

    # Expect to fail if the series is not known
    def test_db_fail(self):
        series, build = self.setup()

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 2)

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.2")))

        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(Series.objects.all()), 1)
        self.assertEqual(len(Build.objects.all()), 2)

    # Expect the JSON response to match the arguments
    def test_response(self):
        series, builds = self.setup()

        response = self.client.get(authorizedURL("%s/%s/" % (BASE_URL_API_V1, "1.1")))
        response = json.loads(response.content)

        self.assertEqual(response["series"], series.__str__())
        self.assertEqual(response["series_id"], series.id)
        self.assertEqual("series_created" in response, True)
        self.assertEqual(response["message"], "Found")
        self.assertEqual(response["status"], 200)

        for build in response["builds"]:
            self.assertEqual(
                build["commit_hash"], builds[build["build_number"] - 1].commit_hash
            )
            self.assertEqual(
                build["build_number"], builds[build["build_number"] - 1].build_number
            )
            self.assertEqual("build_created" in build, True)
