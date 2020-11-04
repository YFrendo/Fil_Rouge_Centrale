import json
import PyPDF2
import pandas
import base64

def txt_json(path):

    fichier = open(path, 'rb')
    texte = ''
    try:
        for ligne in fichier:
            texte = texte + ligne
        sortie = json.dumps(texte)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un fichier texte?")
    return(sortie)

def pdf_json(path):
    
    fichier = open(path, 'rb')
    try:
        read_pdf = PyPDF2.PdfFileReader(fichier)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un PDF?")
    number_of_pages = read_pdf.getNumPages()
    texte = ''

    for k in range(number_of_pages):
        page = read_pdf.getPage(k)
        page_content = page.extractText()
        texte = texte + page_content

    sortie = json.dumps(texte)
    return(sortie)

def csv_json(path):
    try:
        df = pandas.read_csv(path)
    except:
        return("Erreur lors de la transformation, etes vous sur que le fichier soit un CSV?")
    resultat = df.to_json(orient = "split")
    return(resultat)

def image_json(path):
    
    data = {}
    with open(path, 'rb') as file:
        img = file.read()
    data['img'] = base64.b64encode(img)
    return(data)

