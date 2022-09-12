from flask import render_template

from app_portfolio import app


@app.route('/')
def index():
    return render_template('app/index.html')

