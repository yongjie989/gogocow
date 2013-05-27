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
    try:
        c = {}
        c['url'] = request.vars.url or ''
        if c['url']:
            headers = {'User-Agent':request.env.http_user_agent}
            http = httplib2.Http()
            resp, content = http.request(c['url'], headers = headers)
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            title = data.xpath("//h1[@id='itemtitle']/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            if title:
                title = title[0]
            video_src = data.xpath("//link[@rel='video_src']/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            if video_src:
                c['title'] = title
                c['movies'] = []
                c['screen'] = []
                c['sound'] = []
                c['container'] = []
                c['encoding'] = []
                c['rate'] = []

                movie = video_src[0]
                if movie.count('http://vimeo.com/'):
                    movie_id = movie.split('?')[1].split('&amp;')[0].split('=')[1].split('&')[0]
                    resp, content = http.request('http://vimeo.com/moogaloop/load/clip:%s' % movie_id, headers = headers)
                    signature = re.findall('<request_signature>(.*)</request_signature>', content)
                    expires = re.findall('<request_signature_expires>(.*)</request_signature_expires>',content)
                    movie = 'http://vimeo.com/moogaloop/play/clip:%s/%s/%s/?q=hd&type=local&embed_location=' % (movie_id, signature[0], expires[0])

                    c['movies'].append(movie)
                    c['screen'].append('640x480')
                    c['sound'].append('stereo')
                    c['container'].append('MP4')
                    c['encoding'].append('H.264/AVC Video')
                    c['rate'].append('44100 Hz')
                    c['paster'] = 'true'
                    return sj.dumps(c)

                c['movies'].append(movie)
                c['screen'].append('470x384')
                c['sound'].append('stereo')
                c['container'].append('FLV')
                c['encoding'].append('H.264/AVC Video')
                c['rate'].append('22050 Hz')
                c['paster'] = 'true'
                return sj.dumps(c)
            else:
                video_src = data.xpath("//param[@name='src']/@value", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                if video_src:
                    video_src = video_src[0].rsplit('/',1)[-1].split('?')[0]
                    c['url'] = 'http://www.youtube.com/watch?v=%s' % video_src
           
                    http = httplib2.Http()
                    resp, content = http.request(c['url'], headers = headers)
                    data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
                    scripts = data.xpath("//script[contains(text(),'object')]", namespaces={"regxp": "http://exslt.org/regular-expressions"})

                    output=''
                    for x in scripts:
                        output += lxml.etree.tostring(x)
                    
                    output = urllib2.unquote(output)
                    movie_url = output[output.find('fmt_url_map=')+12:output.find('&amp;csi_page_type')]

                    movie_urls = movie_url.split('|')
                    #use for urlencode
                    #movie_urls = movie_url.split('%7C')
                    c['movies'] = []
                    for i in range(1, len(movie_urls)):
                        #use for urlencode
                        #movie_urls[i] = movie_urls[i].replace(movie_urls[i][movie_urls[i].find(','):],'')
                        c['movies'].append(movie_urls[i].rsplit(',',1)[0])

                    format_text = output[output.find('fmt_list=')+9:output.find('&', output.find('fmt_list='))]
                    formats = format_text.split(',')
                    
                    c['screen'] = []
                    c['sound'] = []
                    c['container'] = []
                    c['encoding'] = []
                    c['rate'] = []

                    screen = ''
                    sound = ''
                    container = ''
                    encoding = ''
                    rate = ''
                    for x in formats:
                        xx = x.split('/')
                        #xx = x.split('%2F')
                        f = xx[0]
                        if f == '5':
                            fmt = '240p'
                            screen = '400x226'
                            sound = 'stereo'
                            container = 'FLV'
                            encoding = 'H.263'
                            rate = '22050 Hz'

                        if f == '34':
                            fmt = '360p'
                            screen = '640x360'
                            sound = 'stereo'
                            container = 'FLV'
                            encoding = 'MPEG-4 AVC(H.264)'
                            rate = '44100 Hz'

                        if f == '35':
                            fmt = '480p'
                            screen = '851x480'
                            sound = 'stereo'
                            container = 'FLV'
                            encoding = 'MPEG-4 AVC(H.264)'
                            rate = '44100 Hz'

                        if f == '22':
                            fmt = '720p'
                            screen = '1280x720'
                            sound = 'stereo'
                            container = 'MP4'
                            encoding = 'MPEG-4 AVC(H.264)'
                            rate = '44100 Hz'

                        if f == '37':
                            fmt = '1080p'
                            screen = '1920x1080'
                            sound = 'stereo'
                            container = 'MP4'
                            encoding = 'MPEG-4 AVC(H.264)'
                            rate = '44100 Hz'

                        if f == '18':
                            fmt = 'Medium'
                            screen = '480x360'
                            sound = 'stereo'
                            container = 'MP4'
                            encoding = 'MPEG-4 AVC(H.264)'
                            rate = '44100 Hz'

                        if f == '43':
                            fmt = 'WebM 480p'
                            screen = '854x480'
                            sound = 'stereo'
                            container = 'WebM'
                            encoding = 'VP8'
                            rate = '44100 Hz'

                        if f == '45':
                            fmt = 'WebM 720p'
                            screen = '1280x720'
                            sound = 'stereo'
                            container = 'WebM'
                            encoding = 'VP8'
                            rate = '44100 Hz'

                        if f == '17':
                            fmt = 'Mobile'
                            screen = '176x144'
                            sound = 'stereo'
                            container = '3GP'
                            encoding = 'MPEG-4 Visual'
                            rate = '44100 Hz'

                        if f == '0, 5':
                            fmt = 'Standard, Old formats (pre Feb 2009)'
                            screen = '320x240'
                            sound = 'mono'
                            container = 'FLV'
                            encoding = 'H.263'
                            rate = '22050 Hz'

                        if f == '6':
                            fmt = 'High, Old formats (pre Feb 2009)'
                            screen = '480x360'
                            sound = 'mono'
                            container = 'FLV'
                            encoding = 'H.263'
                            rate = '44100 Hz'

                        if f == '13':
                            fmt = 'Mobile, Old formats (pre Feb 2009)'
                            screen = '176x144'
                            sound = 'mono'
                            container = '3GP'
                            encoding = 'H.263'
                            rate = '8000 Hz'
                            
                        c['screen'].append(screen)
                        c['sound'].append(sound)
                        c['container'].append(container)
                        c['encoding'].append(encoding)
                        c['rate'].append(rate)
                        c['paster'] = 'true'

        if not c['movie']:
            return sj.dumps(['error'])
            
        return sj.dumps(c)
    except:
        return sj.dumps(['error'])
