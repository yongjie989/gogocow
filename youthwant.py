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
            if content.count("embed src=http://www.youtube.com"):
                return sj.dumps(['error'])
            video_src = re.findall('(http://.*\.flv)',content)
            if not video_src:
                return sj.dumps(['error'])
            if video_src:
                video_src = video_src[0]
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='big5') )
            c['title'] = data.xpath("//div[@class='filetitlebox']//strong/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            c['title'] = ''.join(c['title'])
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(video_src)
            c['screen'].append('640x360')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('22050 Hz')
            c['paster'] = 'true'
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    
