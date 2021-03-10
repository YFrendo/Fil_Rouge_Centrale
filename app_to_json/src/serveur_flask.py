from flask import Flask, request, send_from_directory, after_this_request, make_response
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


UPLOAD_FOLDER = "./static/uploads/"  # Variable qui permet de gérer ou est le fichier de stockage temporaire
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route(
    "/static/<path:path>"
)  # Tout ce qui est en dessous permet de gérer le swagger
def send_static(path):
    return send_from_directory("static", path)


SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Seans-Python-Flask-REST-Boilerplate"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route(
    "/upload", methods=["POST"]
)  # Route /upload qui permet de upload un ficheir et d'avoir la transformation JSON
def to_json():

    if not os.path.isdir(
        app.config["UPLOAD_FOLDER"]
    ):  # On vérifie l'existance du fichier Upload
        os.makedirs(app.config["UPLOAD_FOLDER"])
    if request.method == "POST":
        if (
            "file" not in request.files
        ):  # Si il n'y a pas de file dans la requette on renvoie une erreur
            return "No file part", 400
        upload_file = request.files["file"]  # Sinon on la télécharge

        if (
            upload_file.filename == ""
        ):  # Si il y a une file mais rien dedans on renvoie une erreur
            return "No selected file", 400
        _, ext = os.path.splitext(
            upload_file.filename
        )  # On extrait le MIME du fichier qui va nous permettre de savoir de quel type il est

        upload_file.save(
            os.path.join(app.config["UPLOAD_FOLDER"], "temporary_file")
        )  # Enregistre de facon temporaire le fichier
        path = app.config["UPLOAD_FOLDER"] + "temporary_file"

        if ext == ".txt":  # Si le fichier est un fichier texte
            sortie = txt_json(path)
            if isinstance(
                sortie, str
            ):  # Si la sortie est un str alors il y a eu une erreur et on renvoie le message d'erreur
                return (sortie, 400)
            sortie_json, metadata = sortie
            metadata[
                "Nom fichier"
            ] = upload_file.filename  # On rajoute le nom du fichier
        elif ext == ".pdf":  # Idem pour PDF
            sortie = pdf_json(path)
            if isinstance(sortie, str):
                return (sortie, 400)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        elif ext == ".csv":  # Idem pour CSV
            sortie = csv_json(path)
            if isinstance(sortie, str):
                return (sortie, 400)
            sortie_json, metadata = sortie
            metadata["Nom fichier"] = upload_file.filename
        else:  # Si ce n'est rien de tout ca alors on teste si c'est une image
            try:
                sortie_json, metadata = image_json(path)
            except:  # Si cella ne marche pas on renvoie une erreur
                return ("Extension non supporté,non existante ou incorrecte", 400)

        os.remove(
            "./static/uploads/temporary_file"
        )  # On enlève le fichier qui n'est plus utile
        dico_sortie = {
            "Transfo_json": sortie_json,
            "Metadata": metadata,
        }  # On créer le dico de sortie

        s3 = boto3.client("s3")
        id_dc = str(
            uuid.uuid4()
        )  # On va créer une ID pseudo unique pour le fichier (10^38 ID possible)

        dico_sortie["ID"] = id_dc  # On rajoute l'ID au JSON de sortie
        with open(
            "./static/" + str(id_dc) + ".json", "w"
        ) as file:  # On créer un JSON avec la sortie
            json.dump(dico_sortie, file)
        with open("./static/" + id_dc + ".json", "rb") as f:
            val = s3.upload_fileobj(
                f, "filrouge", id_dc
            )  # On upload le fichier sur le bucketS3 AWS
        if val == False:
            id_dc = "s3fail"  # Si il y a un problème avec S3

        @after_this_request  # Après envoie on vide les fichiers temporaire
        def remove_static(response):
            os.remove("./static/" + str(id_dc) + ".json")
            return response

        response = make_response(
            send_from_directory(directory="./static/", filename=id_dc + ".json")
        )  # On fabrique la réponse
        # response.headers['content-disposition'] = "attachment; filename=rendu.zip" Permet de télécharger via swagger
        return response, 200  # Et on envoie


@app.route("/stockage/<id_dos>", methods=["GET"])
def stockage(id_dos):  # Permet de récupérer un JSON enregistré dans S3
    s3 = boto3.client("s3")
    try:
        s3.download_file(
            "filrouge", str(id_dos), "./static/" + str(id_dos) + ".json"
        )  # On télécharge sur S3
    except:
        return "No file at this ID", 404

    @after_this_request
    def remove_demande(response):  # On supprime fichier temporaire
        os.remove("./static/" + str(id_dos) + ".json")
        return response

    response = make_response(
        send_from_directory(directory="./static/", filename=id_dos + ".json")
    )  # On renvoie
    # response.headers['content-disposition'] = "attachment; filename=rendu.json" Permet de télécharger via swagger
    return response, 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)  # Démarage de Flask
