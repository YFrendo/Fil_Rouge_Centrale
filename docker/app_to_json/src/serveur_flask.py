from flask import Flask, request,send_from_directory
import os
from json_transform import *
from PIL import Image, ExifTags
import shutil
import json
from flask_httpauth import HTTPBasicAuth

import logging
#logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
#auth = HTTPBasicAuth()
#with open('./static/pwd.json', 'r') as file: #Rajouter achage +sel
#        users = json.load(file)


UPLOAD_FOLDER = './static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#@auth.verify_password
#def verify_paddword(username,passeword):
#    if username in users:
#        if users[username] == passeword:
#            return True
#    return False

@app.route('/', methods = ['GET','POST'])#/upload
#@auth.login_required
def to_json():

    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part',400
        upload_file = request.files['file']

        if upload_file.filename == '':
            return 'No selected file',400
        _, ext = os.path.splitext(upload_file.filename)
       
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'],'temporary_file')) #Enregistre de facon temporaire
        path = app.config['UPLOAD_FOLDER'] + 'temporary_file'

        if ext == ".txt":
            sortie = txt_json(path)
            if isinstance(sortie,str):
                return(sortie,400)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".pdf":
            sortie = pdf_json(path)
            if isinstance(sortie,str):
                return(sortie,400)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".csv":
            sortie = csv_json(path)
            if isinstance(sortie,str):
                return(sortie,400)
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
                sortie_json = image_json(path)
            except:
                return("Extension non supporté ou non existante",400)

        with open(app.config['UPLOAD_FOLDER'] + 'metadata.txt','w') as outfile:
            outfile.write(json.dumps(metadata))
        with open(app.config['UPLOAD_FOLDER'] + 'transfo.json','w') as outfile:
                outfile.write(str(sortie_json))
        shutil.make_archive('./static/outpout','zip',app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory = './static/', filename = 'outpout.zip'),200
if __name__ == "__main__":
    #app.secret_key = 'test'
    app.run(debug=True, host='0.0.0.0', port=5000)#ssl_context='adhoc') 
