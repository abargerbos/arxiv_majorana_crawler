import urllib
import feedparser
from datetime import datetime
import database_manipulation

# Base api query url
base_url = 'http://export.arxiv.org/api/query?'

# Search parameters
search_keywords = ['all:majorana+AND+cat:cond-mat.mes-hall',
                'au:kouwenhoven+AND+cat:cond-mat.mes-hall',
                'au:c+m+marcus+AND+cat:cond-mat.mes-hall']

# search for majorana in all fields and category cond-mat.mes-hall
start = 0                     # retreive the first 50 results
max_results = 50
sorting_order = '&sortBy=submittedDate&sortOrder=descending'

def _convert_time(val):
    """
    Changes the date-time string format
    """
    date = datetime.strptime(val,'%Y-%m-%dT%H:%M:%SZ')
    return date.strftime("%Y-%m-%d %H:%M:%S")

def _remove_newlines(val):
    """Strips line breaks from the title string"""
    return val.replace('\n  ', ' ')

def _join_authors(val):
    """Makes a single string as the author list"""
    return ', '.join([val[i]['name'] for i in range(len(val))])


result_list = []

for search_query in search_keywords:
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                        start,
                                                        max_results)

    d = feedparser.parse(base_url+query+sorting_order)

    for entry in d.entries:
        dic_stored = {}
        dic_stored['id'] = entry.id.split('/')[-1].split('v')[0]
        dic_stored['author_list'] = _join_authors(entry.authors)
        dic_stored['title'] = _remove_newlines(entry.title)
        dic_stored['arxiv_primary_category'] = entry.arxiv_primary_category['term']
        dic_stored['published'] = _convert_time(entry.published)
        dic_stored['link'] = entry.link
        result_list.append(dic_stored)

old_db = database_manipulation.load_database('dummydatabase.pkl')
new_db = database_manipulation.create_dataframe(result_list)
updated_db = database_manipulation.update_database(old_db, new_db)
database_manipulation.save_database(updated_db, 'dummydatabase.pkl')


