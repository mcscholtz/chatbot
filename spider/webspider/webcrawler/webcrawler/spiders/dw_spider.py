import scrapy
import pickle
from time import sleep
from HTMLParser import HTMLParser

class LinksParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0
    self.data = []

  def handle_starttag(self, tag, attributes):
    if tag != 'body':
      return
    else:
      self.recording = 1
      #print "BODY START"

  def handle_endtag(self, tag):
    if tag == 'body' and self.recording:
      self.recording = 0
      #print "BODY END"

  def handle_data(self, data):
    if self.recording == 1:
      if data != '' and data != '\r\n':      
        self.data.append(data)


class QuotesSpider(scrapy.Spider):
    name = "chakoteya"

    def start_requests(self):
        urls = []        
                
        for i in range(1,80):        
            urls.append('http://www.chakoteya.net/StarTrek/'+str(i)+'.htm')
        
        for i in range(1,24):        
            if i < 10:
                i = '0'+str(i)
            else:
                i = str(i)            
            urls.append('http://www.chakoteya.net/StarTrek/TAS0'+i+'.htm')
        
        for i in range(101,278):        
            urls.append('http://www.chakoteya.net/NextGen/'+str(i)+'.htm')

        for i in range(401,576):        
            urls.append('http://www.chakoteya.net/DS9/'+str(i)+'.htm')
        
        for i in range(101,723):        
            urls.append('http://www.chakoteya.net/Voyager/'+str(i)+'.htm')

        for i in range(1,99):        
            if i < 10:
                i = '0'+str(i)
            else:
                i = str(i)            
            urls.append('http://www.chakoteya.net/Enterprise/'+i+'.htm')

        for i in range(1,11):        
            urls.append('http://www.chakoteya.net/movies/movie'+str(i)+'.html')
        
        for i in range(101,523):        
            urls.append('http://www.chakoteya.net/Andromeda/'+str(i)+'.htm')        
        
        for i in range(1,37):        
            for j in range(1,20):            
                urls.append('http://www.chakoteya.net/DoctorWho/'+str(i)+'-'+str(j)+'.htm')

        for i in range(100,507):            
            urls.append('http://www.chakoteya.net/SJA/'+str(i)+'.htm')

        for i in range(101,411):            
            urls.append('http://www.chakoteya.net/Torchwood/'+str(i)+'.htm')

        for i in range(101,108):            
            urls.append('http://www.chakoteya.net/Torchwood/'+str(i)+'.html')
                

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            sleep(1) #wait 1 second between each page

    def parse(self, response):
        parser = LinksParser()        
        parser.feed(response.body)
        page = response.url.split("/")
        num = page[len(page)-1]
        series = page[len(page)-2]
        num = num.split('.')[0]
        filename = series+num+'.dump'
        #with open(filename, 'wb') as f:
            #f.write(parser.data)
        with open(filename, 'wb') as file:
            pickle.dump(parser.data, file)
        self.log('Saved file %s' % filename)
