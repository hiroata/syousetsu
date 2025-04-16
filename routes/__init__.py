#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes package initialization.
Registers all blueprints to be imported by the application factory.
"""

from flask import Blueprint

# Import all blueprints
from .character import character_bp
from .location import location_bp
from .novel import novel_bp

# List of all blueprints to register with the app
all_blueprints = [
    character_bp,
    location_bp,
    novel_bp
]

# Function to register all blueprints with the app
def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)