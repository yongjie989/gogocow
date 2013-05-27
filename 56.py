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
            pid = c['url'].split('-')[-1].split('.')[0]
            if pid.count("http"):
                pid = c['url'].rsplit('/',1)[-1].split('.')[0].split('_')[-1]
            if not pid:    
                return sj.dumps(['error'])
            resp, content = http.request('http://vxml.56.com/json/%s/?src=site' % (pid), headers = headers)
            title = re.findall('"Subject":"(.*)","textid"', content)
            c['title'] = title[0]

            movie = re.findall('"url":"(http://.*\.flv)","type":"normal".*"url":"(http://.*\.flv)"', content)
            if movie:
                movie = movie[0]
            if not movie:
                movie = re.findall('"url":"(http://.*\.flv)","type"', content)
            
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
