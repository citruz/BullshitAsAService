import urllib2, Queue, threading, requests, random, codecs
from HTMLParser import HTMLParser

text_blocks = []

class BullshitHTMLParser(HTMLParser):
    headline_tags = ['h2', 'h3', 'h4', 'h5', 'h6']

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset_state()

    def reset_state(self):
        self.last_tag = ""
        self.last_headline = ""
        self.distance_to_headline = 0
        self.in_headline = False
        self.in_content = False
        self.last_content = ""

    def handle_starttag(self, tag, attrs):
        self.last_tag = tag
        if tag in self.headline_tags:
            self.in_headline = True
            self.in_content = False
            self.distance_to_headline = 0
            self.last_headline = ""
        elif tag == "p":
            self.in_headline = False
            self.in_content = True
        elif self.in_content == False:
            self.distance_to_headline += 1

    def handle_endtag(self, tag):
        self.last_tag = ""
        if tag in self.headline_tags:
            self.in_headline = False
        elif tag == "p":
            self.in_content = False
            if len(self.last_content) > 30:
                text_blocks.append((self.last_headline.strip(), self.last_content.strip()))
            
            self.reset_state()

    def handle_data(self, data):
        if self.in_headline and data.strip() != "":
            self.last_headline += data
            self.distance_to_headline = 0

        elif self.in_content and self.distance_to_headline < 3 and self.last_headline != "" and self.last_tag != "script" and data.strip() != "":
            data = data.replace("\t","")
            data = ' '.join(data.split())
            self.last_content += data


def read_url(url, queue):
    r = requests.get(url)
    data = r.text
    print('Fetched %s from %s' % (len(data), url))
    queue.put(data)

def fetch_parallel():
    result = Queue.Queue()
    with open('urlsv1.txt') as f:
        threads = [threading.Thread(target=read_url, args = (url,result)) for url in f]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return result
                

parser = BullshitHTMLParser()
q = fetch_parallel()

while not q.empty():
    data = q.get()
    try:
        parser.feed(data)
    except UnicodeDecodeError, e:
        parser.reset_state()
        parser.feed(unicode(data))
    finally:
        parser.reset_state()

print "Found", len(text_blocks), "text blocks"

random.shuffle(text_blocks)

with codecs.open('inputv1.txt', 'w', 'utf-8') as f:
    for text_block in text_blocks:
        f.write(text_block[0])
        f.write(":\n")
        f.write(text_block[1])
        f.write("\n\n")
