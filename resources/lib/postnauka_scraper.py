#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013 Dmytro Prylipko (kometa.triatlon@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from urllib2 import urlopen, HTTPError, URLError, unquote
import re

from BeautifulSoup import BeautifulSoup


class NetworkError(Exception):
    pass


class Scraper():
	
	VIDEOS_URL = 'http://postnauka.ru/video/page/%s'
	COURSES_URL = 'http://postnauka.ru/courses'
	VIDEO_URL_PATTERN = 'http://postnauka.ru/video/%s'
	COURSE_URL_PATTERN = 'http://postnauka.ru/courses/%s'
	VIDEO_ID_PATTERN = 'http\:\/\/postnauka\.ru\/video\/(.+)'
	COURSE_ID_PATTERN = 'http\:\/\/postnauka\.ru\/courses\/(.+)'
	PAGE_NUM_PATTERN = 'http\:\/\/postnauka\.ru\/video\/page\/(.+)'
	YOUTUBE_ID_PATTERN = 'src\=\"http\:\/\/www\.youtube.com\/embed\/(.+?)\?'
	
	def get_courses(self):
		items = []
		tree = self._build_tree(self.COURSES_URL)
		div_pattern = re.compile('thumb')
		for div in tree.findAll('div', {'class': div_pattern}):
			a = div.a
			img = a.img
			id_match = re.compile(self.COURSE_ID_PATTERN).findall(a['href'])
			items.append({'title': a['title'], 'thumb': img['src'], 'id': id_match[0]})
		return items
		
	def get_course_content(self, course_id):
		items = []
		tree = self._build_tree(self.COURSE_URL_PATTERN % course_id)
		pattern = re.compile('c\-name')
		for h in tree.findAll('h2', { 'class' : pattern } ):
			a = h.a
			id_match = re.compile(self.VIDEO_ID_PATTERN).findall(a['href'])
			if id_match is not None:
				if len(id_match) > 0:
					items.append({'title': a['title'], 'id': id_match[0]})
		return items
		
	def get_videos(self, page = '1'):
		items = []
		tree = self._build_tree(self.VIDEOS_URL % page)
		div_pattern = re.compile('thumb')
		for div in tree.findAll('div', {'class': div_pattern}):
			a = div.a
			img = a.img
			id_match = re.compile(self.VIDEO_ID_PATTERN).findall(a['href'])
			items.append({'title': a['title'], 'thumb': img['src'], 'id': id_match[0]})
		
		next_page = '-1'
		prev_page = '-1'
		a_next = tree.find('a', {'class': 'nextpostslink'})
		if a_next is not None:
			next_match = re.compile(self.PAGE_NUM_PATTERN).findall(a_next['href'])
			next_page = next_match[0]
		
		a_prev = tree.find('a', {'class': 'previouspostslink'})
		if a_prev is not None:
			prev_match = re.compile(self.PAGE_NUM_PATTERN).findall(a_prev['href'])
			if len(prev_match) == 0:
				prev_page = '1'
			else:
				prev_page = prev_match[0]

		return items, prev_page, next_page
	
	
	def get_youtube_id(self, video_id):
		html = self._read_url( self.VIDEO_URL_PATTERN % video_id )
		match = re.compile(self.YOUTUBE_ID_PATTERN).findall(html)
		if match:
			if len(match) > 0:
				return match[0]
		return ''
		
	def _read_url(self, url):
		self.log('opening url: %s' % url)
		try:
			html = urlopen(url).read()
		except HTTPError, error:
			self.log('HTTPError: %s' % error)
			raise NetworkError('HTTPError: %s' % error)
		except URLError, error:
			self.log('URLError: %s' % error)
			raise NetworkError('URLError: %s' % error)
		self.log('got %d bytes' % len(html))
		return html
		
	def _build_tree(self, url):
		html = self._read_url(url)
		tree = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
		return tree
	
	@staticmethod
	def log(text):
		print 'Scraper: %s' % repr(text)
