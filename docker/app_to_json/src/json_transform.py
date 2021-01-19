import json
import PyPDF2
import pandas
import base64
import os

def txt_json(path):
    fichier = open(path, 'r')
    texte = ''
    try:
        for ligne in fichier:
            texte = texte + ligne
        json_txt = json.dumps(texte)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un fichier texte?")
    taille = os.path.getsize(path)
    metadata = { "taille" : taille , "MIME" : "txt"}
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
    metadata = { "taille" : taille , "MIME" : "csv"}
    json_csv = df.to_json(orient = 'columns')
    sortie = (json_csv,metadata)
    return(sortie)

def image_json(path):
    
    data = {}
    with open(path, 'rb') as file:
        img = file.read()
    data['img'] = base64.b64encode(img)
    return(data)

