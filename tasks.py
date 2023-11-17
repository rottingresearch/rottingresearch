from celery import shared_task
from celery import group
import linkrot
from linkrot.downloader import sanitize_url, get_status_code
from urllib.parse import urlparse
from time import sleep

@shared_task(ignore_result=False)
def pdfdata_task(path):
    pdf = linkrot.linkrot(path)
    metadata = pdf.get_metadata()
    for key in metadata:
        if "Date" in key:
            value = metadata[key]
            metadata[key] = '{y}-{mo}-{d} {h}:{m} UTC{th}:{tm}'.format(d=value[8:10],
                                                                       mo=value[6:8],
                                                                       y=value[2:6],
                                                                       h=value[10:12],
                                                                       m=value[12:14],
                                                                       s=value[14:16],
                                                                       th=value[16:19],
                                                                       tm=value[20:22])
    refs = pdf.get_references()
    g = group(sort_ref.s(dict(reftype=ref_row.reftype, ref=ref_row.ref)) for ref_row in refs)
    res = g()
    while not res.ready():
        sleep(1)
    result_data = list()
    for child in res:
        result_data.append(child.result)
    return {'metadata': metadata, 'result_data': result_data}

@shared_task(ignore_result=False)
def sort_ref(ref_dict):
    result = dict(pdfs=[],
                    urls=[],
                    arxiv=[],
                    doi=[],
                    check = []
                  )
    if ref_dict['reftype'] == 'arxiv':
        url = "http://arxiv.org/abs/"+ref_dict['ref']
        result['arxiv'].append(url)
    elif ref_dict['reftype'] == 'doi':
        url = "http://doi.org/"+ref_dict['ref']
        result['doi'].append(url)
    else:
        url = ref_dict['ref']
    try:
        stat = str(get_status_code(url))
    except Exception as ex:
        stat = 0
    result["check"].append(stat)

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