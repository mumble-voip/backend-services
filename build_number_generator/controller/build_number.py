from flask import Flask, jsonify, current_app, request
from build_number_generator.database import get_database

import hashlib

MIN_COMMIT_HASH_LENGTH = 16

def hash_token(token: str) -> str:
	digest = hashlib.blake2b(digest_size=64)
	digest.update(str.encode(token))
	return digest.hexdigest()


def fail(status_message: str, status_code: int = 400) -> tuple:
	response = {}
	response["status"] = status_code
	response["message"] = status_message
	return response, status_code


@current_app.errorhandler(405)
def method_not_allowed(e) -> tuple:
    return fail("Method not allowed", 405)


@current_app.route("/build-number", methods=["POST"])
@current_app.route("/build-number/<string:series>", methods=["POST"])
@current_app.route("/build-number/<string:series>/<string:commit>", methods=["POST"])
def build_number(series=None, commit=None):

	token = request.form.get("token")

	if not token:
		return fail("Unautherized", 401)

	if not hash_token(token) in current_app.config["AUTHORIZED_HASHES"]:
		return fail("Unautherized", 401)

	if not series:
		return fail("Required parameter not provided. Format: /build-number/<series>/<commit_hash>")

	if series.count(".") != 1:
		return fail("Invalid parameter: series. Format: <major>.<minor>")

	major, minor = series.split(".")

	if not major.isnumeric() or not minor.isnumeric():
		return fail("Invalid parameter: series. Format: <major>.<minor>")

	major = int(major)
	minor = int(minor)

	if not commit:
		return fail("Required parameter not provided. Format: /build-number/<series>/<commit_hash>")

	if len(commit) < MIN_COMMIT_HASH_LENGTH:
		return fail("Invalid parameter: commit. Must be at least %i characters long" % (MIN_COMMIT_HASH_LENGTH))

	response = {}

	db = get_database()

	# Find or insert series
	result = db.execute("SELECT * FROM series WHERE name='%i.%i'" % (major, minor))
	row = result.fetchone()

	if row is not None:
		series_id = row["id"]
		response["message"] = "Known series. "
	else:
		cursor = db.execute("INSERT INTO series VALUES (NULL, '%i.%i', NULL)" % (major, minor))
		series_id = cursor.lastrowid
		response["message"] = "Unknown series. "

	# Find or insert build number
	result = db.execute("SELECT * FROM build WHERE series_id=%i AND commit_hash='%s'" % (series_id, commit))
	row = result.fetchone()

	if row is not None:
		build_number = row["build_number"]

		response["message"] += "Known commit hash."
		response["stauts"] = 200
	else:
		result = db.execute("SELECT build_number FROM build WHERE series_id=%i ORDER BY build_number DESC LIMIT 1" % (series_id))
		row = result.fetchone()
		build_number = (row["build_number"] + 1) if row is not None else 1
		cursor = db.execute("INSERT INTO build VALUES (NULL, %i, '%s', %i, NULL)" % (series_id, commit, build_number))

		response["message"] += "Unknown commit hash. New build number created."
		response["stauts"] = 201

	db.commit()

	response["commit_hash"] = commit
	response["series"] = "%i.%i" % (major, minor)
	response["series_id"] = series_id
	response["build_number"] = build_number

	return response, response["stauts"]
