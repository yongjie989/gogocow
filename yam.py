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
            c['title'] = scripts = data.xpath("//h1[@class='heading']/span/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            c['title'] = ''.join(c['title'])
            scripts = data.xpath("//link[@rel='audio_src']/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            video_id = ''.join(scripts).split("=")[-1]
            url = 'http://mymedia.yam.com/api/a/?pID=%s' % (video_id)
            resp, content = http.request(url, headers = headers)
            video_src = content[content.find("mp3file=")+8:content.find("&")]
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(video_src)
            c['screen'].append('None')
            c['sound'].append('stereo')
            c['container'].append('MP3')
            c['encoding'].append('MPEG 1 Audio, Layer 3 (MP3)')
            c['rate'].append('44100 Hz')
            c['paster'] = 'true'
        except:
            return sj.dumps(['error'])

    return sj.dumps(c)
