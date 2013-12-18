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

from xbmcswift2 import Plugin
from resources.lib.postnauka_scraper import Scraper, NetworkError

plugin = Plugin()
scraper = Scraper()
YOUTUBE_CMD_PATTERN = 'plugin://plugin.video.youtube?action=play_video&videoid=%s'

STRINGS = {
	'next_page': 30000,
	'prev_page': 30001,
	'courses'  : 30002,
	'videos'   : 30003
}


@plugin.route('/')
def entry_point():
	items = []
	items.append( { 'label' : _('courses'), 'path' : plugin.url_for( endpoint = 'show_courses' ) } )
	items.append( { 'label' : _('videos'), 'path' : plugin.url_for( endpoint = 'show_videos', page = '1' ) } )
	return plugin.finish(items)

@plugin.route('/courses')
def show_courses():
	courses = scraper.get_courses()
	items = []
	items.extend([{
		'label': course['title'],
		'thumbnail': course['thumb'],
		'is_playable': False,
		'path': plugin.url_for( endpoint = 'course_content', course_id = course['id'] )
	} for course in courses])
	return items

@plugin.route('/course/<course_id>')
def course_content(course_id):
	videos = scraper.get_course_content(course_id)
	items = []
	items.extend([{
		'label': video['title'],
		'is_playable': True,
		'path': plugin.url_for( endpoint = 'play_video', video_id = video['id'] )
	} for video in videos])
	return items
	
@plugin.route('/videos/page/<page>')
def show_videos(page = '1'):
	videos, prev_page, next_page = scraper.get_videos(page)
	items = []
	if prev_page != '-1':
		items.append({ 'label' : _('prev_page') % ( prev_page ), 'path' : plugin.url_for( endpoint = 'show_videos', page = prev_page, update = 'true' ) })
	items.extend([{
		'label': video['title'],
		'thumbnail': video['thumb'],
		'is_playable': True,
		'path': plugin.url_for( endpoint = 'play_video', video_id = video['id'] )
	} for video in videos])
	
	if next_page != '-1':
		items.append({ 'label' : _('next_page') % ( next_page ), 'path' : plugin.url_for( endpoint = 'show_videos', page = next_page, update = 'true' ) })
	return items

@plugin.route('/video/<video_id>')
def play_video(video_id):
	youtube_id = scraper.get_youtube_id(video_id)
	if youtube_id == '':
		return
	plugin.set_resolved_url(YOUTUBE_CMD_PATTERN % youtube_id)

def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id


if __name__ == '__main__':
    try:
        plugin.run()
    except NetworkError:
        plugin.notify(msg='Network error')
