# coding: utf-8
### nlehuby - AccraMobile3

import requests
import xml.dom.minidom as dom
from lxml import html


def dl_track(track_url, track_name, destination="."):
    #TODO : skip download if the file already exist ?
    r = requests.get(track_url)
    with open(destination + track_name, "wb") as code:
        code.write(r.content)

def download_from_rss(rss_url, destination="."):
    rss = requests.get(rss_url)

    dom3 = dom.parseString(rss.content)
    tracks = dom3.getElementsByTagName("item")

    for a_track in tracks:
        title_elem = a_track.getElementsByTagName('title')[0]
        title = title_elem.childNodes[0].data
        url_elem = a_track.getElementsByTagName('link')[0]
        track_id = url_elem.childNodes[0].data.split('/')[-1]
        track_url = "http://www.openstreetmap.org/trace/{}/data".format(track_id)
        dl_track(track_url, title, destination)

def download_last_tracks_from_user(user, destination="."):
    url1 = "http://www.openstreetmap.org/user/"+user+"/traces/rss"
    download_from_rss(url1, destination)

def download_last_tracks_from_tag(tag, destination="."):
    url1 = "https://www.openstreetmap.org/traces/tag/"+tag+"/rss"
    download_from_rss(url1, destination)

def collect_tracks_from_one_page(page_prefix, page_id):
    page_url = "{}/page/{}".format(page_prefix, page_id) #"https://www.openstreetmap.org/traces/tag/abidjantransport/page/4"
    page = requests.get(page_url)
    tree = html.fromstring(page.content)

    trace_names = tree.xpath('//tr/td[2]/a[1]/text()')
    trace_links = tree.xpath('//tr/td[2]/a[1]/attribute::href')

    results = []
    for id_, trace_name in enumerate(trace_names):
        elem = {}
        elem['name'] = trace_name
        elem['user'] = trace_links[id_].split('/')[2]
        elem['trace_id'] = trace_links[id_].split('/')[-1]
        elem['track_url'] = "http://www.openstreetmap.org/trace/{}/data".format(elem['trace_id'])
        results.append(elem)
    return results

def collect_all_tracks_from_tag(tag):
    elems = []
    for page_number in range(124):
        result_page = collect_tracks_from_one_page("https://www.openstreetmap.org/traces/tag/{}".format(tag), page_number +1)
        elems += result_page
        if not result_page :
            break
    return elems

def download_all_tracks_from_tag(tag, destination="."):
    traces_info = collect_all_tracks_from_tag(tag)
    for elem in traces_info :
        dl_track(elem['track_url'], elem['name'], destination)
    return traces_info

if __name__ == '__main__':
    for index in range(10):
        user_id = "accramobileghana" + str(index +1)
        download_last_tracks_from_user(user_id)
