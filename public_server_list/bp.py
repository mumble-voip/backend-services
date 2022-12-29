from flask import Blueprint

server_list: Blueprint = Blueprint("server_list", __name__, url_prefix="/public_server_list")
