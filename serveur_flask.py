from flask import Flask, request,send_from_directory
import os
from json_transform import *
from PIL import Image, ExifTags
import shutil
import json

UPLOAD_FOLDER = './static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods = ['GET','POST'])
def to_json():

    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        upload_file = request.files['file']

        if upload_file.filename == '':
            return 'No selected file'
        _, ext = os.path.splitext(upload_file.filename)
       
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'],'temporary_file')) #Enregistre de facon temporaire
        path = app.config['UPLOAD_FOLDER'] + 'temporary_file'

        if ext == ".txt":
            sortie = txt_json(path)
            if isinstance(sortie,str):
                return(sortie)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".pdf":
            sortie = pdf_json(path)
            if isinstance(sortie,str):
                return(sortie)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".csv":
            sortie = csv_json(path)
            if isinstance(sortie,str):
                return(sortie)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        else:
            try:
                im = Image.open(upload_file)
                exif = {
                    ExifTags.TAGS[k] : v
                    for k, v in im.getexif().items()
                    if k in ExifTags.TAGS
                    }
                metadata = str(exif)
                sortie_json = image_josn(path)
            except:
                return("Extension non supporté ou non existante")

        with open(app.config['UPLOAD_FOLDER'] + 'metadata.txt','w') as outfile:
            outfile.write(json.dumps(metadata))
        with open(app.config['UPLOAD_FOLDER'] + 'transfo.json','w') as outfile:
            outfile.write(sortie_json)
        shutil.make_archive('./static/outpout','zip',app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory = './static/', filename = 'outpout.zip')

#Manque plus que de merge et zip le tout et renvoyer 



