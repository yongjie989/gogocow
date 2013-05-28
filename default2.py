# -*- coding: utf-8 -*- 

import lxml.etree
import lxml.html
import cStringIO
import urllib
import urllib2
import httplib2
import cookielib
import os
import time
import datetime
import gluon.contrib.simplejson as sj
import gluon.tools
import gluon.utils


headers = {'User-Agent':request.env.http_user_agent}

def mail(to, subject, message):
    mail = gluon.tools.Mail()
    attachment = mail.Attachment(os.path.join(request.folder,'static/images/gogocow_beta_logo.jpg'))
    mail.settings.server = 'localhost'
    #mail.settings.server = 'smtp.gmail.com:587'
    mail.settings.sender = '"gogocow video downloader" <service@gogocow.com>'
    #mail.settings.login = 'service@gogocow.com:09140317'

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
        title = 'gogocow影音下?- 您的好友%s分享一?影片?您!' % yourname
    else:
        title = 'gogocow video downloader - Your Friends share a video for you!'
    if len(to.split(",")) >= 1:
        for x in range(len(to.split(","))):
            mail(to.split(",")[x],
            title,
            content)
    return 'OK'


def index():
    # the login fields name are ['username','passwd']
    japan_yahoo_bid_login_url = "https://login.yahoo.co.jp/config/login"
    #http = httplib2.Http(".cache")
    #resp, content = http.request(japan_yahoo_bid_login_url, headers = headers)
    
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozila/5.0')]
    urllib2.install_opener(opener)    
    f = opener.open(japan_yahoo_bid_login_url)
    #cj.save(os.path.join(request.folder,'yahoo.cookie'))
    cj.save('./yahoo.cookie')
    content = f.read()
    f.close()
        
    data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='euc-jp') )
    title = data.xpath("//h1[@class='yjM']/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
    title = ''.join(title)
    
    print title
    
    headers['Content-type'] = 'application/x-www-form-urlencoded'
    post_data = {}
    post_data["login"] = "myname"
    post_data["passwd"] = "12345"
    
    #hiddens = data.xpath("//form[@name='login_form']/input[@type='hidden']", namespaces={"regxp": "http://exslt.org/regular-expressions"})
    #for h in hiddens:
    #    print h.xpath("@name")[0] , h.xpath("@value")[0]
    #    post_data[h.xpath("@name")[0]] = h.xpath("@value")[0]
        
    https_post_url = data.xpath("//form[@name='login_form']/@action", namespaces={"regxp": "http://exslt.org/regular-expressions"})
    
    print https_post_url[0]
    
    print urllib.urlencode(post_data)
    
    #resp, content = http.request(https_post_url[0], "POST", headers = headers, body=urllib.urlencode(post_data))
    
    #set cookie of login success.
    #headers['Cookie'] = resp['set-cookie']
    #print resp
    
    request = urllib2.Request(https_post_url[0], urllib.urlencode(post_data))
    
    f = opener.open("http://user.auctions.yahoo.co.jp/jp/show/mystatus")
    content = f.read()
    f.close()
    
    #resp, content = http.request("http://user.auctions.yahoo.co.jp/jp/show/mystatus", headers = headers)
    data = lxml.etree.parse( cStringIO.StringIO(content) ,lxml.etree.HTMLParser(encoding='euc-jp') )
    print headers
    return content
    login_username = data.xpath("//div/center[3]/table//tr/td/small/b/text()", namespaces={"regxp": "http://exslt.org/regular-expressions"})
    print login_username
    
    return title
    
def test():
    from mechanize import Browser
    USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; tr-TR; rv:1.8.1.9) Gecko/20071102 Pardus/2007 Firefox/2.0.0.9"
    br = Browser()
    br.addheaders = [("User-agent", USER_AGENT)]
    
    url = "https://login.yahoo.co.jp/config/login?.src=&.done=http%3A//www.yahoo.co.jp/"
    br.open(url)
    br.select_form("login_form")
    br['login'] = "by8nana"
    br['passwd'] = "877877"
    response = br.submit()
    print response.read()
    #form_data = {'username' : 'by8nana', 'passwd' : '877877'}
    #jar = cookielib.CookieJar()
    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    #form_data = urllib.urlencode(form_data)
    #resp = opener.open(url, form_data)
    #resp = opener.open("http://user.auctions.yahoo.co.jp/jp/show/mystatus")

    #return resp.read()

def test_login_yahoo_account():
    url = "https://login.yahoo.co.jp/config/login?.src=&.done=http%3A//www.yahoo.co.jp/"
    form_data = {'login' : 'myname', 'passwd' : '123456'}
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    form_data = urllib.urlencode(form_data)
    resp = opener.open(url, form_data)
    resp = opener.open("http://user.auctions.yahoo.co.jp/jp/show/mystatus")
    return resp.read()
    
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
