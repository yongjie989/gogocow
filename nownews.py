# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import gluon.contrib.simplejson as sj
import base64
import re
import cgi
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
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='big5') )
            video_src = data.xpath("//param[@name='movie']/@value", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            video_src = video_src[0]
            vars = cgi.parse_qs(video_src.split("?")[-1])
            id = vars['id'][0]
            cdate = vars['cdate'][0]
            video_src = 'http://www.nownews.com/flv/%s/%s.flv' % (cdate, id)
            
            c['title'] = data.xpath("//div[@id='video_top']//h1/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            c['title'] = c['title'][0]
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(video_src)
            c['screen'].append('400x300')
            c['sound'].append('mono')
            c['container'].append('FLV')
            c['encoding'].append('MPEG 1 Audio, Layer 3 (MP3)')
            c['rate'].append('22050 Hz')
            #c['paster'] = 'true'
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    

