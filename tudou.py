# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import cookielib
import os
import re
import gluon.contrib.simplejson as sj
import applications.downloader.modules.common as common

def download():
    if not common.check_verify(request,session,db):
        return redirect('/')
    c = {}
    c['url'] = request.vars.url or ''
    if c['url']:

        c['movies'] = []
        c['screen'] = []
        c['sound'] = []
        c['container'] = []
        c['encoding'] = []
        c['rate'] = []
        
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', request.env.http_user_agent)]
        urllib2.install_opener(opener)
        try:
            f = opener.open(c['url'])
        except:
            return redirect('/')
        cj.save(os.path.join(request.folder,'static/tudou.cookie'))
        content = f.read()
        f.close()
        
        try:
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='gbk') )
            scripts = data.xpath("//script[1]", namespaces={"regxp": "http://exslt.org/regular-expressions"})

            title = data.xpath("//title/text()")
            c['title'] = ''.join(title)
            c['title'] = c['title'].rsplit(u'－',1)[0].strip()

            output=''
            for x in scripts:
                output += lxml.etree.tostring(x)
                
            output = urllib2.unquote(output)
            f=open('/tmp/test','wa')
            f.write(output)
            f.close()
            #if not find iid, that mean old format, using another code to capture movie_iid
            movie_iid = output[output.find('iid')+5:output.find('iid')+15]
            movie_iid = re.findall("\d{8,12}", movie_iid)
            if movie_iid:
                movie_iid = movie_iid[0]
            
            if len(movie_iid) == 0:
                scripts = data.xpath("//script[1]", namespaces={"regxp": "http://exslt.org/regular-expressions"})

                output=''
                for x in scripts:
                    output += lxml.etree.tostring(x)
                movie_iid = re.findall("\d{8,12}", output)

                if movie_iid:
                    movie_iid = movie_iid[0]

            if len(movie_iid) == 0:
                movie_iid = re.findall("\d{8,12}", content)
                print movie_iid
                if movie_iid:
                    movie_iid = movie_iid[0]
                    
            f = opener.open('http://v2.tudou.com/v?it=%s' % (movie_iid))
            content = f.read()
            f.close()
            
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            scripts = data.xpath("//f/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            
            for x in scripts:
                c['movies'].append(x)
                c['screen'].append('448x336')
                c['sound'].append('stereo')
                c['container'].append('F4V')
                c['encoding'].append('MPEG-4 AAC audio')
                c['rate'].append('44100 Hz')
                c['paster'] = 'true'
        except:
            return sj.dumps(['error'])

    return sj.dumps(c)
