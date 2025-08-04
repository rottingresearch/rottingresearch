import os
import shutil
from datetime import timedelta
import linkrot
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, send_from_directory, after_this_request
from linkrot.downloader import sanitize_url, get_status_code
from celery_init import celery_init_app
from tasks import pdfdata_task
from celery.result import AsyncResult
from flask import Response, request
from datetime import datetime
from urllib.parse import urljoin
import utilites
import requests

app = Flask(__name__)
-app.config['UPLOAD_FOLDER'] = utilites.get_tmp_folder()  # '/tmp/'
app.secret_key = os.environ.get('APP_SECRET_KEY')

broker = os.environ['REDIS_URL']  # "redis://localhost"
backend = os.environ['REDIS_URL']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config['CELERY'] = dict(
    broker_url=broker,
    result_backend=backend,
    task_ignore_result=False,
)
app.config['CAPTCHA_KEY_ID'] = os.environ.get('CAPTCHA_KEY_ID')
app.config['CAPTCHA_SECRET_KEY'] = os.environ.get('CAPTCHA_SECRET_KEY')
app.config['ENV'] = os.environ.get('ENV')
celery_app = celery_init_app(app)
app.extensions["celery"] = celery_app

app.config['CAPTCHA_DISPLAY'] = "block" if app.config['ENV'] == "PROD" else "none"

ALLOWED_EXTENSIONS = set(['pdf'])
MAX_THREADS_DEFAULT = 30


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def upload_form():
    captcha_key = app.config['CAPTCHA_KEY_ID']
    captcha_display = app.config['CAPTCHA_DISPLAY']
    return render_template('upload.html', captcha=captcha_key, captcha_display=captcha_display, flash='')

@app.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    #app.logger.debug("↳ sitemap_xml() fired")    # Debug log
    """
    Generates an XML sitemap dynamically based on all accessible GET routes.
    Only includes routes that do not require parameters.
    """
    pages = []
    lastmod = datetime.now().date().isoformat()
    base_url = request.host_url.rstrip('/')
    # Loop through all routes in the app
    for rule in app.url_map.iter_rules():
        # Include only GET routes without arguments (i.e., static routes)
        if "GET" in rule.methods and len(rule.arguments) == 0:
            url = urljoin(base_url, rule.rule)
            pages.append(f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    # Wrap all collected URLs in the <urlset> tag
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>   
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(pages)}
</urlset>"""

    return Response(xml, mimetype='application/xml')

@app.errorhandler(404) 
# inbuilt function which takes error as parameter 
def not_found(e): 
  
# defining function 
    return render_template("404.html"),404 

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.route('/best-practices')
def practices():
    return render_template('practices.html')


@app.route('/research')
def research():
    return render_template('research.html')


@app.route('/story')
def story():
    return render_template('story.html')


@app.route('/policies')
def policies():
    return render_template('policies.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contribute')
def contribute():
    return render_template('contribute.html')


@app.route('/', methods=['POST'])
def upload_pdf():
    captcha_key = app.config['CAPTCHA_KEY_ID']
    captcha_display = app.config['CAPTCHA_DISPLAY']

    if 'file' not in request.files:
        return render_template('upload.html', captcha=captcha_key, captcha_display=captcha_display, flash='')
    
    file = request.files['file']
    if file.filename == '':
        return render_template('upload.html', captcha=captcha_key, captcha_display=captcha_display, flash='none')
    
    if file and allowed_file(file.filename):
        isCaptchaValid = validateCaptcha(request.form['g-recaptcha-response'])
        if isCaptchaValid:
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
            return render_template('upload.html', captcha=captcha_key, captcha_display=captcha_display, flash='captcha')
    else:
        return render_template('upload.html', captcha=captcha_key, captcha_display=captcha_display, flash='pdf')


def pdfdata(path):
    metadata = dict()
    pdfs, urls, arxiv, doi = (list(), list(), list(), list())
    session['path'] = path
    task_id = pdfdata_task.delay(path)
    return metadata, pdfs, urls, arxiv, doi, task_id


@app.route('/downloadpdf', methods=['GET', 'POST'])
def downloadpdf():
    @ after_this_request
    def remove_file(response):
        os.remove(os.path.join(
            app.config['UPLOAD_FOLDER'], session['file']+'.zip'))
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


@app.route('/check')
def check():
    args = request.args
    url = sanitize_url(args['url'])
    status = get_status_code(url)
    return str(status)


@app.route("/result/<id>")
def task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if (result.ready() and result.result) else None,
    }

def validateCaptcha(response: str):
    if app.config['ENV'] == "DEV":
        return True
    
    res = requests.post(
        'https://www.google.com/recaptcha/api/siteverify?secret='+app.config['CAPTCHA_SECRET_KEY']+'&response='+response).json()
    
    return res['success']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

