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
            vars = cgi.parse_qs(c['url'].split("?")[-1])
            id = vars['id'][0]
            video_src = 'http://video.libertytimes.com.tw/media/flv/%s.flv' % (id)
            print video_src
            if not video_src:
                return sj.dumps(['error'])

            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            c['title'] = data.xpath("//div[@id='videotitle']/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            c['title'] = c['title'][0]
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(video_src)
            c['screen'].append('480x386')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('MPEG 1 Audio, Layer 3 (MP3)')
            c['rate'].append('44100 Hz')
            #c['paster'] = 'true'
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    

