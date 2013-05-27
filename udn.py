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
            sno = c['url'].split("sno=")[-1]
            url = 'http://video.udn.com/video/Item/ListRelateMD.do?sno=%s' % (sno)
            resp, content = http.request(url, headers = headers)
            video_src = re.findall('<vc id="(.*)">',content)
            video_src = 'http://video.udn.com' + video_src[0]
            if not video_src:
                return sj.dumps(['error'])

            c['title'] = re.findall('<title>(.*)</title>',content)
            c['title'] = c['title'][0]
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            c['movies'].append(video_src)
            c['screen'].append('440x330')
            c['sound'].append('stereo')
            c['container'].append('FLV')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('44100 Hz')
            #c['paster'] = 'true'
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    
