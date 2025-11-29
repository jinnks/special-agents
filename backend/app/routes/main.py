# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Main routes for homepage and general pages
"""
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Homepage - marketplace landing page."""
    return render_template('index.html')


@bp.route('/about')
def about():
    """About page explaining ethical AI agents."""
    return render_template('about.html')
