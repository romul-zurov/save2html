#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, urllib, time
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui

VERSION = '20120222'
EXIT_TIMEOUT = 30000

class Downloader(QtCore.QObject):
	def __init__(self, url, beg_str, end_str, url_enc, parent = None):
		super(Downloader, self).__init__(parent)
		self.url = url
		self.url_enc = url_enc
		self.wv = QtWebKit.QWebView()
#		self.wv.settings().setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 8)
		self.wv.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, False)
		self.wv.page().networkAccessManager().finished.connect(self.save)
		
		self.tmp_timer = QtCore.QTimer(self)
		self.wv.loadFinished.connect(self.do_submit)
		
		self.count = 0
		self.beg_str = beg_str
		self.end_str = end_str
		self.beg_qstr = QtCore.QString(beg_str.decode('utf8'))
		self.end_qstr = QtCore.QString(end_str.decode('utf8'))
		self.timer = QtCore.QTimer(self)
		self.timer.start(EXIT_TIMEOUT)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.exit_timeout)
	
	
	
	def do_submit(self):
		self.tmp_timer.start(1500)
		self.connect(self.tmp_timer, QtCore.SIGNAL("timeout()"), self.press_submit)
		pass
	
	
	def press_submit(self):
		dom = self.wv.page().mainFrame().documentElement()
		button = dom.findFirst("input[type=submit]")
		button.evaluateJavaScript("this.click()")
		pass
	
	
	def say(self, s):
#		print '<<<%s>>>' % s
		print '<<<%s>>>' % s.encode('cp1251')
	
	
	def exit_timeout(self):
		self.say("Error : no data found or bad url")
		sys.exit()
	
	def save(self):
		def to_f(name, data):
			out = open(name, "w")
			out.write(data)
			out.flush()
			out.close()
			pass
		
		
		def ret_subQstr(data, str1, str2):
			i1 = data.indexOf(str1)
			if (i1 > -1):
				i1 += str1.size()
				i2 = data.indexOf(str2, i1)
				if (i2 > i1):
					return data.mid(i1, i2 - i1)
					pass
				else:
					return None
			else:
				return None
		
		
		def ret_time(data):
			rex = QtCore.QRegExp(u'Время \(с учетом пробок\):.*$')
			if (data.contains(rex)):
				i = data.indexOf(rex)
				data = data.mid(i)
				rex = QtCore.QRegExp(u'\n')
				i = data.indexOf(rex) #+ rex.pattern().length()
				data.truncate(i)
				return data
			else:
				return None
		
		def ret_coords(data):
			dom = self.wv.page().mainFrame().documentElement()
			inp = dom.findFirst('input[class=coords]')
			val = inp.attribute("value")
#			print val
			if val.isEmpty():
				return None
			else:
				return val
		
		
		def ret_substr(stroka, str1, str2):
			i1 = stroka.find(str1) 
			if (i1 > -1):
				i1 += len(str1)
				i2 = stroka.find(str2, i1)
				if (i2 > i1):
					print stroka[i1:i2]
					return stroka[i1:i2]
				else:
					return None
			else:
				return None
		
#		data = self.wv.page().mainFrame().toHtml(); # to_f('foo.html', data)
#		data = self.wv.page().mainFrame().toPlainText(); # res = ret_time(data)
#		res = ret_substr(str(data.toUtf8()).decode('utf8'), self.beg_str, self.end_str)		
		
		data = self.wv.page().mainFrame().toHtml()
		if (self.beg_str == 'DayGPSKoordinatPoAdresu'):
			res = ret_coords(data)
		else:
			res = ret_subQstr(data, self.beg_qstr, self.end_qstr)
		
		if (res != None):
			sout = str(res.toUtf8()).decode('utf8')
			if (sout.isspace()):
				pass
			else:
				self.say(sout)
				sys.exit()
		
#		print "Page %d saved." % self.count
		self.count += 1
		pass
	
	
	def load(self):
#		get_url = urllib.quote(self.url.decode('utf8').encode('cp1251'), ':/')
		get_url = self.url.decode('utf8').encode(self.url_enc)
		qt_url = QtCore.QUrl()
		qt_url.setEncodedUrl(QtCore.QByteArray(get_url))
		self.wv.load(qt_url)
		pass
	
	
	def show(self):
		self.wv.show()
		pass


if __name__ == '__main__':
	arg = sys.argv
	url_enc = 'cp1251'
	la = len(arg) 
	if (la > 3):
		map_url = arg[1]
		beg_str = arg[2]
		end_str = arg[3]
		if (la > 4):
			url_enc = arg[4]
		
		#----
#		print map_url, '\n', beg_str, '\n', end_str, '\n', url_enc; sys.exit()
		
	else: 
		print 'Using: \nxvfb-run -a -w 1 save2html.py url pattern_from pattern_to [encoding]'
		print 'version %s' % VERSION
		sys.exit()
	
	app = QtGui.QApplication(arg)
	
	## ---
#	map_url = r'http://ac-taxi.ru/order/?service=1&point_from[obj][]=Балтийская ул.&point_from[house][]=21&point_from[corp][]=1'
#	sys.exit()
	
	webpage = Downloader(map_url, beg_str, end_str, url_enc)
	
	webpage.load()
	
#	webpage.show()
	
	sys.exit(app.exec_())
	pass

