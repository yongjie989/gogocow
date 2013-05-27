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
            clipid = re.findall('clip_id=(.*)', content)
            clipid = clipid[0].split('"')[0]
            resp, content = http.request('http://vimeo.com/moogaloop/load/clip:%s' % clipid, headers = headers)
            signature = re.findall('<request_signature>(.*)</request_signature>', content)
            expires = re.findall('<request_signature_expires>(.*)</request_signature_expires>',content)
            movie = 'http://vimeo.com/moogaloop/play/clip:%s/%s/%s/?q=hd&type=local&embed_location=' % (clipid, signature[0], expires[0])
            c['title'] = title
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            c['movies'].append(movie)
            c['screen'].append('640x480')
            c['sound'].append('stereo')
            c['container'].append('MP4')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('44100 Hz')
            c['paster'] = 'true'
        
        return sj.dumps(c)
    except:
        return sj.dumps(['error'])
