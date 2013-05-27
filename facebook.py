# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import cStringIO
import urllib
import urllib2
import cookielib
import gluon.contrib.simplejson as sj
import applications.downloader.modules.common as common
#T.force('en-us')
#print T.accepted_language
    
def download():
    if not common.check_verify(request,session,db):
        return redirect('/')
    c = {}   
    c['url'] = request.vars.url or ''
    c['movies'] = []
    c['screen'] = []
    c['sound'] = []
    c['container'] = []
    c['encoding'] = []
    c['rate'] = []
    if c['url']:
        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-Agent', request.env.http_user_agent)]
            urllib2.install_opener(opener)
            data = urllib.urlencode({'email':'python.tw@gmail.com','pass':'a157303'})
            link = 'http://www.facebook.com/login.php'
            f = opener.open(link)
            f = opener.open(link,data)
        except:
            return redirect('/')
        f = opener.open(c['url'])
        content = f.read()
        #f.close() # if close sure be occur cannot login
        try:
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            scripts = data.xpath("//script[contains(text(),'video_src')]", namespaces={"regxp": "http://exslt.org/regular-expressions"})
        except:
            return sj.dumps(['error'])
        title = data.xpath("//h3[@class='video_title datawrap']/text()")
        c['title'] = ''.join(title)
        
        output=''
        for x in scripts:
            output += lxml.etree.tostring(x)
        
        output = urllib2.unquote(output)
        movie_url = output[output.find('video_src')+13:output.find(')',output.find('video_src')+9)-1]
        #return movie_url
        c['movies'].append(movie_url)
        c['screen'].append('375x500')
        c['sound'].append('stereo')
        c['container'].append('FLV')
        c['encoding'].append('MPEG-4 AVC(H.264)')
        c['rate'].append('44100 Hz')
        c['paster'] = 'true'

    return sj.dumps(c)

