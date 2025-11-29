# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Authentication routes for user registration and login
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        # Convert string 'true'/'false' to boolean
        is_seller_raw = data.get('is_seller', False)
        is_seller = is_seller_raw in ['true', 'True', True, 1, '1']

        # Validation
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))

        # Check if user exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'error': 'Username already exists'}), 400
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already exists'}), 400
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create user
        user = User(username=username, email=email, is_seller=is_seller)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        if request.is_json:
            return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201

        flash('Registration successful!', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            if request.is_json:
                return jsonify({'message': 'Login successful', 'user_id': user.id}), 200

            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))

        if request.is_json:
            return jsonify({'error': 'Invalid username or password'}), 401

        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
