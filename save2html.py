#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, re
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui


class Downloader(QtCore.QObject):
	def __init__(self, url, parent = None):
		super(Downloader, self).__init__(parent)
		self.url = url
		self.wv = QtWebKit.QWebView()
		self.wv.page().networkAccessManager().finished.connect(self.save)
		self.count = 0;
	
	
	def save(self):
		def to_f(name, data):
			out = open(name, "w")
			out.write(data)
			out.flush()
			out.close()
			pass
		
		def ret_time(data):
			rex = QtCore.QRegExp(u'Среднее время в пути:.*$')
			if (data.contains(rex)):
				i = data.indexOf(rex)
				data = data.mid(i)
				rex = QtCore.QRegExp(u'\n')
				i = data.indexOf(rex) #+ rex.pattern().length()
				data.truncate(i)
				return data
			else:
				return None
		
#		data = self.wv.page().mainFrame().toHtml(); to_f('foo.html', data)
		data = self.wv.page().mainFrame().toPlainText()
		res = ret_time(data)
		if (res != None):
			print res.toUtf8()
			sys.exit()
		
#		print "Page %d saved." % self.count
		self.count += 1
		pass
	
	
	def load(self):
		self.wv.load(QtCore.QUrl(self.url))
		pass
	
	
	def show(self):
		self.wv.show()
		pass


if __name__ == '__main__':
	arg = sys.argv
	if (len(arg) > 1):
		map_url = arg[1]
	else: 
		print 'Error: No URL'
		sys.exit()
	
	app = QtGui.QApplication(arg)
	
	webpage = Downloader(map_url)
	
	webpage.load()
	
#	webpage.show()
	
	sys.exit(app.exec_())
	pass

