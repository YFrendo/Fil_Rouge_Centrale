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
            sortie_json, metadata = txt_json(path,upload_file.filename)
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".pdf":
            sortie_json,metadata = pdf_json(path)
        elif ext == ".csv":
            sortie_json,metadata = csv_json(path,upload_file.filename)
            metadata["Nom fichier"] = upload_file.filename
        elif:
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
            outfile.write(metadata)
        with open(app.config['UPLOAD_FOLDER'] + 'transfo.json','w') as outfile:
            outfile.write(sortie_json)

#Manque plus que de merge et zip le tout et renvoyer 



