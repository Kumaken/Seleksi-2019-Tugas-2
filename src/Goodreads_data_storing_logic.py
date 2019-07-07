#Dependencies-------------------------------------------------------------------------------------------------------
import json
import sys  # to accept bash input parameter
import pymysql.cursors  # bridge between Python and MySQL
from dateutil.parser import parse #3rd party library that parses string to datetime objects. pretty helpful.
import datetime
#-------------------------------------------------------------------------------------------------------------------
#How To Run:--------------------------------------------------------------------------------------------------
# command: python Goodreads_data_storing_logic.py <desired genre>
# example: python Goodreads_data_storing_logic.py mystery
#-------------------------------------------------------------------------------------------------------------------
#Static Variables:--------------------------------------------------------------------------------------------------
genre = sys.argv[1]
tablename = genre+"_table"
mastertable = 'master_'+tablename
#-------------------------------------------------------------------------------------------------------------------

#MySQL Database Setup-----------------------------------------------------------------------------------------------
DB_connection = pymysql.connect(host='localhost',
        user='root',
        passwd='Nyo-chocobis123',
        db='goodreadsdb',
        cursorclass=pymysql.cursors.DictCursor)
#-------------------------------------------------------------------------------------------------------------------
#Main Code:---------------------------------------------------------------------------------------------------------
with DB_connection.cursor() as cursor:
    with open('data/sorted_top_books_'+genre+'.json', encoding = "utf-8") as f:
        #MASTER TABLE-----------------------------------------------------------------------------------------------
        #Drop the table if already existing.
        cursor.execute("DROP TABLE IF EXISTS "+ mastertable)
        #Create a new table in a clean slate.
        cursor.execute("CREATE TABLE `"+mastertable+"""` (
            `id` INT(11) NULL DEFAULT NULL,
            `title` TEXT NULL,
            `author` TEXT NULL,
            `genre` TEXT NULL,
            `ISBN` TEXT NULL,
            `series` TEXT NULL,
            `avg_rating` FLOAT NULL DEFAULT NULL,
            `pages` INT(11) NULL DEFAULT NULL,
            `rating_count` INT(11) NULL DEFAULT NULL,
            `review_count` INT(11) NULL DEFAULT NULL,
            `book_format` TEXT NULL,
            `published_year` INT(11) NULL DEFAULT NULL,
            `publisher` TEXT NULL
        )
        COMMENT='Master table for """+genre+""" genre. Contains every single attributes relevant to the genre from the .json data file.'
        COLLATE='utf8mb4_0900_ai_ci'
        ENGINE=InnoDB
        ;""")
        #-------------------------------------------------------------------------------------------------------------------
        #MASTER TABLE-----------------------------------------------------------------------------------------------

        data = json.load(f)
        for datum in data:
            try:
                #ISBN null check:
                isbn = datum['ISBN']
                if isbn == '':
                    isbn = None
                #Series null check:
                series = datum['series']
                if series == '':
                    series = None
                else:
                    try:
                        series = (series.split("#")[0])[1:] #get the series name only, before the '#' mark
                    except:
                        series = series[1:-1]
                #book_format:
                format = datum['book_format']
                if format == '':
                    format = None
                #published null date check:
                try:
                    published_year=parse(datum['published_year']).date().year
                except: #if no published year is provided
                    published_year=None
                #page count check
                try:
                    pagecount=int(datum['pages'])
                except: #if no published year is provided
                    pagecount=None
                #publisher null check:
                publisher= datum['publisher']
                if publisher == '':
                    publisher = None
                cursor.execute("INSERT INTO "+mastertable+"(id, title, author, genre, ISBN, series, avg_rating, pages, rating_count, review_count, book_format, published_year, publisher) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (int(datum['id']), datum['title'], datum['author'], genre, isbn, series, float(datum['avg_rating']), pagecount, int(datum['rating_count']), int(datum['review_count']), format, published_year, publisher))
            except Exception as e:
                print("Exception Occured!!!")
                print(e)
                #print(datum)

#close the connection to the database.
DB_connection.commit()
cursor.close()
#-------------------------------------------------------------------------------------------------------------------
