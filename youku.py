# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import gluon.contrib.simplejson as sj
import hashlib
import time
import applications.downloader.modules.common as common

# youku error problem list:
# 1. api auth fail, because server time not mapping.
# 2. //stream[@type='flv']/seg/@url Here are no type = flv.
def download():  
    if not common.check_verify(request,session,db):
        return redirect('/')
        
    c = {}
    c['url'] = request.vars.url or ''
    if c['url']:
        auth = ''.join([(str(int(time.time()))),' XOA== MWZlNWE4Y2Q4OWQ0NjEyMWJjZTJmMWNiYTVhNzQwZGM='])
        auth = hashlib.md5(auth).hexdigest()
        videoid = c['url'].rsplit("/")[-1].split(".")[0][3:]
        #return videoid
        direct_url = ''.join([('http://api.youku.com/api_rest?method=video.getvideofile&'),'pid=XOA==&ctime=%s&auth=%s&videoid=%s'% (int(time.time()), auth, videoid)])
        headers = {'User-Agent':request.env.http_user_agent}
        http = httplib2.Http()
        try:
            resp, content = http.request(direct_url, headers = headers)
        except:
            return redirect('/')
        try:
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            movie_url = data.xpath("//stream[contains(@type,'flv')]/seg[1]/@url", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            movie_url = ''.join(movie_url)
            #print movie_url
        except:
            return sj.dumps(['error'])
        try:
            resp, content = http.request(c['url'], headers = headers)
        except:
            return redirect('/')    
        data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
        title = data.xpath("//title/text()")
        c['title'] = ''.join(title)
        
        c['movies'] = []
        c['screen'] = []
        c['sound'] = []
        c['container'] = []
        c['encoding'] = []
        c['rate'] = []
        c['movies'].append(movie_url)
        c['screen'].append('592x254')
        c['sound'].append('stereo')
        c['container'].append('FLV')
        c['encoding'].append('MPEG-4 AAC audio')
        c['rate'].append('44100 Hz')
            
    return sj.dumps(c)
