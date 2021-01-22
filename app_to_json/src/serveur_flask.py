from flask import Flask, request,send_from_directory, after_this_request
import os
from json_transform import *
from PIL import Image, ExifTags
import shutil
import json
import uuid
from flask_httpauth import HTTPBasicAuth
import logging
import boto3

app = Flask(__name__)


UPLOAD_FOLDER = './static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods = ['GET','POST'])
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

        os.remove('./static/uploads/temporary_file') #On enlève le fichier
        with open(app.config['UPLOAD_FOLDER'] + 'metadata.txt','w') as outfile:
            outfile.write(json.dumps(metadata))
        with open(app.config['UPLOAD_FOLDER'] + 'transfo.json','w') as outfile:
            outfile.write(str(sortie_json))

        s3 = boto3.client('s3')
        id_dc = str(uuid.uuid4())
        with open(app.config['UPLOAD_FOLDER'] + 'id_dos.txt' ,'w') as outfile:
                outfile.write(id_dc)

        shutil.make_archive('./static/' + id_dc,'zip',app.config['UPLOAD_FOLDER'])
        with open('./static/' + id_dc +'.zip', 'rb') as f:
            val = s3.upload_fileobj(f, "filrouge",id_dc)
        if val == False:
            id_dc = 's3fail'

        @after_this_request #Après envoie on vide les fichiers temporaire
        def remove_static(response):
            os.remove('./static/' + id_dc + '.zip')
            os.remove('./static/uploads/transfo.json')
            os.remove('./static/uploads/metadata.txt')
            return(response)

        return send_from_directory(directory = './static/', filename = id_dc + '.zip'),200


@app.route('/stockage/<id_dos>', methods = ['GET'])
def stockage(id_dos):
    s3 = boto3.client('s3')
    s3.download_file("filrouge",str(id_dos),'./static/' + str(id_dos) + '.zip')
   
    @after_this_request
    def remove_demande(response):
        os.remove('./static/' + str(id_dos) + '.zip')
        return (response)
    return send_from_directory(directory = './static/', filename = id_dos +'.zip'),200



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 
