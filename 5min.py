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
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            title = data.xpath("//title/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            title = title[0].strip()
            c['title'] = title
            movie = re.findall('videoUrl=(.*)&pageUrl=', content)
            movie = urllib2.unquote(movie[0])

            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            c['movies'].append(movie)
            c['screen'].append('1280x720')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('44100 Hz')
            c['paster'] = 'true'

            return sj.dumps(c)
        except:
            return sj.dumps(['error'])
