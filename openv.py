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
            c['title'] = re.findall("<title>(.*)</title>", content)
            c['title'] = c['title'][0].rsplit('-',1)[0]
        except:
            return redirect('/')
        try:
            pid = c['url'].rsplit('/',1)[-1].split('.')[0].split('-')[-1]
            if not pid:
                return sj.dumps(['error'])

            resp, content = http.request('http://casting.openv.com/PLGS/plgs.php?pid=%s' % (pid), headers = headers)
            movie = re.findall('<flvpath>(.*)</flvpath>', content)
            print movie
            
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            for x in movie:
                c['movies'].append(x)
                c['screen'].append('576x432')
                c['sound'].append('stereo')
                c['container'].append('FLV')
                c['encoding'].append('H.264/AVC Video')
                c['rate'].append('48000 Hz')
                c['paster'] = 'true'

            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    
