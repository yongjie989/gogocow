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
    c = {}
    c['url'] = request.vars.url or ''
    if c['url']:
        headers = {'User-Agent':request.env.http_user_agent}
        http = httplib2.Http()
        try:
            resp, content = http.request(c['url'], headers = headers)
        except:
            return redirect('/')
        try:
            title = re.findall('<title>(.*)</title>',  content)
            video_src = re.findall('sGlobalFileName=\'(.*)\';EmbedSEOLinkURL=', content)
            if video_src:
                video_src = video_src[0]
            token = re.findall('sGlobalToken=\'(.*)\';', content)
            if token:
                token = token[0]
            movie = video_src + '.flv?' + token
            
           
            c['title'] = title
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            c['movies'].append(movie)
            c['screen'].append('464x352')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('44100 Hz')
            c['paster'] = 'true'

            return sj.dumps(c)
        except:
            return sj.dumps(['error'])
