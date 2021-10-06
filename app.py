import string
import re
import json
import os
from flask import Flask, flash, render_template, redirect, request, session, make_response, redirect, url_for, send_from_directory, after_this_request
import requests
from werkzeug.utils import secure_filename
import subprocess as sp
import linkrot
from datetime import timedelta
import shutil
from urllib.request import Request, urlopen, HTTPError, URLError

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/'
app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

ALLOWED_EXTENSIONS = set(['pdf'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html', flash='')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/', methods=['POST'])
def upload_pdf():
    website = request.form['text']
    if website:
        if website.endswith('.pdf'):
            session['file'] = website.split('/')[-1].split('.')[0]
            session['type'] = 'url'
            metadata, pdfs, urls, pdf_codes, url_codes = pdfdata(website)
            print(url_codes)
            return render_template('analysis.html', meta_titles=list(metadata.keys()), meta_values=list(metadata.values()), pdfs=pdfs, urls=urls, pdf_codes=pdf_codes, url_codes=url_codes)
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
            metadata, pdfs, urls, pdf_codes, url_codes = pdfdata(path)
            return render_template('analysis.html', meta_titles=list(metadata.keys()), meta_values=list(metadata.values()), pdfs=pdfs, urls=urls, pdf_codes=pdf_codes, url_codes=url_codes)
        else:
            return render_template('upload.html', flash='pdf')


def pdfdata(path):
    pdf = linkrot.linkrot(path)
    session['path'] = path
    metadata = pdf.get_metadata()
    references_dict = pdf.get_references_as_dict()
    pdfs = []
    urls = []
    pdf_codes = []
    url_codes = []
    if 'pdf' in references_dict:
        pdfs = references_dict['pdf']
    if 'url' in references_dict:
        urls = references_dict['url']
    for p in pdfs:
        pdf_codes.append(get_status_code(p))
    for u in urls:
        url_codes.append(get_status_code(u))
    return metadata, pdfs, urls, pdf_codes, url_codes


@app.route('/download', methods=['GET', 'POST'])
def download():
    @after_this_request
    def remove_file(response):
        os.remove(app.config['UPLOAD_FOLDER']+session['file']+'.zip')
        return response
    download_folder_path = os.path.join(
        app.config['UPLOAD_FOLDER'], session['file'])
    print(download_folder_path)
    os.mkdir(download_folder_path)
    linkrot.linkrot(session['path']).download_pdfs(download_folder_path)
    shutil.make_archive(
        app.config['UPLOAD_FOLDER']+session['file'], 'zip', download_folder_path)
    if session['type'] is 'file':
        os.remove(session['path'])
    shutil.rmtree(download_folder_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], session['file']+'.zip', as_attachment=True)


def get_status_code(url):
    try:
        r = requests.head(url)
        return r.status_code
    except:
        return 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
