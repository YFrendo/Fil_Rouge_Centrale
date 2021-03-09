import json
import PyPDF2
import pandas
import base64
import os
import logging
import boto3
from botocore.exceptions import ClientError
from PIL import Image

def txt_json(path): #Va transformer le fichier texte en JSON
    fichier = open(path, 'r')
    texte = ''
    nb_ligne = 0
    nb_carac = 0
    try:
        for ligne in fichier: # Parcours le fichier pour compter le nombre de ligne et de caractère ainssi que les mettres dans une variable string
            nb_ligne += 1
            nb_carac += len(ligne)
            texte = texte + ligne
        json_txt = json.dumps(texte) #Transforme le string en JSON
    except: #Si il y a une erreur lors de la création du JSON on renvoie le message d'erreur
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un fichier texte?")
    taille = os.path.getsize(path)
    metadata = { "taille" : taille , "MIME" : "txt","NombreLigne" : nb_ligne,"nombre-caractère" : nb_carac} #Création du dictionnaire de métadonné
    sortie = (json_txt,metadata)
    return(sortie) #Renvoie JSON + metadonné

def pdf_json(path): #Transforme un fichier PDF en JSON
    
    fichier = open(path, 'rb')
    try: #On ouvre le fichier comme un PDF
        read_pdf = PyPDF2.PdfFileReader(fichier)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un PDF?") #Si on arrive pas à l'ouvrir ce n'est pas un PDF
    Docinfo = read_pdf.getDocumentInfo() #Extraction des metadonnées du PDF
    metadata = {"Auteur" : Docinfo.author , "Createur" : Docinfo.creator , "Sujet" : Docinfo.subject , "Titre" : Docinfo.title, "MIME" : "pdf", "taille" : os.path.getsize(path)}
    number_of_pages = read_pdf.getNumPages()
    texte = ''

    for k in range(number_of_pages): #Permet de gérer plusieurs pages 
        page = read_pdf.getPage(k)
        page_content = page.extractText()
        texte = texte + page_content

    json_pdf = json.dumps(texte)
    sortie = (json_pdf,metadata) #On renvoie JSON + Metadata
    return(sortie)

def csv_json(path): #Transforme un CSV en JSON
    try:
        df = pandas.read_csv(path,sep =';')
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un CSV?Séparateur : ;") #Permet de vérifier que c'est bien un CSV
    taille = os.path.getsize(path)
    nb_col = len(df.columns)
    nb_lignes = len(df)
    metadata = { "taille" : taille , "MIME" : "csv","Nombre_Colones" : nb_col, "Nombre_Lignes" : nb_lignes} #Metadonnées
    json_csv = df.to_json(orient = 'columns')
    sortie = (json_csv,metadata) #JSON + metadata
    return(sortie)

def detect_labels_rekognition(path): #Cette fonction permet de demandé à AWS de faire de la reconnaissance d'image
    with open(path, 'rb') as f:
        Image_bytes = f.read()
        session = boto3.Session()
        s3_client = session.client('rekognition')
        response = s3_client.detect_labels(Image={'Bytes':Image_bytes},MaxLabels=10, MinConfidence=95) #Je ne séléctionne que les labels avec une confience de 95% ou plus
        return response



def image_json(path): #Images en JSON
    exifTag = ('DateTimeOriginal', 'DateTimeDigitized', 'Flash', 'ShutterSpeedValue',\
                    'Software', 'ISOSpeedRatings', 'BrightnessValue', 'Make', 'Model', \
                            'Orientation') #Liste des tag pour les métadonnées

    data = {}
    metadata = {}
    with open(path, 'rb') as file:
        img = file.read()
    base64_bytes = base64.b64encode(img) #On transforme l'image en base64
    data['img'] = base64_bytes.decode('utf-8') #On transforme la base64 en string pour pouvoir la stocker dans un JSON
    image = Image.open(path) #Si l'image ne peuit pas etre ouverte par PIL alors le programme plante ce qui est récupérer dans le programme principal

    metadata['Width'] = image.size[0]
    metadata['Height'] = image.size[1]
    metadata['Format'] = image.format #Certaine metadatas
    
    try:
        for tag_id in exifdata:
            tag = TAGS.get(tag_id,tag_id) #On récupére les métadatas
            data = exifdata.get(tag_id)

            if isinstace(data,bytes):
                data = data.decode()

            if tag in exifTag:
                metadata[str(tag)] = str(data)
    except: #Si on arrive pas à les récupérer on ne fait rien et on continue 
        pass

    labels = detect_labels_rekognition(path) #Reconnaissance d'image par AWS, si l'image à été récupéré par PIL alors il est possible de la lire avec AWS
    Labels_dictionary = {}
    for k in range(len(labels['Labels'])):
        Labels_dictionary[labels['Labels'][k]['Name']] = 'Confiance de' + str(labels['Labels'][k]['Confidence'])
        metadata['Labels detected'] = Labels_dictionary
    return(data['img'],metadata) #Json + metadata











