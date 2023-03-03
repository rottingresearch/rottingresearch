from celery import shared_task
from celery import group
import linkrot
from linkrot.downloader import sanitize_url
from urllib.parse import urlparse
from celery.utils.log import get_task_logger
from time import sleep
logger = get_task_logger(__name__)

@shared_task(ignore_result=False)
def pdfdata_task(path):
    pdfs = []
    urls = []
    arxiv = []
    doi = []

    pdf = linkrot.linkrot(path)
    metadata = pdf.get_metadata()
    refs = pdf.get_references()
    g = group(sort_ref.s(dict(reftype=ref_row.reftype, ref=ref_row.ref)) for ref_row in refs)
    res = g()
    while not res.ready():
        logger.info("wait")
        sleep(1)
    result_data = list()
    for child in res:
        result_data.append(child.result)
        dd= 0
    #return metadata, pdfs, urls, arxiv, doi
    return {'metadata':metadata, 'result_data':result_data}

@shared_task(ignore_result=False)
def sort_ref(ref_dict):
    result = dict(pdfs=[],
                    urls=[],
                    arxiv=[],
                    doi=[],
                  )
    if ref_dict['reftype'] == 'arxiv':
        url = "http://arxiv.org/abs/"+ref_dict['ref']
        url = sanitize_url(url)
        result['arxiv'].append(url)
    elif ref_dict['reftype'] == 'doi':
        url = "http://doi.org/"+ref_dict['ref']
        url = sanitize_url(url)
        result['doi'].append(url)
    url = sanitize_url(ref_dict['ref'])
    if ref_dict['reftype'] == 'url':
        host = urlparse(url).hostname
        if host and host.endswith("doi.org"):
            result['doi'].append(url)
        elif host and host.endswith("arxiv.org"):
            result['arxiv'].append(url)
        else:
            result['urls'].append(url)
    elif ref_dict['reftype'] == 'pdf':
        result['pdfs'].append(url)

    return result