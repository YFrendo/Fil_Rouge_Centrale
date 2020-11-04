import flask

app = Flask(__name__)

@app.route('/upload', methods = ['GET','POST'])
def to_json():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        upload_file = request.file['file']

        if upload_file.filename == '':
            return 'No selected file'

        #Voila et a partir de la je récupère et j'indentifie l extension et je fais la suite

