# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import gluon.contrib.simplejson as sj
import applications.downloader.modules.common as common
#T.force('en-us')
#print T.accepted_language     
        
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
            scripts = data.xpath("//script[contains(text(),'vdoPath')]", namespaces={"regxp": "http://exslt.org/regular-expressions"})
        except:
            return sj.dumps(['error'])
        title = data.xpath("//title/text()")
        c['title'] = ''.join(title)
        c['title'] = c['title'].rsplit('-',1)[0].strip()

        output=''
        for x in scripts:
            output += lxml.etree.tostring(x)
        
        output = urllib2.unquote(output)
        
        movie_url = output[output.find('vdoPath=')+8:output.find('"',output.find('vdoPath='))]
        
        c['movies'] = []
        c['screen'] = []
        c['sound'] = []
        c['container'] = []
        c['encoding'] = []
        c['rate'] = []
        c['movies'].append(movie_url)
        c['screen'].append('320x239')
        c['sound'].append('mono')
        c['container'].append('FLV')
        c['encoding'].append('MPEG 1 Audio, Layer 3 (MP3)')
        c['rate'].append('22050 Hz')
        c['paster'] = 'true'

    return sj.dumps(c)
