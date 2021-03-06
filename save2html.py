#!/usr/bin/env python
# -*- coding: utf-8 -*-


#import urllib
import sys
import time
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui

VERSION = '20120604'
EXIT_TIMEOUT = 10000
DEBUG = False


def print_debug(s, dec = 'utf8', enc = 'utf8'):
	if DEBUG:
		print str(s).decode(dec).encode(enc)


class Downloader(QtCore.QObject):
	def __init__(self, url, beg_str, end_str, url_enc, parent = None):
		super(Downloader, self).__init__(parent)
		self.url = url
		self.url_enc = url_enc
		self.wv = QtWebKit.QWebView()
#		self.wv.settings().setFontSize(QtWebKit.QWebSettings.DefaultFontSize, 8)
		self.wv.page().networkAccessManager().finished.connect(self.save)
		
		self.tmp_timer = QtCore.QTimer(self)
		self.ADRES_TO_COORDS = False
		self.GET_WAY_TIME = False
		self.COORDS_TO_ADRES = False
		if (beg_str == 'DayGPSKoordinatPoAdresu'):
			self.ADRES_TO_COORDS = True
			self.wv.loadFinished.connect(self.do_submit)
		elif (beg_str == 'DayVremyaPuti'):
			self.GET_WAY_TIME = True
		elif (beg_str == 'DayAdresPoKoordinate'):
			self.COORDS_TO_ADRES = True
			self.wv.loadFinished.connect(self.do_submit)
		else:
			pass
		self.count = 0
		self.beg_str = beg_str
		self.end_str = end_str
		self.beg_qstr = QtCore.QString(beg_str.decode('utf8'))
		self.end_qstr = QtCore.QString(end_str.decode('utf8'))
		self.timer = QtCore.QTimer(self)
		self.timer.start(EXIT_TIMEOUT)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.exit_timeout)
		self.save_timer = QtCore.QTimer(self)
		self.connect(self.save_timer, QtCore.SIGNAL("timeout()"), self.resave)
	
	
	def resave(self):
		print_debug('!resave %d time run.' % self.count)
		self.save()
	
	def do_submit(self):
		if (self.ADRES_TO_COORDS) or (self.COORDS_TO_ADRES) : 
			self.tmp_timer.start(1000)
			self.connect(self.tmp_timer, QtCore.SIGNAL("timeout()"), self.press_submit)
		else:
			return None
	
	
	def press_submit(self):
		dom = self.wv.page().mainFrame().documentElement()
		button = dom.findFirst("input[name=orderRecalc]")
		button.evaluateJavaScript("this.click()")
		pass
	
	
	def say(self, s):
		if DEBUG:
			print '<<<%s>>>' % s.encode('utf8')
		else:
			print '<<<%s>>>' % s.encode('cp1251')
	
	
	def exit_timeout(self):
		self.save()
		time.sleep(2)
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
			print_debug(data)
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
		
		def ret_time_DOM(data):
			dom = self.wv.page().mainFrame().documentElement()
			print_debug(dom.toInnerXml().toUtf8())
			inp = dom.findFirst('td[id=recalcOutput]')
			val = inp.toInnerXml()
			print_debug('val=[[%s]]' % val.toUtf8())
			if val.isEmpty():
				return None
			else:
				return val
		
		def ret_coords(data):
			dom = self.wv.page().mainFrame().documentElement()
			inp = dom.findFirst('div[id=gps_coords]')
			val = inp.toInnerXml()
			if val.isEmpty():
				return None
			else:
				return val
		
		def ret_adres(data):
			dom = self.wv.page().mainFrame().documentElement()
			inp = dom.findFirst('div[id=gps_addr]')
			val = inp.toInnerXml()
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
		
		def start_save_timer():
			self.save_timer.start(EXIT_TIMEOUT // 5)
		
		if self.ADRES_TO_COORDS:
			res = ret_coords(data)
		elif self.GET_WAY_TIME:
#			data = self.wv.page().mainFrame().toPlainText()
			res = ret_time_DOM(data)
		elif self.COORDS_TO_ADRES:
			res = ret_adres(data)
		else:
			res = ret_subQstr(data, self.beg_qstr, self.end_qstr)
		
		if (res != None):
			sout = str(res.toUtf8()).decode('utf8')
			if (sout.isspace()):
				start_save_timer()
			else:
				self.say(sout)
				sys.exit()
		else:
			start_save_timer()
		
		if DEBUG and (not self.GET_WAY_TIME) :
			print_debug(data)
		print_debug(self.beg_qstr + self.end_qstr + "Load #%d saved. res =[[ %s ]]" % (self.count, res))
		self.count += 1
		pass
	
	
	def load(self):
		get_url = self.url.decode('utf8').encode(self.url_enc)
		if DEBUG:
#			get_url = urllib.quote_plus(self.url.decode('utf8').encode(self.url_enc), r'\:/"<>=[]&?')
			print_debug(get_url, self.url_enc)
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
			if (arg[4] == 'DEBUG'):
				DEBUG = True
				EXIT_TIMEOUT = 30000
			else:
				url_enc = arg[4]
#		if 'WAIT10' in arg :
#			EXIT_TIMEOUT = 10000
		#----
#		print map_url, '\n', beg_str, '\n', end_str, '\n', url_enc; sys.exit()
	else: 
		print 'Using: \nxvfb-run -a -w 1 save2html.py url pattern_from pattern_to [encoding]'
		print 'version %s' % VERSION
		sys.exit()
	
	
	print_debug('DEBUG mode running!')
	
	app = QtGui.QApplication(arg)
	
	## ---
#	map_url = r'http://ac-taxi.ru/order/?service=1&point_from[obj][]=Балтийская ул.&point_from[house][]=21&point_from[corp][]=1'
#	map_url = r'http://ac-taxi.ru/order/?i_generate_address=1&service=0&point_from[obj][]=&point_from[house][]=&point_from[corp][]=&point_from[coords][]=30.356885910342,59.9133987426758&point_to[obj][]=&point_to[house][]=&point_to[corp][]=&point_to[coords][]=30.375401,59.90293&'
#	map_url = r'http://test.robocab.ru/order/?i_generate_address=1&service=0&point_from[obj][]=&point_from[house][]=&point_from[corp][]=&point_from[coords][]=30.353979,59.912411&point_to[obj][]=&point_to[house][]=&point_to[corp][]=&point_to[coords][]=30.375401,59.902930&'
#	map_url = r'http://test.robocab.ru/order/?i_generate_address=1&service=1&point_from[obj][]=&point_from[house][]=&point_from[corp][]=&point_from[coords][]=30.339092,59.858280&point_to[obj][]=&point_to[house][]=&point_to[corp][]=&point_to[coords][]=30.484661,59.852063&note=&orderRecalc=Рассчитать'
#	beg_str = '___DayVremyaPuti'
#	sys.exit()
	
	webpage = Downloader(map_url, beg_str, end_str, url_enc)
	webpage.load()
	
	if DEBUG:
		webpage.show()
	
	sys.exit(app.exec_())
	pass

