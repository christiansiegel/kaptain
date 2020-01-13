#!/usr/bin/env python3
import connexion
import logging
import os
import shutil
import sys
import uuid
import urllib.parse
from flask import g
from ruamel.yaml import YAML
from git import Repo
from pathlib import Path

GIT_ORGA = "https://github.com/christiansiegel" + "/"


def create_tmp_dir(func):
    """
    Creates a temporary dir and passes its path as parameter "tmp_dir" to the
    wrapped function. The temporary dir is removed after exciting the
    function.
    """

    def wrapper(*args, **kwargs):
        tmp_dir = f"/tmp/{uuid.uuid4()}"
        kwargs["tmp_dir"] = tmp_dir
        os.makedirs(tmp_dir)
        try:
            return func(*args, **kwargs)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return wrapper


def _clone(repo_url, dest_dir):
    """
    Clones a git repository into the destination dir.
    """
    return Repo.clone_from(repo_url, dest_dir)


def get_hello():
    return {"message": "Kaptain says 'hello'!"}


@create_tmp_dir
def get_repo_chart(repo, chart, tmp_dir):
    repo_url = urllib.parse.urljoin(GIT_ORGA, repo)
    r = _clone(repo_url, tmp_dir)
    return {"values": [{"path": "test", "value": "xx"}]}


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api("openapi.yaml")


@app.app.errorhandler(Exception)
def handle_exception(e):
    logging.error("server error: %s", repr(e))
    return "server error", 500


# uwsgi --http :8080 -w app
application = app.app

if __name__ == "__main__":
    app.run(port=8080, debug=True)
