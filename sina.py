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
            videoid = ''.join(re.findall("vid='(.*)'",content))
            if not videoid:
                videoid = ''.join(re.findall("vid :'(.*)'",content))
            if not videoid:
                return sj.dumps(['error'])
            flv_id = videoid.split("|")[0]

            if len(videoid.split("|")) > 1:
                hp_id = videoid.split("|")[1]
            resp, content = http.request('http://v.iask.com/v_play.php?vid=%s' % (flv_id), headers = headers)
            movie = re.findall('<url>.*</url>', content)
            
            c['title'] = re.findall('<vname>.*</vname>', content)
            c['title'] = c['title'][0][16:-11]
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            for x in movie:
                c['movies'].append(x[14:-9])
                c['screen'].append('640x480')
                c['sound'].append('stereo')
                c['container'].append('FLV')
                c['encoding'].append('H.264/AVC Video')
                c['rate'].append('22050 Hz')
            
            if len(videoid.split("|")) > 1:
                resp, content = http.request('http://v.iask.com/v_play.php?vid=%s' % (hp_id), headers = headers)
                movie = re.findall('<url>.*</url>', content)
                for x in movie:
                    c['movies'].append(x[14:-9])
                    c['screen'].append('640x480')
                    c['sound'].append('stereo')
                    c['container'].append('FLV')
                    c['encoding'].append('H.264/AVC Video')
                    c['rate'].append('44100 Hz')
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])

    
