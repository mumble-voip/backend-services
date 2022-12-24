#!/usr/bin/env python3

from flask import Flask

app = Flask(__name__)


@app.route("/public_server_list/<version>/register")
def register(version: str):
    return "Endpoint for register version " + version


@app.route("/public_server_list/<version>/fetch")
def fetch(version: str):
    return "Endpoint for fetch version " + version


@app.route("/public_server_list/<version>/display")
def display(version: str):
    return "Endpoint for display version " + version


if __name__ == "__main__":
    app.run(debug=True)
