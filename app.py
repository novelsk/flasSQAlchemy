from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some text'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dir_path + '/flask_app_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Folder(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    objects = db.relationship('Object', backref='upfolder')
    grandFolder = db.Column(db.Integer(), db.ForeignKey('folder.id'))

    def __init__(self, name):
        super(Folder, self).__init__()
        self.name = name

    def __repr__(self):
        return "<{}:{}:{}>".format(self.id, self.name, self.created)


class Object(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    folder = db.Column(db.Integer(), db.ForeignKey('folder.id'))

    def __init__(self, name, folder=None):
        super(Object, self).__init__()
        self.name = name
        if folder is not None:
            self.folder = folder

    def __repr__(self):
        return "<{}:{}:{}>".format(self.id, self.name, self.created)


@app.route('/')
def index():
    try:
        return jsonify(filtered(True))
    except:
        return 'another error', 500


@app.get('/object/')
def all_object():
    try:
        return jsonify(filtered())
    except:
        return 'another error', 500


@app.get('/object/<id_numb>/')
def get_object(id_numb):
    outfile = []
    try:
        id_numb = int(id_numb)
        if id_numb == 0:
            outfile = filtered()
        else:
            temp = Object.query.filter_by(id=id_numb).first_or_404()
            temp_json = {
                'id': temp.id,
                'name': temp.name,
                'created_at': temp.created
            }
            outfile.append(temp_json)
    except ValueError:
        return 'the specified id is not a digit', 400
    except:
        return 'another error', 500
    return jsonify(outfile)


@app.get('/<tempfolder>')
def folders(tempfolder):
    try:
        temp = Folder.query.filter_by(name=tempfolder).first_or_404()
        temp_json = {
            'id': temp.id,
            'name': temp.name,
            'created_at': temp.created,
            'objects': filtered()
        }
        return jsonify(temp_json)
    except:
        return 'another error', 500


def filtered(fold=False):
    temp = []
    req_filter = request.args.get('filter')
    if fold:
        if req_filter and req_filter != '':
            objs = Folder.query.filter_by(name=req_filter)
        else:
            objs = Folder.query.all()
    else:
        if req_filter and req_filter != '':
            objs = Object.query.filter_by(name=req_filter)
        else:
            objs = Object.query.all()
    for i in objs:
        temp.append({
            'id': i.id,
            'name': i.name,
            'created_at': i.created
        })
    return temp


if __name__ == '__main__':
    app.run(debug=True)
