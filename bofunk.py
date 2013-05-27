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
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            video_id = data.xpath("//link[@rel='video_src']/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            if video_id:
                video_id = video_id[0].rsplit('/', 1)[-1]
                resp, content = http.request('http://flv.bofunk.com/watch.php?file=%s' % video_id, headers = headers)
                movie = re.findall('<PLAYER_SETTINGS Name="FLVPath" Value="(.*)"/>', content)
                movie = ''.join(movie)
            
           
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
