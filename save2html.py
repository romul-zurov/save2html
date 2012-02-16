#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, urllib
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui

VERSION = '0.9.1'
EXIT_TIMEOUT = 30000

class Downloader(QtCore.QObject):
	def __init__(self, url, beg_str, end_str, url_enc, parent = None):
		super(Downloader, self).__init__(parent)
		self.url = url
		self.url_enc = url_enc
		self.wv = QtWebKit.QWebView()
		self.wv.settings().setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 8)
		self.wv.page().networkAccessManager().finished.connect(self.save)
		self.count = 0
		self.beg_str = beg_str
		self.end_str = end_str
		self.beg_qstr = QtCore.QString(beg_str.decode('utf8'))
		self.end_qstr = QtCore.QString(end_str.decode('utf8'))
		self.timer = QtCore.QTimer(self)
		self.timer.start(EXIT_TIMEOUT)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.exit_timeout)
	
	def say(self, s):
		print '<<<%s>>>' % s
	
	
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
		
		data = self.wv.page().mainFrame().toHtml()
		res = ret_subQstr(data, self.beg_qstr, self.end_qstr)
		
#		res = ret_substr(str(data.toUtf8()).decode('utf8'), self.beg_str, self.end_str)
		
		if (res != None):
			self.say(res.toUtf8())
#			print res
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
		sys.exit()
	
	app = QtGui.QApplication(arg)
	
	webpage = Downloader(map_url, beg_str, end_str, url_enc)
	
	webpage.load()
	
#	webpage.show()
	
	sys.exit(app.exec_())
	pass

