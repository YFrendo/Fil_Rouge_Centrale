from flask import Flask, request,send_from_directory, after_this_request, make_response
import os
from json_transform import *
from PIL import Image, ExifTags
import shutil
import json
import uuid
from flask_httpauth import HTTPBasicAuth
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import boto3

app = Flask(__name__)


UPLOAD_FOLDER = './static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static',path)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name' : 'Seans-Python-Flask-REST-Boilerplate'
            }
        )
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
                sortie_json,metadata = image_json(path)
            except:
                return("Extension non supporté ou non existante",400)

        os.remove('./static/uploads/temporary_file') #On enlève le fichier
        dico_sortie = {'Transfo_json':sortie_json,'Metadata':metadata}

        s3 = boto3.client('s3')
        id_dc = str(uuid.uuid4())

        dico_sortie['ID'] = id_dc
        with open("./static/" + str(id_dc) + ".json", "w") as file:
                json.dump(dico_sortie, file)
        with open('./static/' + id_dc +'.json', 'rb') as f:
            val = s3.upload_fileobj(f, "filrouge",id_dc)
        if val == False:
            id_dc = 's3fail'
        

        @after_this_request #Après envoie on vide les fichiers temporaire
        def remove_static(response):
            os.remove('./static/' + str(id_dc) + ".json")
            return(response)
        

        response = make_response( send_from_directory(directory = './static/', filename = id_dc + '.json'))
        #response.headers['content-disposition'] = "attachment; filename=rendu.zip"
        return response, 200


@app.route('/stockage/<id_dos>', methods = ['GET'])
def stockage(id_dos):
    s3 = boto3.client('s3')
    try:
        s3.download_file("filrouge",str(id_dos),'./static/' + str(id_dos) + '.zip')
    except:
        return 'No file at this ID',404

    @after_this_request
    def remove_demande(response):
        os.remove('./static/' + str(id_dos) + '.zip')
        return (response)

    response = make_response( send_from_directory(directory = './static/', filename = id_dos + '.zip'))
    response.headers['content-disposition'] = "attachment; filename=rendu.zip"
    return response, 200


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000) 
