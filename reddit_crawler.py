#-------------------------------------------------------------------------------
# Name:        reddit_cralwler.py
# Purpose:     solution for the IDWall crawler challenge
#
# Author:      Jerome Vergueiro Vonk
#
# Created:     25/04/2018
#-------------------------------------------------------------------------------

import requests
from lxml import html

REDDIT_PREFIX = 'https://www.reddit.com/r/'

def createdThreadDict(node, subreddit):
    dict = {}

    # Likes are inside this container:
    #
    # <div class="score likes" title="2562">
    #
    likes_div = node.xpath('.//*[@class="score likes"]')

    # --------------------------------------------------
    # If score for likes not found, ignore this thread
    # --------------------------------------------------
    if not likes_div:
        # Return with empty dictionary
        return dict

    # Get the string
    likes_str = likes_div[0].text_content()

    # Since we want > 5k likes,
    # we are only interested in strings that contains 'k'
    if 'k' in likes_str:
        likes_str = likes_str.replace('k', '').replace('.', '')
        likes_int = int(likes_str) * 100
    else:
        try:
            likes_int = int(likes_str)
        except:
            # Return with empty dictionary
            return dict

    # ------------------------------------------
    # We want threads with 5000+ likes
    # ------------------------------------------
    if likes_int < 5000:
        # Return with empty dictionary
        return dict

    # Save the number of likes
    dict['likes'] = likes_int

    # Save the subreddit
    dict['subreddit'] = subreddit

    # Save the title
    title = node.xpath('.//p[@class="title"]//a')
    if title:
        dict['title'] = title[0].text_content()
    else:
        dict['title'] = "Error getting title"

    # Save the thread link
    thread_link = node.xpath('.//p[@class="title"]//a/@href')
    if thread_link:
        if thread_link[0].startswith('http'):
            dict['thread_link'] = thread_link[0]
        else:
            dict['thread_link'] = 'https://www.reddit.com' + thread_link[0]
    else:
        dict['thread_link'] = "Error getting thread link"


    # Save the comments link
    comments_link = node.xpath('.//li[@class="first"]//a/@href')
    if comments_link:
        dict['comments_link'] = comments_link[0]
    else:
        dict['comments_link'] = "Error getting comments link"

    return dict

def find_hot_threads(subreddits):

    # Split subreddits
    subreddits_list = subreddits.split(';')

    # List of hot threads
    hot_threads = []

    # New session
    s = requests.session()

    for subreddit in subreddits_list:
        addr = REDDIT_PREFIX + subreddit
        headers = {"User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"}

        nRetries = 5
        while nRetries:
            r = s.get(addr, headers=headers)

            # Get the text (Requests makes an educated guesses about the encoding)
            page_to_inspect = r.text

            # Parse a document from string
            parsed = html.document_fromstring(page_to_inspect)


            # The information we want is inside the following container:
            #
            # <div id="siteTable" class="sitetable linklisting">
            #
            try:
                site_table = parsed.xpath('//*[@class="sitetable linklisting"]')[0]
            except:
                # We are getting errors sometimes, so try a new session
                print("Did not find class \'sitetable linklisting\'. Retrying...")
                s = requests.session()
                nRetries -= 1
                continue

            # Cada child representa uma thread
            for child in site_table.xpath('div[*]'):
                thread_dict = createdThreadDict(child, subreddit)
                if thread_dict:
                    hot_threads.append(thread_dict)

            # If we reached here, break from the while loop
            break

    return hot_threads
