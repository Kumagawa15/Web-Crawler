import requests
import threading
import queue
import csv
import validators
import time

from urllib.request import Request, urlopen, URLError, urljoin
from urllib.parse import urlparse
from datetime import datetime 
from bs4 import BeautifulSoup

from multiprocessing import Lock

#Get html content on first URL
startUrl = 'http://komputasi.lipi.go.id/utama.cgi?depan'
outputName = 'WebCrawler.csv'

lst = []
freq = []
temp = []

#Max executed time
timeout = 30.0
#Max url crawled
maxUrl = 10

#Start time
startTime = time.time()

class crawler(threading.Thread):
    def getResponse(self):
        currentTime = datetime.now()
        response = requests.get(startUrl)
        soup = BeautifulSoup(response.content, 'html5lib')
        return soup

    def __init__(self, startUrl_locks, startUrl):
        threading.Thread.__init__(self)
        self.startUrl_locks = startUrl_locks
        self.startUrl = startUrl

    def urlScrapping(self, soup, w):
        for row in soup.findAll('a', href = True):
            self.startUrl_locks.acquire()
            startUrl = self.startUrl
            self.startUrl_locks.release()

            newUrl = row['href']
            parsed = urlparse(newUrl)
            splitUrl = parsed.netloc
            temp.append(splitUrl)
            isTimeout = self.timeoutChecker()
            if isTimeout == False:
              self.webCrawler(newUrl, w)
            else:
              break
    
    def appendToDict(self, w):
      countDict = {i:temp.count(i) for i in temp}
      lst = [url for (url, count) in countDict.items()]
      freq = [count for (url, count) in countDict.items()]
      for k,v in countDict.items():
        w.writerow([k,v])
      return

    def webCrawler(self, url, w):
        #Start web crawling
        soup = self.getResponse()
        self.urlScrapping(soup, w)

    def timeoutChecker(self):
        currentTime = time.time()
        checker = currentTime - startTime
        print(checker)
        if checker < timeout:
            return False
        else:
            return True

    def main(self):
      with open(outputName, 'w', newline = '') as f:
        header = ['Scrapped URL', 'Frequency']
        w = csv.writer(f, delimiter=',')
        w.writerow(header)
        
        asd = self.webCrawler(startUrl, w)
        self.appendToDict(w)
        print('Web Crawler Success')

if __name__ == "__main__":
  startUrl_locks = Lock()
  cr = crawler(startUrl_locks = startUrl_locks, startUrl = startUrl)
  cr.main()