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


def _read_config(repo):
    file_path = Path(os.path.join(repo.working_tree_dir, "kaptain.yaml"))
    if not os.path.exists(file_path):
        return dict()
    yaml = YAML()
    return yaml.load(file_path)


def _read_values_yaml(repo, chart):
    file_path = Path(os.path.join(repo.working_tree_dir, chart, "values.yaml"))
    yaml = YAML()
    return yaml.load(file_path)


def _get_value_by_path(obj, path):
    keys = path.split(".")
    for k in keys[:-1]:
        obj = obj[k]
    return obj[keys[-1]]


@create_tmp_dir
def get_repo_chart(repo, chart, tmp_dir):
    repo_url = urllib.parse.urljoin(GIT_ORGA, repo)
    r = _clone(repo_url, tmp_dir)
    config = _read_config(r)
    values_yaml = _read_values_yaml(r, chart)
    values = []
    for path in config["values"]:
        values.append({"path": path, "value": _get_value_by_path(values_yaml, path)})
    return {"values": values}


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
