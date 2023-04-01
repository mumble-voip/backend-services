import pytest
import json

@pytest.fixture()
def app():
	from build_number_generator import create_app
	from build_number_generator.database import init_database

	app = create_app()
	app.testing = True

	app.config.update({
		"DATABASE": "/tmp/test.sqlite",
		"AUTHORIZED_HASHES": {
			# 'testpassword'
			"ebe5a79f942bab98b3c122ceb72a9c23fb21991848cddb9ad4ce8a209c8269c25eb5f5146427afc23ef588de61798b38451282339e2c637c6dec51d635ab50c4"
		}
	})

	with app.app_context():
		init_database()

	yield app

@pytest.fixture()
def app_context(app):
	with app.app_context():
		yield app


@pytest.fixture()
def client(app_context):
	yield app_context.test_client()


def request(client, url, data=None):
	response = client.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
	j = json.loads(response.data)
	status = response.status_code
	return j, status


def test_method_1(client):
	response = client.get("/build-number")
	j = json.loads(response.data)
	status = response.status_code
	assert status == 405 and j["status"] == 405


def test_method_2(client):
	response = client.get("/build-number")
	j = json.loads(response.data)
	status = response.status_code
	assert status == 405 and j["status"] == 405
	#j, status = request(client, "/build-number/asd/asd", "")
	#assert status == 400 and j["status"] == 400

	#request(client, "/build-number/1.1/abcdefghijklmnopq", "token=testpassword")
