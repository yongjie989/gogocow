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
            title = title[0]
            video_id = re.findall('flvId=\'(.*)\'',content)
            if video_id:
                video_id = video_id[0]
            video_secname = re.findall('videoSecName=\'(.*)\'', content)
            if video_secname:
                video_secname = video_secname[0]
#            video_type = re.findall('flvTp=\'(.*)\'', content)
#            if video_type:
#                video_type = video_type[0]
#                if video_type == '3':
#                    video_type = 'low'
#                if video_type == '2':
#                    video_type = 'medium'
#                if video_type == '1':
#                    video_type = 'high'
            movies = []        
            movies.append('http://videos.bollywoodhungama.com/%s/low/%s.flv' % (video_secname, video_id))
            movies.append('http://videos.bollywoodhungama.com/%s/medium/%s.flv' % (video_secname, video_id))
            movies.append('http://videos.bollywoodhungama.com/%s/high/%s.flv' % (video_secname, video_id))
            
            c['title'] = title
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []
            for x in movies:
                c['movies'].append(x)
                c['sound'].append('stereo')
                c['container'].append('FLV')
                c['encoding'].append('H.264/AVC Video')
                c['rate'].append('44100 Hz')
                c['paster'] = 'true'
            c['screen'].append('320x240 (Low)')
            c['screen'].append('640x480 (Medium)')
            c['screen'].append('640x480 (High)')
            return sj.dumps(c)
        except:
            return sj.dumps(['error'])
