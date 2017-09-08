#!/usr/bin/env python3

import re
import logging
import os.path
import textwrap
import json
import requests

from bs4 import BeautifulSoup

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 0

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.INFO)
#requests_log.propagate = True


url = {
    'base':      'https://www.lifecubby.me',
    'login':     'https://www.lifecubby.me/login.html',
    'hub' :      'https://www.lifecubby.me/cubby_hub.html',
    'entry' :    'https://www.lifecubby.me/cubby_view.html?entryid={}&saveit=Yes',
    'download' : 'https://www.lifecubby.me/d',
    'load_more' :'https://www.lifecubby.me/ajax/load_more.php',
}


credentials_file = './credentials.json'

# for storing filename index values
index = {}


def load_creds(credfile):
    j = {}

    j = json.load(open(credfile))
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

    entry['url'] = r.url

    entry['title'] = re.sub(r'.*entry title:',
                            '',
                            soup.find(id='entry_title-field').text,
                            flags=re.I).strip()

    entry['date'] = re.sub(r'.*date:',
                           '',
                           soup.find(id='date-field').text,
                           flags=re.I).strip()

    desc = soup.find('div', id=re.compile(r'(activity_purpose__goals__objective-field|observation-field)'))
    if desc:
        entry['description'] = re.sub(r'^.*(objective|observation):\s+',
                                      '',
                                      desc.text,
                                      flags=re.I|re.M|re.S).strip()
    else:
        entry['description'] = '<none>'


    #entry_title-field//*[@id="entry_title-field"]

    attachments = []
    for attach in soup.find_all(class_='attachment'):
    #for attach in soup.find_all(class_='attachment', id=re.compile(r'^img\d+')):
        match = re.search(r'id=(\d+)', attach.a.get('href'))
        if match:
            download_url = '{}/{}'.format(url['download'], match.group(1))
            attachments.append(download_url)
        #attachments.append(attach.a.get('href'))

    entry['attachments'] = attachments
    #entry['attachments'] = list(map(lambda x: url['base'] + x, attachments))

    return entry


def make_filename(title, date, index):

    # 05/22/2017
    month, day, year = date.split('/')
    newdate = '{}-{}-{}'.format(year, month, day)

    newtitle = re.sub(r'\W+', '_', title.strip())
    newtitle = re.sub(r'[^a-zA-Z0-9]$', '', newtitle)

    if index is None:
        return '{}-{}'.format(newdate, newtitle)

    if newtitle in index:
        index[newtitle] += 1
    else:
        index[newtitle] = 1

    filename = '{}-{}-{}'.format(newdate, newtitle, index[newtitle])

    return filename



def fetch_file(url, filename):

    req = session_request.get(url)

    if not req:
        logging.error('Failed to fetch %s' % str(url))
        return None

    if req.headers['Content-Type'] == 'image/png':
        extension = 'png'
    elif req.headers['Content-Type'] == 'video/quicktime':
        extension = 'mov'

    filename = filename + '.' + extension

    if os.path.isfile(filename):
        logging.info("Already have {}  Please remove it to re-fetch.".format(filename))
        return -1

    logging.info("Fetching [{}] to {}.".format(url, filename))

    if req.status_code == 200:
        try:
            fd = open(filename, 'wb')
        except OSError:
            logging.error("failed opening {} for writing!".format(filename))

        fd.write(req.content)
        fd.close()

    else:
        logging.error("Something bad happened!")

    return req.status_code




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

    pages = []
    pages.append(login.text)

    bowl = []
    seen = {}

    login_soup = BeautifulSoup(login.text, 'html.parser')

    bowl.append(login_soup)

    # seed the "seen" list with the first batch.
    logging.info("Adding entries from initial page at login")
    for link in login_soup.find_all(class_='preview'):
        l = link.get('href')

        if l not in seen:
            seen[l] = True
            logging.info("New login link: {}".format(l))
        else:
            logging.info("Previously seen login link: {}".format(l))


    # fetch more pages, until it wraps around...
    # load_more.php returns up to 5 links at a time,
    # then loops again, in batches of 5
    done = False
    while not done:

        another_page = session_request.get(url['load_more'])
        soup = BeautifulSoup(another_page.text, 'html.parser')

        found = 0
        for link in soup.find_all(class_='preview'):
            l = link.get('href')
            if l not in seen:
                seen[l] = True
                found += 1
                logging.info("New more link: {}".format(l))
            else:
                logging.info("Previously seen more link: {}".format(l))

        if not found:
            done = True
        else:
            bowl.append(soup)



    #print(soup.prettify())

    #entries = soup.find_all(class_='entry')
    logging.info("Final url list: {}".format(str(seen)))

    for soup in bowl:

        for link in soup.find_all(class_='preview', limit=4):
            raw_src = link.get('href')

            entry_url = url['base'] + raw_src
            #print(entry_url)


            entry = parse_entry(session_request.get(entry_url))

            print(entry)

            if entry:

                metadata_filename = make_filename(entry['title'], entry['date'], None)+'.txt'
                if os.path.isfile(metadata_filename):
                    logging.info("Metadata file {} alreadt exists.  Skipping this one.".format(metadata_filename))
                    continue

                try:
                    fd = open(metadata_filename, 'w', newline='\n')
                except OSError:
                    logging.error("failed opening {} for metadata writing!".format(metadata_filename))

                fd.write('Title: {}\n'.format(entry['title']))
                fd.write('Date: {}\n'.format(entry['date']))
                fd.write(textwrap.fill('Description: ' + entry['description'])+'\n')

                fd.close()

                for attachment in entry['attachments']:
                    filename = make_filename(entry['title'], entry['date'], index)
                    #print("new filename={}".format(filename))
                    print("attachment url = " + attachment)

                    rc = fetch_file(attachment, filename)

