#!/usr/bin/env python3

import requests
import json
import re
import logging
import os.path
import textwrap

from bs4 import BeautifulSoup

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 0

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True


url = { 
    'base':      'https://www.lifecubby.me',
    'login':     'https://www.lifecubby.me/login.html',
    'hub' :      'https://www.lifecubby.me/cubby_hub.html',
    'entry' :    'https://www.lifecubby.me/cubby_view.html?entryid={}&saveit=Yes',
    'download' : 'https://www.lifecubby.me/d',
}


credentials_file = './credentials.json'

# for storing filename index values
index = { }


def load_creds(f):
    j={}

    j = json.load(open(f))
    j['command'] = 'Login'
    j['_flash'] = 'enabled'
    j['_javascript'] = 'enabled'
    j['UPLOAD_IDENTIFIER'] = '1'
    j['MAX_FILE_SIZE'] = '100000'

    return j


# takes requetss object, deals with it.
# returns dict of things to fetch + metadata)
def parse_entry(r):

    entry = {}

    soup = BeautifulSoup(r.text, 'html.parser')

    entry['title'] = re.sub('.*entry title:', '', soup.find(id='entry_title-field').text, flags=re.I).strip()

    entry['date'] = re.sub('.*date:', '', soup.find(id='date-field').text, flags=re.I).strip()

    desc = soup.find('div', id=re.compile(r'(activity_purpose__goals__objective-field|observation-field)'))
    if desc: 
        entry['description'] = re.sub('^.*(objective|observation):\s+', '', desc.text , flags=re.I|re.M|re.S).strip()
    else:
        entry['description'] = '<none>'
            

    #entry_title-field//*[@id="entry_title-field"]

    attachments = []
    for attach in soup.find_all(class_='attachment'):
    #for attach in soup.find_all(class_='attachment', id=re.compile(r'^img\d+')):
        m = re.search('id=(\d+)',attach.a.get('href'))
        if m:
            download_url = '{}/{}'.format(url['download'], m.group(1))
            attachments.append(download_url)
        #attachments.append(attach.a.get('href'))

    entry['attachments'] = attachments
    #entry['attachments'] = list(map(lambda x: url['base'] + x, attachments))

    return entry


def make_filename(title, date,index):

    # 05/22/2017
    month,day,year = date.split('/')
    newdate = '{}-{}-{}'.format(year,month,day)

    newtitle = re.sub('\W+','_',title.strip())
    newtitle = re.sub('[^a-zA-Z0-9]$','',newtitle)

    if index is None:
        return '{}-{}'.format(newdate,newtitle)

    if newtitle in index:
        index[newtitle]+=1
    else:
        index[newtitle] =1

    filename = '{}-{}-{}'.format(newdate,newtitle,index[newtitle])

    return filename 



def fetch_file(url,filename):

    r = session_request.get(url)

    if not r:
        logging.err('Failed to fetch {}'.format(url))
        return None

    if r.headers['Content-Type'] == 'image/png':
        extension = 'png'
    elif r.headers['Content-Type'] == 'video/quicktime':
        extension = 'mov'

    filename = filename + '.' + extension

    if os.path.isfile(filename):
        logging.info("Already have {}  Please remove it to re-fetch.".format(filename))
        return -1

    logging.info("Fetching [{}] to {}.".format(url,filename))

    if r.status_code == 200:
        try:
            fd = open(filename, 'wb')
        except:
            logging.err("failed opening {} for writing!".format(filename))

        fd.write(r.content)
        
    else:
        logging.err("Something bad happened!")

    return r.status_code




def extract_image(page):

    print('==========-----------===============')
    print(page.text)
    attachment_soup = BeautifulSoup(page.text, 'html.parser')
    img_src = attachment_soup.find('img')
    print(img_src)
    if img_src:
        #print(img_src.get('src'))
        return img_src.get('src')



if __name__ == '__main__':

    payload = load_creds(credentials_file)
    
    session_request = requests.session()
    session_request.headers.update({'referer': url['login']})

    login = session_request.post(
            url['login'], 
            data=payload, 
            allow_redirects=True, 
            )

    print('=================')
    print(login.status_code)
    print(login.headers)
    print(login.cookies)
    print(login.history)
    print(login.url)
    #print(login.text)
    print('-----------------')

    soup = BeautifulSoup(login.text, 'html.parser')
    
    #print(soup.prettify())

    #entries = soup.find_all(class_='entry')


    for link in soup.find_all(class_='preview', limit=4):
        raw_src=link.get('href')

        entry_url = url['base'] + raw_src
        print(entry_url)


        entry = parse_entry(session_request.get(entry_url))

        print(entry)

        if entry:

            for attachment in entry['attachments']:
                filename=make_filename(entry['title'], entry['date'],index)
                #print("new filename={}".format(filename))
                print("attachment url = " + attachment)

                rc = fetch_file(attachment, filename)

                metadata_filename = make_filename(entry['title'], entry['date'], None)+'.txt'
                if rc:
                    try:
                        fd = open(metadata_filename, 'w', newline='\n')
                    except:
                        logging.err("failed opening {} for metadata writing!".format(metadata_filename))

                    fd.write('Title: {}\n'.format(entry['title']))
                    fd.write('Date: {}\n'.format(entry['date']))
                    fd.write(textwrap.fill('Description: ' + entry['description'])+'\n')

