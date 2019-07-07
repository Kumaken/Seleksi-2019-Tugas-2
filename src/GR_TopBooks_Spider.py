#NOTE TO SELF-------------------------------------------------------------------------------------------------------
'''
1. Goodreads is one of my favourite site and scraping it is quite fun, but sometimes it can drive you MAD. There's one bug in goodreads API I think (or the way it is designed is really frustrating). If you are not logged in, https://www.goodreads.com/shelf/show/<genre>?page=3 will still show page 1... (I've wasted like TONS of hours cause of this "strange" behaviour -_-)

2. Scrapy framework is used because of its async behaviour with Twisted async networking library. It enables concurrency, which of course, plays important factor in spider performance.

3. Beautiful soup is also used in tandem with Scrapy just because I wanted to try both frameworks to judge for myself. beautiful soup is only content extractor though. To send HTTP requests, I need other frameworks, such as requests OR scrapy's request library. (And BS being very simple and having a friendly learning curve is a great boon)

4. Scraped data from GR website is going to be stored in .json file as requested by the assignment. However, it also makes a .csv file for easier view, and in case it is needed...

5. Scrapy's spider runs asynchronously, id given to each entry does not reflect the real order of the data as shown in the webpage. 

6. On windows environment, Scrapy does not support python3!!!

7. Inputting path to terminal with whitespaces in it will cause problems. Surround that path with double quotes instead!

8. Install specific package with pip: use ==x.y.z (version number). To get information about current version, do: pip show <package_name>

9. Avoid having both python 2.7 n 3.7 at once? Causes scrapy to always pick 2.7 no matter what I am running out of my patience...
'''
#-------------------------------------------------------------------------------------------------------------------
#Dependencies-------------------------------------------------------------------------------------------------------
import csv, json #for writing csvs and jsons:
import scrapy #framework for asynchronous html data extractor and parser (VERSION: >=1.6 )
#Twisted : version >= 1.89.0
from scrapy.http import Request #send http requests with scrapy framework. it is not included with default import!!!
from bs4 import BeautifulSoup as bs #beautiful soup to parse html data received
import io #to write to file, especially with utf-8 encoding
import re #complex string splitting
#-------------------------------------------------------------------------------------------------------------------

#How to run---------------------------------------------------------------------------------------------------------
# COMMAND to run the spider:
# scrapy runspider src/GR_TopBooks_Spider.py -a username=<GR Username> -a password=<GR Password> -a genre=<desired genre> -a intial_page_num=<start page> -a last_page_num=<last page>
# 
# However... If by any means any of the required parameters is not provided, custom default value will be issued instead. So don't get upset plz.
# Here is the simplified command to run the spider with default configuration:
# COMMAND: scrapy runspider src/GR_TopBooks_Spider.py
# 
# ALSO: if you want your data to be sorted by id and you need .json file, run data_organizer.py!
# COMMAND: python src/data_organizer.py <genre>
#
# WARNING: RUN all of the above commands at project root!
#-------------------------------------------------------------------------------------------------------------------

#Static Variables:---------------------------------------------------------------------------------------------------
base_url = "https://www.goodreads.com/shelf/show/"
# Input from bash: self.username, self.password, self.genre, self.init_page_num, self.last_page_num
fieldnames = ['id','title', 'author', 'ISBN', 'series', 'avg_rating', 'pages', 'rating_count', 'review_count', 'book_format','published_year', 'publisher'] #headers for .csv
#-------------------------------------------------------------------------------------------------------------------

#Goodreads TopBooks Spider Class------------------------------------------------------------------------------------
class GoodreadsSpider(scrapy.Spider):
    name = "Goodreads_spider"
    #Initial URL for spider to begin crawling:
    start_urls = ['https://www.goodreads.com/']
    #Prevent crawling to unwanted sites:
    allowed_domains = ['www.goodreads.com']
    #set user agent: <IMPORTANT: CHANGE THIS TO ACCORDING TO YOUR BROWSER'S USER AGENT!
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

    _id = 0 #for enumeration & to handle the fact that scrapy spider is asynchronous.

    def parse(self, response):
        with io.open('data/top_books_' + self.genre +'.csv', 'w', encoding = "utf-8") as f:
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writerow({'id':'id','title':'title', 'author':'author', 'ISBN':'ISBN', 'series':'series', 'avg_rating':'avg_rating', 'pages':'pages', 'rating_count':'rating_count', 'review_count':'review_count', 'book_format':'book_format',  'published_year' : 'published_year', 'publisher':'publisher'}) #write header to csv
        #test if input parameters is given or not. If not given, set to default value. AL
        #username
        try:
            assert len(self.username) > 0
        except:
            self.username = '13517068@std.stei.itb.ac.id'
        #password
        try:
            assert len(self.password) > 0
        except:
            self.password = 'testgrspider'
        #genre
        try:
            assert len(self.genre) > 0
        except:
            self.genre = 'horror'
        #init_page_num
        try:
            assert len(self.init_page_num) > 0
        except:
            self.init_page_num = 1
        #last_page_num
        try:
            assert len(self.last_page_num) > 0
        except:
            self.last_page_num = 5

        #send formdata with post request using scrapy framework:
        return scrapy.FormRequest.from_response(response,
            formdata={'user[email]': self.username, 'user[password]': self.password},
            callback=self.after_login)

    def after_login(self, response):
        # check if login is successful or not:
        if b"recognize that email" in response.body:
            print ("Error desu!")
            return
        else:
            #authenticated: use callback to call the real webscraper with current status of being logged in
            #make get requests to every pages until last_page_num is reached, calls GR_Web_Scraper function.
            for i in range(int(self.last_page_num)):
                yield Request(url="https://www.goodreads.com/shelf/show/" + self.genre + "?page=" + str(i+1), callback=self.GR_Web_Scraper)
    

    def GR_Web_Scraper(self, response):
        #use beautiful soup to parse the HTML object response:
        bsoup = bs(response.body, 'html.parser')
        #find all href links to individual book detail pages:
        book_detail_pages= bsoup.find_all('a', class_='bookTitle')
        
        #send request to every book detail pages in the corresponding page, calls Get_Individual_Book_Details function
        for page in book_detail_pages:
            self._id+=1 #give ID and embed it into response meta parameter so it can be processed later down the line
            link = page['href'] #get the link from the title text hyperlink
            yield Request(url=self.start_urls[0]+link, callback=self.Get_Individual_Book_Details, meta={'id':self._id})


    def Get_Individual_Book_Details(self, response):
        #use beautiful soup to parse the HTML object response:
        bsoup = bs(response.body, 'html.parser')
        #Extract every single data as indicated by the .csv headers (details in fieldnames var above)
        #fill Book Title:
        book_title = bsoup.find('h1', id='bookTitle', class_='gr-h1 gr-h1--serif').get_text().rstrip().lstrip()
        #fill Book Author:
        book_author = bsoup.find('a', class_='authorName').findChild('span', itemprop ='name').get_text().rstrip().lstrip()
        #fill Book ISBN: Special Touch is needed. Not all books has ISBN, like books from hundred of years ago. Books without ISBN will be filled with 'NULL' value
        listtemp = bsoup.find('div', id='bookDataBox', class_='uitext').findChildren('div', class_='clearFloats') #get all contents from the small data box on website
        book_ISBN = None
        for x in listtemp:
            temp = x.findChild('div', class_='infoBoxRowTitle', text='ISBN')
            if  temp != None: #This book has ISBN
                book_ISBN = temp.find_next_sibling('div', class_='infoBoxRowItem').find(text=True, recursive=False).rstrip().lstrip()
                break
            #otherwise NULL value is assigned.
        #fill Book_Series data. Need special touch too. Not all books are in a series!
        try:
            #not all books are in series (some are standalones). Thus, books without series are assigned 'none' value
            book_series = bsoup.find('h2', id='bookSeries').findChild('a', class_='greyText').get_text().rstrip().lstrip() #find child returns the first child node. Find children returns ResultSet object. Pay attention!
        except:
            book_series = None
        #fill book average rating data:
        book_rating = bsoup.find('span', itemprop='ratingValue').get_text().rstrip().lstrip()
        #fill book pages data. Special touch: need to parse string as the data gotten contains 'pages' word too. Also, page data is converted to Int.
        try:
            temp = bsoup.find('span', itemprop='numberOfPages').get_text().rstrip().lstrip()
            book_pages = int(''.join(filter(str.isdigit, temp))) #get only numeric vals
        except: #special case when there's no page number on the book page
            print("----------------------------------------")
            print("No page number!!!")
            print(book_title)
            book_pages = None
            print("----------------------------------------")
        #fill book rating count data. Special touch: need to parse string as the data gotten contains 'ratings' word too. Also, rating count data is converted to Int.
        temp = bsoup.find('meta', itemprop='ratingCount').get_text().rstrip().lstrip()
        book_rating_count = int(''.join(filter(str.isdigit, temp))) #get only numeric vals
        #fill book review count data. Special touch: need to parse string as the data gotten contains 'reviews' word too. Also, review count data is converted to Int.
        temp = bsoup.find('meta', itemprop='reviewCount').get_text().rstrip().lstrip()
        book_review_count = int(''.join(filter(str.isdigit, temp))) #get only numeric vals
        #fill book format: Paperback/Digital/Kindle Edition/Hardcover/Audiobook/etc.
        try:
            book_format = bsoup.find('span', itemprop='bookFormat').get_text().rstrip().lstrip()
        except: #Special case when there is no book format listed on goodreads page
            print("----------------------------------------")
            print("No book format!!!")
            print(book_title)
            print(book_author)
            print("----------------------------------------")
            book_format = None
        #publishing details : published date and book's publisher. need special string parsing cause raw data collected is in jumbled string form.
        try:
            book_publishing_details = re.split(r'\s{2,}', bsoup.find('div', id='details', class_='uitext').findChildren('div', class_='row')[1].find(text=True,recursive=False).rstrip().lstrip().strip('\r\n').replace('\n','')) # [1] : 'published' text, useless. [2]: published date. [3]: publisher data
        except:
            print("----------------------------------------")
            print("No publishing details at all???")
            print(book_title)
            print(book_author)
            print("----------------------------------------")
        try:
            book_published_year = book_publishing_details[1]
        except: #Special case when there is no published year listed on goodreads page
            print("----------------------------------------")
            print("No publishing year!!!")
            print(book_title)
            print(book_author)
            print("----------------------------------------")
            book_published_year = None
        try:
            book_publisher = book_publishing_details[2][3:]
        except: #Special case when there is no publisher listed on goodreads page
            print("----------------------------------------")
            print("No publisher details!!!")
            print(book_title)
            print(book_author)
            print("----------------------------------------")
            book_publisher = None
        
        #write to csv:
        with io.open('data/top_books_' + self.genre +'.csv', 'a', encoding = "utf-8") as f: #use utf-8, as there are some fancy characters in book's or author's names.
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writerow({
                        'id' : int(response.meta.get('id')),
                        'title': book_title, 
                        'author': book_author,
                        'ISBN' : book_ISBN,
                        'series' : book_series, 
                        'avg_rating': book_rating,
                        'pages' : book_pages,
                        'rating_count': book_rating_count,
                        'review_count' : book_review_count,
                        'book_format' : book_format,
                        'published_year' : book_published_year,
                        'publisher' : book_publisher})

#-------------------------------------------------------------------------------------------------------------------