#!/usr/bin/env python3

import sys
import re
import json
import requests

def getHTMLContent(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'
    }
    r = requests.get(url, headers=headers)
    return r.text

def getVideoID(html):
    m = re.search(r'var video_id  = "(.*)";', html)
    return m.group(1)

def getVideoPart(videoID, part):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69',
        'X-Requested-With': 'XMLHttpRequest'
    }
    payload = {
        'video_id': videoID,
        'part_name': '720p',
        'page': part
    }
    r = requests.post('http://seriesever.net/service/get_video_part', headers=headers, data=payload)
    return json.loads(r.text)

def resolveParts(parts):
    links = []
    for part in parts:
        if part['source'] == 'url':
            links.append(resolveCDN(part['code']))
        elif part['source'] == 'other':
            links.append(resolveIFrame(part['code']))
    return links

def resolveCDN(code):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69',
    }
    payload = {'link': code}
    r = requests.post('http://se.watchpass.net/sevr/plugins/playerphp.php', headers=headers, data=payload)
    links = json.loads(r.text)
    if 'error' in links:
        print("Error resolving CDN: {}".format(links['error']))
        return None
    elif 'link' in links and type(links['link']) is str:
        return links['link']
    else:
        # myCDN
        return links['link'][0]['link']

def resolveIFrame(code):
    m = re.search(r'<iframe.*src="(.*?)"', code)
    return m.group(1)

def main():
    url = sys.argv[1]

    html = getHTMLContent(url)

    videoID = getVideoID(html)
    print("Video ID is: {}".format(videoID))

    part = getVideoPart(videoID, 0)
    print("{} stream(s) are available".format(part['part_count']))
    parts = [part['part']]
    if not part['one_part']:
        for i in range(1, part['part_count']):
            part = getVideoPart(videoID, i)
            parts.append(part['part'])

    links = resolveParts(parts)
    for link in links:
        print(link)

if __name__ == '__main__':
    main()