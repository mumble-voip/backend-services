from . import bp
from flask import flash, request, render_template
from http import HTTPStatus
from werkzeug import wsgi
import socket

cert_header = "PEER_SSL_CERTIFICATE"


def handle_registration():
    for requiredParam in [
        "server_certificate_digest",
        "server_name",
        "registration_password",
        "port",
    ]:
        if not requiredParam in request.form:
            return (
                'Missing required parameter "%s"' % requiredParam,
                HTTPStatus.BAD_REQUEST,
            )

    server_certificate_digest: str = request.form["server_certificate_digest"]
    server_name: str = request.form["server_name"]
    registration_password: str = request.form["registration_password"]
    website_url = request.form.get("website_url", None)
    hostname = request.form.get("hostname", None)
    ip_address = wsgi.get_host(request.environ)
    try:
        port: int = int(request.form["port"])
    except ValueError:
        return 'Invalid port "%s"' % request.form["port"], HTTPStatus.BAD_REQUEST

    server_addresses = []
    if hostname is not None:
        # TODO: handle unknown hostname
        for current in socket.getaddrinfo(hostname, None):
            # TODO: parse result
            pass

        if len(server_addresses) == 0:
            return (
                'Hostname "%s" could not be resolved' % hostname,
                HTTPStatus.BAD_REQUEST,
            )
    else:
        server_addresses.append(ip_address)

    # TODO: verify server is reachable (and cert matches)

    # TODO: Insert into database

    return "Registration successful"


@bp.server_list.route("/register", methods=["POST"])
def register():
    # TODO: Handle versioning
    return handle_registration()
