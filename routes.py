from flask import Blueprint, render_template

# This is what app.py is trying to import
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/menu')
def menu():
    return render_template('index.html')  # For now just render index.html

@main.route('/about')
def about():
    return render_template('index.html')  # For now just render index.html

@main.route('/contact')
def contact():
    return render_template('index.html')  # For now just render index.html

@main.route('/cart')
def cart():
    return render_template('index.html')  # For now just render index.html

@main.route('/profile')
def profile():
    return render_template('index.html')  # For now just render index.html