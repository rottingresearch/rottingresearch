import os
import shutil
from datetime import timedelta
import linkrot
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, send_from_directory, after_this_request
from linkrot.downloader import sanitize_url, get_status_code
from urllib.parse import urlparse
from celery_init import celery_init_app
from tasks import pdfdata_task
from celery.result import AsyncResult
import utilites
from flask import current_app

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = utilites.get_tmp_folder() #'/tmp/'
app.secret_key = os.environ.get('APP_SECRET_KEY')
if os.getenv("HEROKU_FLG", None):
    name_redis_env = "REDISCLOUD_URL"
    app.config['HEROKU_FLG']=True
else:
    name_redis_env = 'REDIS_URL'
    app.config['HEROKU_FLG'] = False
broker = os.environ[name_redis_env] # "redis://localhost"
backend = os.environ[name_redis_env]
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config['CELERY'] = dict(
    broker_url=broker,
    result_backend=backend,
    task_ignore_result=False,
    )
celery_app = celery_init_app(app)
app.extensions["celery"] = celery_app

ALLOWED_EXTENSIONS = set(['pdf'])
MAX_THREADS_DEFAULT = 7

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['GET'])
def upload_form():
    heroku_flg = current_app.config["HEROKU_FLG"]
    dd= 0
    return render_template('upload.html', flash='', heroku_flg=heroku_flg)


@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/policies',methods=['GET'])
def policies():
    return render_template('policies.html')


@app.route('/', methods=['POST'])
def upload_pdf():
    website = request.form['text']
    if website:
        if website.endswith('.pdf'):
            website = sanitize_url(website)
            url_parsed = urlparse(website)
            session['file'] = os.path.basename(url_parsed.path)
            session['type'] = 'url'
            metadata, pdfs, urls, arxiv, doi, task_id = pdfdata(website)
            return render_template('analysis.html',
                                   meta_titles=list(metadata.keys()),
                                   meta_values=list(metadata.values()),
                                   pdfs=pdfs,
                                   urls=urls,
                                   arxiv=arxiv,
                                   doi=doi,
                                   task_id=task_id
                                   )
        else:
            return render_template('upload.html', flash='pdf')
    else:
        if 'file' not in request.files:
            return render_template('upload.html', flash='')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', flash='none')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            session['file'] = filename.split('.')[0]
            session['type'] = 'file'
            file.save(path)
            metadata, pdfs, urls, arxiv, doi, task_id = pdfdata(path)
            return render_template('analysis.html',
                                   meta_titles=list(metadata.keys()),
                                   meta_values=list(metadata.values()),
                                   pdfs=pdfs,
                                   urls=urls,
                                   arxiv=arxiv,
                                   doi=doi,
                                   filename=filename,
                                   task_id=task_id)
        else:
            return render_template('upload.html', flash='pdf')


def pdfdata(path):
    metadata = dict()
    pdfs, urls, arxiv, doi = (list(),list(),list(),list())
    session['path'] = path
    task_id = pdfdata_task.delay(path)
    return metadata, pdfs, urls, arxiv, doi, task_id

@app.route('/downloadpdf', methods=['GET', 'POST'])
def downloadpdf():
    @ after_this_request
    def remove_file(response):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], session['file']+'.zip'))
        return response
    download_folder_path = os.path.join(
        app.config['UPLOAD_FOLDER'], session['file'])
    os.mkdir(download_folder_path)
    linkrot.linkrot(session['path']).download_pdfs(download_folder_path)
    shutil.make_archive(
        os.path.join(app.config['UPLOAD_FOLDER'], session['file']), 'zip', download_folder_path)
    if session['type'] == 'file':
        os.remove(session['path'])
    shutil.rmtree(download_folder_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], session['file']+'.zip', as_attachment=True)


@app.route('/check', methods=['GET'])
def check():
    args = request.args
    url = sanitize_url(args['url'])
    status = get_status_code(url)
    return str(status)

@app.route("/result/<id>",methods=['GET'])
def task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if (result.ready() and result.result) else None,
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
