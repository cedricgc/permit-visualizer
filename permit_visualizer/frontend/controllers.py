# -*- coding: utf-8 -*-
"""Routing and request handler for client facing part of website

The flask Blueprint object provides the route decorator to dispatch requests
to the function as described in the decorator argument as well as controlling
the valid HTTP verbs that can be requested to that endpoint. The decorated
handler expects a flask.Response object as the return value.

See http://flask.pocoo.org/docs/latest/quickstart/#about-responses for how
flask converts return values to Response objects.

Flask uses Jinja2 as the templating engine to safely interpolate python objects
and embed control flow in HTML templates.

See http://flask.pocoo.org/docs/latest/quickstart/#rendering-templates for how
to render data from the controller to the template
"""


import flask


frontend_bp = flask.Blueprint('frontend', __name__)
"""Flask.Blueprint: Client facing website

Client facing pages scoped to main routes
"""


@frontend_bp.route('/', methods=['GET'])
def index():
    return "Hello!", 200
