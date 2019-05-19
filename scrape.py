import requests
import json
import datetime
import os
from bs4 import BeautifulSoup

def send_texts(message, config_file):
    headers = {
        'Content-Type': 'application/json',
    }
    with open(config_file) as json_file:
        config = json.load(json_file)
        url_base = config['url']
        for user in config['all_users']:
            print(user)
            payload = {
                'number': user['number'],
                'message': message,
                'carrier': user['carrier'],
            }
            text_url = url_base + user['location_path']
            response = requests.post(text_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            print(user['number'], " - ", response.json())

# output for logging            
print("------------------------------------------------------------------------")
print(datetime.datetime.now())

# get path for project (this is needed to use crontab in linux)
project_path = os.path.dirname(os.path.abspath(__file__))

# set file names
last_update_file = project_path + "/lastupdate"
config_file = project_path + "/config.json"

# specify the url
scrape_url = 'https://brandonsanderson.com/'

# query the website and return the html to the variable 'page'
page = requests.get(scrape_url)

# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(page.text, 'html.parser')

# get progress bar div to limit the page
progress_bar = soup.find(attrs={'class': 'progress-titles'})

# get list of book titles
name_box = progress_bar.find_all(attrs={'class': 'book-title'})

# get progress of the books
status_box = progress_bar.find_all(attrs={'class': 'progress'})

# if problem with scrapping
if len(name_box) != len(status_box) or len(name_box) == 0 or len(status_box) == 0: 
    raise RuntimeError("Titles and Status arrays don't match.")

# handle the data scrapped
else:
    final_output = "Brandon Sanderson Status Update:"
    index = 0
    # create data string to be sent
    while index < len(name_box):
        final_output += ("<br>  " + name_box[index].text + " - " + status_box[index].find('div', attrs={'class': 'after'}).text)
        index += 1

    try:
        print()
        save_file = open(last_update_file, "r")
        last_update = save_file.read()
        save_file.close()
    except IOError:
        last_update = ""

    # new update so update and send message(s)
    if last_update != final_output:
        print(final_output)
        send_texts(final_output, config_file)
        save_file = open(last_update_file, "w")
        save_file.write(final_output)
        save_file.close()