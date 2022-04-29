import csv
import os

from flask import Blueprint, render_template, abort, url_for,current_app
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.db import db
from app.db.models import Song
from app.songs.forms import csv_upload
from werkzeug.utils import secure_filename, redirect

songs = Blueprint('songs', __name__,
                        template_folder='templates')


@songs.route('/songs/upload', methods=['POST', 'GET'])
@login_required
def songs_upload():
    form = csv_upload()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)

        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                song = Song.query.filter_by(title=row['Name']).first()
                if song is None:
                    current_user.songs.append(Song(row['Name'], row['Artist'], row['Genre'], row['Year']))
                    db.session.commit()
                else:
                    current_user.songs.append(song)
                    db.session.commit()

        return redirect(url_for('auth.dashboard'))

    try:
        return render_template('upload.html', form=form)
    except TemplateNotFound:
        abort(404)