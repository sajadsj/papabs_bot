import urllib3
from bs4 import BeautifulSoup
import goslate
from tinydb import TinyDB
from tinydb import Query

import telegram.ext
from telegram.ext import *
import tok

# Initial telegram bot
token = tok.tok
updater = Updater(token, use_context=True)
jobs = updater.job_queue


def get_paper(context: telegram.ext.CallbackContext):
    # get soup
    http = urllib3.PoolManager()
    r = http.request('Get', 'https://scholar.google.com/scholar?hl=en&scisbd=1&as_sdt=0%2C5&q='
                     + 'cognitive+psychology' + '&btnG=')
    print("status: " + str(r.status))
    soup = BeautifulSoup(r.data, 'lxml')

    # Initiate translator
    gt = goslate.Goslate()

    # initial paper database
    db = TinyDB('./db.json')
    papers_ids = Query()
    # Container where all needed data is located
    for result in soup.select('.gs_ri'):
        paper_id = result.select_one('.gs_rt a')['id']
        title = result.select_one('.gs_rt').text
        title_link = result.select_one('.gs_rt a')['href']
        publication_info = result.select_one('.gs_a').text
        snippet = result.select_one('.gs_rs').text
        cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
        related_articles = result.select_one('a:nth-child(4)')['href']
        try:
            all_article_versions = result.select_one('a~ a+ .gs_nph')['href']
        except:
            all_article_versions = None

            # check the list if it's not repetitive,
            if bool(db.search(papers_ids.paper_id == paper_id)) == False:
                # prepare a proper face
                paper = "\n\tTitle: " + title + "\nعنوان:" + gt.translate(title,
                                                                          'fa') + "\n\nSnipped:\t " + snippet + "\nLinke:" + title_link

                print(paper)
                # send to channel
                context.bot.sendMessage(chat_id='@Papabs_fa', text=paper)
                # add paper ID to a list, update the file
                db.insert({'paper_id': paper_id, 'Title': title,
                           'Title link': title_link, 'Publication Info': publication_info,
                           'Snippet': snippet, 'Cited by': cited_by, 'Related articles': related_articles,
                           'all_article_versions': all_article_versions})


job_minute = jobs.run_repeating(get_paper, interval=3600, first=1)

updater.start_polling()

updater.idle()
