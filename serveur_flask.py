import flask
import os
from import json_transform import *
from PIL import Image, ExifTags

UPLOAD_FOLDER = './static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods = ['GET','POST'])
def to_json():

    if not os.path.isdir(app.config['UPLOAD_FOLDER']:
            os.makedirs(app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        upload_file = request.file['file']

        if upload_file.filename == '':
            return 'No selected file'
        _, ext = os.path.splitext(upload_file.filename)
       
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'],'temporary_file') #Enregistre de facon temporaire
        path = app.config['UPLOAD_FOLDER'] + 'temporary_file'

        if ext == ".txt":
            sortie_json = txt_json(path)
        elif ext == ".pdf":
            sortie_json = pdf_json(path)
        elif ext == ".csv":
            sortie_json = csv_json(path)
        elif:
            try:
                im = Image.open(upload_file)
                sortie_json = image_josn(path)
            except:
                return("Extension non supporté ou non existante")




        #Voila et a partir de la je récupère et j'indentifie l extension et je fais la suite

