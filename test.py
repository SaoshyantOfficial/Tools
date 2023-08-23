from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
db = SQLAlchemy(app)
UPLOAD_FOLDER = 'static/uploads'  # Name of the folder where uploaded images will be stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    filename = db.Column(db.String(100))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        description = request.form['description']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_image = Image(description=description, filename=filename)
            db.session.add(new_image)
            db.session.commit()
            return redirect(url_for('index'))

    images = Image.query.all()
    return render_template('test.html', images=images)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
