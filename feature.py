# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import httplib2
import cStringIO
import urllib2
import os
import time
import datetime
import gluon.contrib.simplejson as sj
import gluon.tools
import gluon.utils
import applications.downloader.modules.common as common

#print T.accepted_language
if not session.lang:
    T.force(T.accepted_language)
else:
    T.force(session.lang)

headers = {'User-Agent':request.env.http_user_agent}

def mail(to, subject, message):
    mail = gluon.tools.Mail()
    attachment = mail.Attachment(os.path.join(request.folder,'static/images/gogocow_beta_logo.jpg'))
    mail.settings.server = 'localhost'
    #mail.settings.server = 'smtp.gmail.com:587'
    mail.settings.sender = '"gogocow video downloader" <service@gogocow.com>'
    #mail.settings.login = 'service@gogocow.com:123456'

    mail.send(
        to=[to],
        subject=subject,
        message=message,
        attachments=attachment
    )
    
def sendmail():
    to = request.vars.users
    content = request.vars.content or ''
    yourname = request.vars.yourname or ''
    video_title = request.vars.video_title or ''
    url = 'http://www.gogocow.com/downloader/youtube/detail?url=' + urllib2.quote(request.vars.url) or ''

    content += '''
    Video title: %s
    Video URL: %s
    ---
    gogocow video downloader - http://www.gogocow.com/
    ''' % (video_title, url)
    if not session.lang:
        lang = T.accepted_language
    else:
        lang = session.lang
    
    if lang == 'zh-tw':
        title = 'gogocow影音下載 - 您的好友%s分享一個影片給您!' % yourname
    elif lang == 'zh-cn':
        title = 'gogocow影音下载- 您的好友%s分享一个影片给您!' % yourname
    else:
        title = 'gogocow video downloader - Your Friends share a video for you!'
    if len(to.split(",")) >= 1:
        for x in range(len(to.split(","))):
            mail(to.split(",")[x],
            title,
            content)
    return 'OK'

def lang():
    country = request.vars.country or 'en'
    session.lang = country
    return redirect('/')

def contact():
    response.view = './youtube/contact.html'
    return dict()
    
def advertising():
    response.view = './youtube/advertising.html'
    return dict()
    
def about():
    response.view = './youtube/about.html'
    return dict()

def view_keywords():
    rows = db(db.search_keywords.id).select(
        db.search_keywords.keyword,
        db.search_keywords.keyword.count(),
        groupby=db.search_keywords.keyword,
        orderby=~db.search_keywords.keyword.count()
        )
    return rows
    
def generate_keywords():
    rows = db(db.search_keywords.id).select(
        db.search_keywords.keyword,
        db.search_keywords.keyword.count(),
        groupby=db.search_keywords.keyword,
        orderby=~db.search_keywords.keyword.count()
        )
    
    for x in rows:
        db.keywords_publish.insert(
            keyword = x.search_keywords.keyword,
            ordering = 0,
            request_time = str(datetime.datetime.now())
        )

    return "OK!"
    
def generate_sitemap():
    urls = db(db.recently_download.id).select()
    f = open(os.path.join(request.folder,'static/sitemap.xml'), 'w')
    sitemap_header = '''<?xml version="1.0" encoding="UTF-8"?>
      <urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">    
    '''
    sitemap_body_new = ''
    for url in urls:
        sitemap_body = '''
    <url>
      <loc>%s%s</loc>
    </url>
        ''' % ('http://www.gogocow.com/downloader/youtube/detail?url=', urllib2.quote(url.movie_url))
        sitemap_body_new += sitemap_body
    sitemap_footer = '''
</urlset>
    '''
    f.write(sitemap_header + sitemap_body_new + sitemap_footer)
    f.close()
    
    f = open(os.path.join(request.folder,'static/urllist.txt'), 'w')
    for url in urls:
        f.writelines('http://www.gogocow.com/downloader/youtube/detail?url=' + urllib2.quote(url.movie_url) + '\n')
    f.close()
    return "OK!"

def index():
    common.get_verify(request,session,db)
    
    key = request.vars.key or ''
    c = {}
    #c['url'] = request.vars.url or 'http://www.youtube.com/watch?v=4DrX8AFIQao'
    c['url'] = request.vars.url or ''

    #recently downloaded videos
    r = {}
    r['title'] = []
    r['movies_url'] = []
    r['movies_image'] = []
    r['movies_embed'] = []

    if key == 'tudou':
        rows = db(db.download_log.query_string.like('http://www.tudou.com%')).select(groupby=db.download_log.query_string, limitby=(0,42), orderby=~db.download_log.id)
        for row in rows:
            try:
                http = httplib2.Http()
                resp, content = http.request(row.query_string, headers = headers)
                data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='gbk') )
                movies_image = data.xpath("//span[@class='s_pic']/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                movies_image = ''.join(movies_image)
                resp, images_content = http.request(movies_image, headers = headers)
                filename = movies_image.rsplit('/',2)[-2] + '.jpg'
                f = open(os.path.join(request.folder,'uploads/tudou/%s' % filename), 'wa')
                f.write(images_content)
                f.close()
                r['movies_image'].append(filename)
                
                title = data.xpath("//span[@id='vcate_title']/text()|//a[@class='sl_a']/@title", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                title = title[0]
                r['title'].append(title)

                movies_embed = data.xpath("//input[contains(@value,'embed src')]/@value", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                movies_embed = ''.join(movies_embed)
                r['movies_embed'].append(movies_embed)
                
                db.recently_download.insert(
                    movie_title = title,
                    movie_url = row.query_string,
                    movie_image = filename,
                    movie_embed = movies_embed
                )
            except:
                pass
        
    if key == 'youtube':
        rows = db(db.download_log.query_string.like('http://www.youtube.com%')).select(groupby=db.download_log.query_string, limitby=(0,42), orderby=~db.download_log.id)
        for row in rows:
            try:
                http = httplib2.Http()
                resp, content = http.request(row.query_string, headers = headers)
                data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
                scripts = data.xpath("//link[@rel='alternate' and contains(@href,'xml')]/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                scripts = ''.join(scripts)

                resp, content = http.request(scripts, headers = headers)
                
                data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
                title = data.xpath("//title/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                title = ''.join(title)
                r['title'].append(title)
                
                movies_image = data.xpath("//thumbnail_url/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                movies_image = ''.join(movies_image)

                movies_embed = data.xpath("//html/descendant::text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
                r['movies_embed'].append(movies_embed[2])

                resp, content = http.request(movies_image, headers = headers)
                filename = movies_image.rsplit('/',2)[-2] + '.jpg'
                f = open(os.path.join(request.folder,'uploads/youtube/%s' % filename), 'wa')
                f.write(content)
                f.close()
                r['movies_image'].append(filename)
                
                db.recently_download.insert(
                    movie_title = title,
                    movie_url = row.query_string,
                    movie_image = filename,
                    movie_embed = movies_embed[2]
                )
            except:
                pass
    else:
        rows = db(db.recently_download.movie_url.like('%youtube%') | db.recently_download.movie_url.like('%tudou%')).select(groupby=db.recently_download.movie_title, limitby=(0,42), orderby=~db.recently_download.id)
        for row in rows:
            r['title'].append(row.movie_title)
            r['movies_image'].append(row.movie_image)
            r['movies_url'].append(row.movie_url)
        
        hot_rows = db(db.keywords_publish.id).select(orderby=~db.keywords_publish.request_time, limitby=(0,8))
        c['hot_rows'] = hot_rows
    response.view = './youtube/index.beta.feature.html'
    return dict(c=c,r=r)
    
def test():
    return redirect('http://119.145.150.131/fcs11.56.com/flvdownload/18/26/i561x70@56.com_56flv_1280126557_934x.flv?m=s')
def getfile():
    #return redirect('http://119.145.150.131/fcs11.56.com/flvdownload/18/26/i561x70@56.com_56flv_1280126557_934x.flv?m=s')
    #filename = request.vars.filename or 'video'
    #response.headers['Content-Type'] = 'video/x-flv'
    #response.headers['Content-disposition'] = 'attachment; filename=%s' % filename
    #url = request.vars.url or ''

    #headers = {'User-Agent':request.env.http_user_agent}
    #http = httplib2.Http(timeout=10)
    #resp, content = http.request(url, headers = headers)
    #return content
    
    url = request.vars.url or ''
    if url:
        return url
        
def get_session():
    if not session.isGoogleAdsClick:
        session.isGoogleAdsClick = 'true'
        
def download(): 
    if not common.check_verify(request,session,db):
        return redirect('/')
    
    c = {}
    c['url'] = request.vars.url or ''
    c['page'] = request.vars.page or 1
    if not c['url']:
        return redirect("/")
    #log to db
    db.download_log.insert(
        userip = request.env.remote_addr,
        query_string = c['url'],
        query_time = str(datetime.datetime.now())
    )
    keywords = None
    c['search_title'] = []
    c['search_image'] = []
    c['search_url'] = []
    c['search_view'] = []
    if c['url'].find("http://")==-1:
        #keywords = c['url'].replace(" ","+")
        keywords = c['url']
        print keywords

        db.search_keywords.insert(
        keyword = keywords,
        userip = request.env.remote_addr,
        request_time = str(datetime.datetime.now())
        )    
            
        http = httplib2.Http()
        url = 'http://www.youtube.com/results?aq=f&search_query=%s' % urllib2.quote(keywords)
        if c['page']:
            url = 'http://www.youtube.com/results?page=%s&search_query=%s' % (c['page'], urllib2.quote(keywords))
        
        #print 'http://www.youtube.com/results?search_query=%s' % urllib2.quote(keywords)
        resp, content = http.request(url, "GET", headers = headers )
        data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
        scripts = data.xpath("//div[@class='video-long-title']/a", namespaces={"regxp": "http://exslt.org/regular-expressions"})
        for link in scripts:
            c['search_title'].append( ''.join(link.xpath("@title")) )
            c['search_url'].append( urllib2.quote('http://www.youtube.com' + ''.join(link.xpath("@href"))) )
            c['search_image'].append( ''.join(link.xpath("ancestor::div[@class='video-entry'][1]//img[not(contains(@src,'pixel-vfl73.gif'))]/@src|ancestor::div[@class='video-entry'][1]//img/@thumb")) )
            c['search_view'].append( ''.join(link.xpath("following::span[@class='video-view-count'][1]/text()")) )
        c['search_record'] = ''.join(data.xpath("//div[@id='search-num-results']/strong[1]/text()"))
        c['search_results'] = ''.join(data.xpath("//div[@id='search-num-results']/strong[2]/text()"))
        print c['search_results']

    else:
        #check support service.
        if c['url'].count('www.wretch.cc'):
            return redirect(URL(r=request,c='wretch',f='download', vars=dict(url=c['url'])))
        
        elif c['url'].count('tudou.com'):
            return redirect(URL(r=request,c='tudou',f='download', vars=dict(url=c['url'])))

        elif c['url'].count('youku.com'):
            return redirect(URL(r=request,c='youku',f='download', vars=dict(url=c['url'])))
            
        elif c['url'].count('facebook.com'):
            return redirect(URL(r=request,c='facebook',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('vlog.xuite.net'):
            return redirect(URL(r=request,c='xuite',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('mymedia.yam.com'):
            return redirect(URL(r=request,c='yam',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('share.youthwant.com.tw'):
            return redirect(URL(r=request,c='youthwant',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('video.sina.com.cn'):
            return redirect(URL(r=request,c='sina',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('video.udn.com'):
            return redirect(URL(r=request,c='udn',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('video.libertytimes.com.tw'):
            return redirect(URL(r=request,c='libertytimes',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('nownews.com'):
            return redirect(URL(r=request,c='nownews',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('openv.com'):
            return redirect(URL(r=request,c='openv',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.56.com'):
            return redirect(URL(r=request,c='56',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.5min.com'):
            return redirect(URL(r=request,c='5min',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('alcachondeo.com'):
            return redirect(URL(r=request,c='alcachondeo',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('blip.tv'):
            return redirect(URL(r=request,c='blip',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.bofunk.com'):
            return redirect(URL(r=request,c='bofunk',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.bollywoodhungama.com'):
            return redirect(URL(r=request,c='bollywoodhungama',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.break.com'):
            return redirect(URL(r=request,c='breakcom',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('www.buzzhumor.com'):
            return redirect(URL(r=request,c='buzzhumor',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('buzznet.com'):
            return redirect(URL(r=request,c='buzznet',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('vimeo.com'):
            return redirect(URL(r=request,c='vimeo',f='download', vars=dict(url=c['url'])))
        elif c['url'].count('youtube.com'):
            pass
        else:
            return sj.dumps(['error'])

        if c['url']:
            http = httplib2.Http()
            try:
                resp, content = http.request(c['url'], headers = headers)
            except :
                return redirect('/')
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            scripts = data.xpath("//script[contains(text(),'object')]", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            
            title = data.xpath("//span[@id='eow-title']/text()")
            c['title'] = ''.join(title)

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
            
    response.view = './youtube/index.beta.html'
    return sj.dumps(c)

def help():
    response.view = './youtube/help.beta.html'
    return dict()


def detail():
    try:
        c = {}
        c['url'] = request.vars.url or None
        c['theurl'] = urllib2.quote(c['url'])
        if type(c['url']) == list:
            c['url'] = c['url'][-1]
        c['keyword'] = request.vars.keyword or None

        rows = db(db.recently_download.movie_url == c['url']).select()
        if c['keyword'] or len(rows) == 0:
            r = {}
            r['title'] = []
            r['movies_url'] = []
            r['movies_image'] = []
            r['movies_embed'] = []
            http = httplib2.Http()
            resp, content = http.request(c['url'], headers = headers)

            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            scripts = data.xpath("//link[@rel='alternate' and contains(@href,'xml')]/@href", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            scripts = ''.join(scripts)
            resp, content = http.request(scripts, headers = headers)
            data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='utf-8') )
            title = data.xpath("//title/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            title = ''.join(title)
            r['title'].append(title)
            movies_image = data.xpath("//thumbnail_url/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            movies_image = ''.join(movies_image)

            movies_embed = data.xpath("//html/descendant::text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
            for i,x in enumerate(movies_embed):
                if x.count("object"):
                    movies_embed = movies_embed[i]
                    r['movies_embed'].append(movies_embed)

            resp, content = http.request(movies_image, headers = headers)
            filename = movies_image.rsplit('/',2)[-2] + '.jpg'
            f = open(os.path.join(request.folder,'uploads/youtube/%s' % filename), 'wa')
            f.write(content)
            f.close()
            r['movies_image'].append(filename)
            
            db.recently_download.insert(
                movie_title = title,
                movie_url = c['url'],
                movie_image = filename,
                movie_embed = movies_embed
            )
    except:
        return redirect('/')

    if not c['url']:
        return redirect('/')
        
    rows = db(db.recently_download.movie_url == c['url']).select(orderby=~db.recently_download.id)
    response.view = './youtube/detail.beta.html'
    return dict(c=c,rows=rows)

def upload():
    image = request.vars.image or ''
    url = request.vars.url or ''
    if image:
        if url.count('youtube'):
            path = os.path.join(request.folder,'uploads/youtube', image)
        elif url.count('tudou'):
            path = os.path.join(request.folder,'uploads/tudou', image)
    else:
        path = os.path.join(request.folder,'uploads', 'noimage.png')
    return response.stream(path)
