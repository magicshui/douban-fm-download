# -*- coding: utf8 -*-
from flask import Flask,render_template,request
import sqlalchemy
import json
from sqlalchemy import *
from sqlalchemy.exc import *
from fmdl import fmdl
app = Flask(__name__)
app.debug = True
'''
    The index page.
    user comes into the website and will see this page.
    they can input their u/p to the sys and 
    the sys will check it by post it to logindb
'''
_session = fmdl()
@app.route('/')
def index():
    v=_session.get_pic()
    return render_template("index.html",v=v)
'''
    check if the login success .
    if do ,return success page and let the user leave 
    email so we can notify them when download success
    else ,return failed page with log inforamtion
'''
@app.route('/login', methods=['POST', 'GET'])
def login_to_douban_fm():
    user_name = request.form['u']
    user_pwd= request.form['p']
    ver = request.form['v']
    _r,_l = _session.download(user_name,user_pwd,ver,"")
    if _r:
        return render_template('/')
    else:
        return render_template('fail.html',r=json.loads(_l))
'''
    let the user leave the email info into the sys
    and gen a process to download music 
    if done sent mail
'''
@app.route('/leaveemail')
def login_ok_and_leave_email():
    pass
'''
    if user login faild will see this page
'''
@app.route('/loginerror')
def login_failed():
    pass
@app.route('/emailme')
def email_to_myself():
    _session.send_notify_email('shui@shui.us')
    return "ok"
if __name__=="__main__":
    app.run()