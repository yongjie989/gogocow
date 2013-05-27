# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import gluon.contrib.simplejson as sj
import base64
import re
import applications.downloader.modules.common as common

def download():
    if not common.check_verify(request,session,db):
        return redirect('/')
    try:
        c = {}
        c['url'] = request.vars.url or ''
        if c['url']:
            headers = {'User-Agent':request.env.http_user_agent}
            http = httplib2.Http()
            resp, content = http.request(c['url'], headers = headers)
            title = re.findall('<title>(.*)</title>',  content)
            if title:
                title = title[0]
                title = title[:title.find('FREE Streaming Online')-2]
                
            video_src = re.findall('file=(.*)"', content)
            if video_src:
                movie = video_src[1]
           
            c['title'] = title
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            c['movies'].append(movie)
            c['screen'].append('320x240')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('22050 Hz')
            c['paster'] = 'true'
        
        return sj.dumps(c)
    except:
        return sj.dumps(['error'])
