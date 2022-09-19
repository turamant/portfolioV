from flask import render_template, request, send_file

from app_portfolio import app, Signup, db, Subscriber


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get("form_type") == 'formOne':
            new_signup = Signup(
                name=request.form.get('name'),
                email=request.form.get('email'),
                subject=request.form.get('subject'),
                timestamp=request.form.get('timestamp'),
                message=request.form.get('message'))
            db.session.add(new_signup)
            db.session.commit()
        elif request.form.get("form_type") == 'formTwo':
            new_subscriber = Subscriber(
                email=request.form.get('email'))
            db.session.add(new_subscriber)
            db.session.commit()
    return render_template('index.html')


@app.route('/download')
def download_file():
    path = 'resume1.pdf'
    return send_file(path, as_attachment=True)



