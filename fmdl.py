# -*- coding:utf8 -*-
'''
 核心代码来自Qleelulu大叔
'''
import os, sys, urllib, urllib2, cookielib, re, json
start = 0

fail_retry = 2
fail_downloads = []
success_downloads = []

class fmdl():
    cj = cookielib.CookieJar()
    cj_temp=cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    url_login = 'http://douban.fm/j/login'
    url_fav_song = 'http://douban.fm/mine?type=liked&start='
    url_song_info = 'http://38bef685.dotcloud.com/song/'
    url_play_list = 'http://douban.fm/j/mine/playlist?type=n&h=&channel=0&from=mainsite&r=4941e23d79'
    id=""
    url_pic_request="http://douban.fm/j/new_captcha"
    pic_url ="http://douban.fm/misc/captcha?size=m&id="

    reg_sid = re.compile('sid="(\d+)"')
    
    _email_u='notice@magicshui.com'
    _email_p='12345a'
    def get_pic(self):
        id=self.opener.open(self.url_pic_request).read()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.cj_temp=self.cj
        self.id= id.replace('"',"")
        return id.replace('%22',"")
    def check_login(self,u,p,v):
        
        url_login = 'http://douban.fm/j/login'
        alias = u
        form_password = p
        captcha_solution = v.replace('"','')
        post_data = {"source":"radio",'alias': alias, 'form_password':form_password,'captcha_solution':captcha_solution,"captcha_id":self.id}
        print post_data
        lg = self.opener.open(self.url_login, urllib.urlencode(post_data)).read()

        if lg.find('user_info') < 0:
            print u'登录失败:'
            print lg
            return False,lg
        else:
            return True,'ok'
            
    def download(self,u,p,v,e):
        url_login = 'http://douban.fm/j/login'
        alias = u
        form_password = p
        captcha_solution = v.replace('"','')
        post_data = {"source":"radio",'alias': alias, 'form_password':form_password,'captcha_solution':captcha_solution,"captcha_id":self.id}
        print post_data
        lg = self.opener.open(self.url_login, urllib.urlencode(post_data)).read()

        if lg.find('user_info') < 0:
            print u'登录失败:'
            print lg
            return False,lg
        else:
            self.down_load_songs(0)
            self.send_notify_email(e)
            return True,'ok'
    def send_notify_email(self,email):
        import smtplib

        fromaddr = 'notice@magicshui.com'
        toaddrs  = email
        msg = 'test!'

        # Credentials (if needed)
        username = 'notice@magicshui.com'
        password = '12345a'

        
        return True
            
    def down_load_songs(self,_start, sids=None):
        global fail_downloads, fail_retry, start

        if not sids:
            print 'get sids'
            fav_page = self.opener.open(self.url_fav_song + str(_start)).read()
            sids = self.reg_sid.findall(fav_page)

        for sid in sids:
            print '---===---'
            print 'down load song sid =', sid

            try:
                self.down_load_song(sid)
            except Exception,e:
                fail_downloads.append(sid)
                print 'down load error:', e

                print '\r\n-- END --'
                print ''

        if _start is not None and len(sids) > 14:
            start += len(sids)
            return self.down_load_songs(start)
        elif fail_retry > 0 and len(fail_downloads) > 0:
            print '--== retry ==--'
            temp = fail_downloads
            fail_downloads = []
            fail_retry -= 1
            return self.down_load_songs(None, temp)
    def down_load_song(self,sid):
        global fail_downloads, fail_retry, success_downloads, start

        song = self.opener.open(self.url_song_info + str(sid)).read()
        try:
            song = json.loads(song)
        except:
            song = None
        if not song:
            print u'load song error, song id is:', song
            fail_downloads.append(sid)
            return

        if not song.has_key('sid') or not song.has_key('ssid'):
            fail_downloads.append(sid)
            print 'song has no "sid" or "ssid" : ', song
            return

        print 'down load : ', song['title']

        start_cookie = '%sg%sg0' % (song['sid'], song['ssid'])
        ck = ck = cookielib.Cookie(version=0, name='start', value=start_cookie, port=None, port_specified=False, domain='.douban.fm', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        self.cj.set_cookie(ck)
        pl = self.opener.open(self.url_play_list).read()
        try:
            pl = json.loads(pl)
        except:
            print 'load play list error:', pl
            fail_downloads.append(sid)
            return

        if pl['song'][0]['sid'] != str(sid):
            print 'load song info ERROR: NOT THE SAME SID'
            fail_downloads.append(sid)
            return

        url = pl['song'][0]['url']

        print '==>> wget: ==>> ', url
       
        cmd = 'wget -O "songs/%s.mp3" %s' % (song['title'], url)
        os.system(cmd.encode('utf8'))

        success_downloads.append(sid)