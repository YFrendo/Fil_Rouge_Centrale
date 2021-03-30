# Fil_Rouge_Centrale
Ceci est le projet fil_rouge fait pour le mastère SIO 2021 à centrale supélec
Il a pour but de construire une API qui pour un fichier donné renvoie sa conversion en JSON et les metadatas associés

## Utilisation

Pendant la durée de l'évaluation l'API est disponible à cette adresse: https://tojson.yaf.p2021.ajoga.fr/  
La façon la plus simple d'utiliser l'API est via le swagger disponible à: https://tojson.yaf.p2021.ajoga.fr/swagger

## Descriptif des fonctionnalité de l'API
L'API n'a que deux commandes possibles qui sont les suivantes:

### /upload (request methode POST)

Cette appel permet d'envoyer un fichier dans les formats suivant: .txt , .pdf , .csv, .jpg et .png (à noter que certaines autres extention d'images sont supporté sans garantie de résultats)  
L'API se charge enssuite de renvoyer un JSON avec tois clef:  
* Transfo_json: qui contient le transformé du fichier en JSON  
* Metadata: qui contient les metadata   
* ID: Qui est l'ID du fichier (utile pour /stockage GET)  

L'API à quelques limitations:
* Limitation de la taille des fichiers en entré : 10 Mo  
* Limitation du nombre de requete pour une adresse IP : 1/s  

Exemple de commande:  
`curl -X POST "https://tojson.yaf.p2021.ajoga.fr/upload" -H  "accept: */*" -H  "Content-Type: multipart/form-data" -F "file=@votre_fichier" -u User:Password`

Le JSON est également stocké dans un bucket S3 amazon et est récupérable avec la commande suivante  

### /stockage/(ID) (request methode GET)
Cette commande permet de récupérer le fichier JSON depuis le bucket S3:  

Exemple de commande:  
` curl -X GET "https://tojson.yaf.p2021.ajoga.fr/stockage/(ID)" -H  "accept: */*"`

### Dossier Kubernetes
Regroupe l'enssemble des fichier pour un déployement sur kubernetes, ces fichiers ont été généré avec Kompose
