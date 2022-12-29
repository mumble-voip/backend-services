import sqlite3

import click
from flask import Flask, current_app, g


def get_database() -> sqlite3.Connection:
    """Gets the database connection for the current request. If this function is called for the first time for the given request,
    this function also connects to the database, whereas later calls will simply reuse that connection"""
    if "database" not in g:
        g.database = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.database.row_factory = sqlite3.Row

    return g.database


def close_database(_ = None) -> None:
    """If a connection to the database has been established, this function closes it again"""
    database: sqlite3.Connection = g.pop("database", None)

    if database is not None:
        database.close()


def init_database() -> None:
    """This function (re)creates the database from scratch. If the database existed
    before, its contents will be dropped"""
    database: sqlite3.Connection = get_database()

    with current_app.open_resource("schema.sql") as file:
        database.executescript(file.read().decode("utf-8"))


@click.command("init-db")
def init_db_command() -> None:
    """Clear existing data and create new tables."""
    init_database()
    click.echo("Database initialized")


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_database)
    app.cli.add_command(init_db_command)
