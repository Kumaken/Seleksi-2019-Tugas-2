#NOTE TO SELF-------------------------------------------------------------------------------------------------------
'''
1. Goodreads trivia page navigation is controlled with javascript button or ajax requests, and not HTML link, so Selenium is the right choice here I think, rather than scrapy or beautifulsoup. This can be proven as when you click an answer to any question of the trivia, the URL on your chrome header does not change at all.
Selenium + chromedriver simulates real user input to a webpage (like clicks and typings), so it is much slower :(

2. Chromedriver is needed! Rest assured, it is included in the package :)

3. Dummy goodreads account is provided for login. Hack it, attack it, steal it, whatever, I don't mind. Though I really prefer that you don't :(

4. Result is written in JSON format.
'''
#-------------------------------------------------------------------------------------------------------------------
 
#How to run---------------------------------------------------------------------------------------------------------
# Command to run the spider:
# python <filename>.py

# yes. Just like that. Just run the .py file.
# BUT! remember to put chromedriver in the same directory as the .py file!
#-------------------------------------------------------------------------------------------------------------------
# #Dependencies-------------------------------------------------------------------------------------------------------
import time #for sleep function
import io #to write to file, especially with utf-8 encoding
import json #for dumping and reading jsons:
from bs4 import BeautifulSoup #beautiful soup to extract and parse html data received
from selenium import webdriver
#IMPORTANT: user must copy chromedriver.exe into the same directory as this .py file!
driver = webdriver.Chrome() #use chromedriver
#driver.set_window_position(-2000,0)#this function will minimize the window, in case it is desired?
#-------------------------------------------------------------------------------------------------------------------

#Static Variables:---------------------------------------------------------------------------------------------------
login_url = "https://www.goodreads.com/user/sign_in"
#-------------------------------------------------------------------------------------------------------------------

#prepare files to be written on:------------------------------------------------------------------------------------
fjson = io.open('data/trivia_cheat_sheet' + '.json', 'w', encoding = "utf-8")
jsondata = {} #prepare dictionary data type
jsondata['trivia_cheat_sheet'] = [] #prepare list for 'top_books' key
#-------------------------------------------------------------------------------------------------------------------

#Login to Goodreads function:---------------------------------------------------------------------------------------
def site_login():
    #use the default account credentials: my dummy test account with my std email :)
    driver.get(login_url)
    driver.find_element_by_id("user_email").send_keys("13517068@std.stei.itb.ac.id")
    driver.find_element_by_id("user_password").send_keys("testgrspider")
    driver.find_element_by_name("next").click()
#-------------------------------------------------------------------------------------------------------------------

#Spider main function:----------------------------------------------------------------------------------------------
def run_spider():
    driver.get("https://www.goodreads.com/trivia") #send the spider to goodreads trivia page
    #i = 0
    error = False
    while True:
        try:
            #important! let the spider wait for at least 3 seconds before trying to read any HTML content. Wait until page content is fully loaded
            time.sleep(3)
            driver.find_element_by_css_selector(".answerButton.quizAnswerText").click() #compound class names must use dot & css_selector. Currently selenium does not support compound class otherwise.
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            try:
                question = soup.find('div', class_="quizQuestionText").get_text().strip('\n').lstrip().rstrip() #get the last question text of the trivia. Strip any trailing or leading whitespaces.
            except: #in case something went wrong, spider must move on XD
                correct_ans = ''
            try:
                #Get the correct answer, colored in green in the left tab after attempting to asnwer the quiz. Strip any trailing or leading whitespaces.
                correct_ans = driver.find_element_by_css_selector(".quizAnswerText.correct").text.strip('\n').lstrip().rstrip() 
                #correct_ans = soup.findElement(By.cssSelector(".quizAnswerText.correct")).find("a").get_text() #the other way with By operator from scrapy
            except: #in case something went wrong, spider must move on XD
                correct_ans = ''

            print("Question: ", question)
            print("Answer  : ", correct_ans)
            jsondata['trivia_cheat_sheet'].append({'question':question, 'answer':correct_ans})
            #i+=1
        except:
            print("error occured desu!")
            #when finisihed, dump the jsondata to fjson. csv does not require extra touch.
            json.dump(jsondata, fjson, indent = 4, ensure_ascii = False)
            error = True
            break
    if(not error):
        #when finisihed, dump the jsondata to fjson. csv does not require extra touch.   
        json.dump(jsondata, fjson, indent = 4, ensure_ascii = False)       

#MAIN COMMAND:
if __name__ == '__main__':
    site_login() #login to the site with selenium and chromedriver.
    run_spider() #start scraping