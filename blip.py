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
            movie = re.findall('player.setPrimaryMediaUrl(.*)', content)
            movie = movie[0].split('?')[0][2:]
            title = re.findall('<div id="EpisodeTitle">(.*)</div>',  content)
            c['title'] = title
            c['movies'] = []
            c['screen'] = []
            c['sound'] = []
            c['container'] = []
            c['encoding'] = []
            c['rate'] = []

            c['movies'].append(movie)
            c['screen'].append('640x352')
            c['sound'].append('stereo')
            if movie.count('flv'):
                c['container'].append('FLV')
            else:
                c['container'].append('MP4')
            c['encoding'].append('H.264/AVC Video')
            c['rate'].append('44100 Hz')
            c['paster'] = 'true'

            return sj.dumps(c)
        except:
            return sj.dumps(['error'])
