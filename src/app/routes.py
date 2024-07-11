from flask import render_template

from app import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'logan'}
    winners = [
        {
            'participant': {'username': 'Becca'},
            'year': 2024,
            'points': 130.50,
        },
        {
            'participant': {'username': 'Yeager'},
            'year': 2023,
            'points': 126.34,
        },
        {
            'participant': {'username': 'Dodd'},
            'year': 2022,
            'points': 129.20,
        },
    ]

    return render_template('index.html', title='Home', user=user, winners=winners)
