#!/usr/bin/env python3
import connexion
import logging

def get_hello():
    return {"message": "Kaptain says 'hello'!"}

logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api('openapi.yaml')

# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    app.run(port=8080)
