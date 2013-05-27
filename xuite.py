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
        
        #get video src xml
        try:
            http = httplib2.Http()
            resp, content = http.request(c['url'], headers = headers)
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            media = data.xpath("//link[@rel='video_src']/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            media = ''.join(media)
            media = media.rsplit("/",1)[-1]
            media = media.split("&")[0]
            url = urllib2.quote(c['url'])
            xml_url = 'http://vlog.xuite.net/flash/player?media=%s==&refer=%s' % (media,url)
            resp, content = http.request(xml_url, headers = headers)
            
            print xml_url
        except:
            return redirect('/')
        try:
            flv_src = urllib2.unquote(base64.decodestring(re.findall('<property id="c3Jj">(.*)]]></property>',content)[0][9:]))
            flv_size = base64.decodestring(re.findall('<property id="c2l6ZQ==">(.*)]]></property>',content)[0][9:])
            c['title'] = urllib2.unquote(base64.decodestring(re.findall('<property id="dGl0bGU=">(.*)]]></property>',content)[0][9:]))
            #hq_src = urllib2.unquote(base64.decodestring(re.findall('<property id="aHFfc3Jj">(.*)]]></property>',content)[0][9:]))
            #print hq_src == ''
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(flv_src)
            c['screen'].append(flv_size)
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('MPEG-4 AVC(H.264)')
            c['rate'].append('44100 Hz')            
        except:
            return sj.dumps(['error'])

    return sj.dumps(c)
