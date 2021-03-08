import json
import PyPDF2
import pandas
import base64
import os
import logging
import boto3
from botocore.exceptions import ClientError
from PIL import Image

def txt_json(path):
    fichier = open(path, 'r')
    texte = ''
    nb_ligne = 0
    nb_carac = 0
    try:
        for ligne in fichier:
            nb_ligne += 1
            nb_carac += len(ligne)
            texte = texte + ligne
        json_txt = json.dumps(texte)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un fichier texte?")
    taille = os.path.getsize(path)
    metadata = { "taille" : taille , "MIME" : "txt","NombreLigne" : nb_ligne,"nombre-caractère" : nb_carac}
    sortie = (json_txt,metadata)
    return(sortie)

def pdf_json(path):
    
    fichier = open(path, 'rb')
    try:
        read_pdf = PyPDF2.PdfFileReader(fichier)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un PDF?")
    Docinfo = read_pdf.getDocumentInfo()
    metadata = {"Auteur" : Docinfo.author , "Createur" : Docinfo.creator , "Sujet" : Docinfo.subject , "Titre" : Docinfo.title, "MIME" : "pdf", "taille" : os.path.getsize(path)}
    number_of_pages = read_pdf.getNumPages()
    texte = ''

    for k in range(number_of_pages):
        page = read_pdf.getPage(k)
        page_content = page.extractText()
        texte = texte + page_content

    json_pdf = json.dumps(texte)
    sortie = (json_pdf,metadata)
    return(sortie)

def csv_json(path):
    try:
        df = pandas.read_csv(path,sep =';')
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un CSV?Séparateur : ;")
    taille = os.path.getsize(path)
    nb_col = len(df.columns)
    nb_lignes = len(df)
    metadata = { "taille" : taille , "MIME" : "csv","Nombre_Colones" : nb_col, "Nombre_Lignes" : nb_lignes}
    json_csv = df.to_json(orient = 'columns')
    sortie = (json_csv,metadata)
    return(sortie)

def detect_labels_rekognition(path):
    with open(path, 'rb') as f:
        Image_bytes = f.read()
        session = boto3.Session()
        s3_client = session.client('rekognition')
        response = s3_client.detect_labels(Image={'Bytes':Image_bytes},MaxLabels=10, MinConfidence=95)
        return response



def image_json(path):
    exifTag = ('DateTimeOriginal', 'DateTimeDigitized', 'Flash', 'ShutterSpeedValue',\
                    'Software', 'ISOSpeedRatings', 'BrightnessValue', 'Make', 'Model', \
                            'Orientation')

    data = {}
    metadata = {}
    with open(path, 'rb') as file:
        img = file.read()
    base64_bytes = base64.b64encode(img)
    data['img'] = base64_bytes.decode('utf-8')
    image = Image.open(path)

    metadata['Width'] = image.size[0]
    metadata['Height'] = image.size[1]
    metadata['Format'] = image.format
    
    try:
        for tag_id in exifdata:
            tag = TAGS.get(tag_id,tag_id)
            data = exifdata.get(tag_id)

            if isinstace(data,bytes):
                data = data.decode()

            if tag in exifTag:
                metadata[str(tag)] = str(data)
    except:
        pass

    labels = detect_labels_rekognition(path)
    Labels_dictionary = {}
    for k in range(len(labels['Labels'])):
        Labels_dictionary[labels['Labels'][k]['Name']] = 'Confiance de' + str(labels['Labels'][k]['Confidence'])
        metadata['Labels detected'] = Labels_dictionary
    return(data['img'],metadata)











