from BeautifulSoup import BeautifulSoup
from collections import defaultdict
import re
import hashlib
import json
import nltk
import sys
from datetime import datetime
import urllib
import urllib2
from threading import Thread
import extract
import operator

from BeautifulSoup import BeautifulSoup


class WebsiteMiner(Thread):
    def __init__(self, category):
        super(WebsiteMiner, self).__init__()
        self.category = category
        self.mined_posts_hashes = []

    def run(self):
        self.log("Starting mining.")
        urls = self.category.urls.split(',')
        for url in urls:
            try:
                visible_text, last_modified = self.download_page(url)
                text_hash = hashlib.sha1(visible_text.encode('utf-8'))
                if text_hash not in self.mined_posts_hashes:
                    terms_dict = extract.extract_terms(visible_text)
                    now = datetime.now().strftime('%Y%m%d%H%M')
                    time = last_modified.strftime('%Y%m%d%H%M')
                    post = WebsiteMiner.dict_of_post(url, terms_dict, time, now)
                    batch = WebsiteMiner.package_batch_to_json(self.category.id, [post])
                    self.send_to_parent(self.category.parent_id, batch)
                    self.mined_posts_hashes.append(hash)
                else:
                    print("Post already mined.")

            except Exception as e:
                print e.message, e.args

    def stop(self):
        self.log("Stopping mining.")

    def log(self, text):
        print "Miner:{} - {}".format(self.category.id, text)

    # website specific static methods
    def download_page(self, uri):
        try:
            res = urllib.urlopen(uri)
            info = dict(res.info())
            time = datetime.now()
            if 'last-modified' in info:
                time_str = info['last-modified']
                time = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %Z')

            html = res.read()
            soup = BeautifulSoup(html)
            text = self.find(soup, 'p') \
                    + self.find(soup, 'h1') \
                    + self.find(soup, 'h2') \
                    + self.find(soup, 'h3')

            return text, time
        except:
            print "Error loading " + uri, sys.exc_info()
            return ""

    def find(self, soup, tag):
        elements = soup.findAll(tag)
        lines = [e.text for e in elements if len(e.text) > 0]
        return ' '.join(lines)

    # standard engine communication static methods
    @staticmethod
    def send_to_parent(url, data):
        url += "/v1/minerpost"
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        try:
            urllib2.urlopen(req)
        except Exception as e:
            print "Exception while sending data to engine at the uri: {}".format(url)
            print e

    @staticmethod
    def dict_of_post(post_url, terms_dict, last_modified, mined_at):
        post = {
           "terms": terms_dict,
           "url": post_url,
           "datetime": last_modified,
           "mined_at": mined_at
        }
        return post

    @staticmethod
    def package_batch_to_json(id_of_miner, posts):
        values = {
           "posts": posts,
           "miner_id": id_of_miner
        }
        data = json.dumps(values)
        return data
