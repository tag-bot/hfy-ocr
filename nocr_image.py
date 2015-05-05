import requests
import json
import sys
from os import path
from time import sleep

KEY='1f90833f0cd9d3403c32fff56dc7e4ba'

def upload_image(fpath):
    fname = path.basename(fpath)
    result = requests.post('http://api.newocr.com/v1/upload?key=%s' % KEY, files=[('file', (fname, open(fpath, 'rb'), 'image/jpg' ))])

    if result.status_code == 200:
        content = json.loads(result.content)
        file_id = content['data']['file_id']
        pages = content['data']['pages']

        sleep(10)
        return (file_id, pages)

    print 'Unable to upload image', result.status_code, result.content
    sys.exit()

def ocr_url(url):
    result = requests.get(url)
    if result.status_code == 200:
        filename = '/tmp/%s' % path.basename(url)
        with open(filename, 'wb') as f:
            f.write(result.content)

        print filename
        return ocr_image(filename)
        
    else: 
        print 'Unable to download %s' % url
        print result.status_code, result.content

def ocr_image(fpath):
    file_id, pages = upload_image(fpath)

    for page in range(1, int(pages)+1):
        result = requests.get('http://api.newocr.com/v1/ocr', params={'file_id':file_id, 'lang':'eng', 'page':page, 'key':KEY})

        if result.status_code == 200:
            content = json.loads(result.content)
            text = content['data']['text']
            
            return text.encode('utf-8')

    print 'Unable to OCR image', result.status_code, result.content


def format_for_reddit(text):
    lines = text.split('\n')
    ret = []

    for line in lines:
        if line.startswith('>>') or line.startswith('Anonymous'):
            continue
        if line == '':
            ret += ['']

        ret += [line]

    return '\n'.join(ret)

def main():
    from sys import argv

    txt = ocr_url(argv[1])
    print format_for_reddit(txt)


if __name__ == '__main__':
    main()
