# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re
from datetime import datetime

from pythonic_testcase import *

from mediadrop.controllers.admin.podcasts import PodcastsController
from mediadrop.lib.test import ControllerTestCase
from mediadrop.model import DBSession, Media, Podcast, User


class PodcastsControllerTest(ControllerTestCase):
    def setUp(self):
        super(PodcastsControllerTest, self).setUp()
        self.admin = DBSession.query(User).filter(User.user_name == u'admin').one()
        # start without the podcast created by the default data
        for podcast in Podcast.query:
            DBSession.delete(podcast)
        DBSession.commit()

    def test_full_list_shows_podcasts_in_display_order(self):
        alpha, beta = self.create_podcasts(u'Alpha Show', u'Beta Show')
        Podcast.reorder([beta.id, alpha.id])
        DBSession.commit()

        response = self.call_podcasts_controller('/admin/podcasts')

        assert_equals(200, response.status_int)
        assert_true(response.body.index('Beta Show') < response.body.index('Alpha Show'))

    def test_compact_list_shows_podcasts_in_display_order(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')
        Podcast.reorder([c.id, a.id, b.id])
        DBSession.commit()

        response = self.call_podcasts_controller('/admin/podcasts/compact')

        assert_equals(200, response.status_int)
        assert_equals([c.id, a.id, b.id], self.listed_podcast_ids(response))

    def test_compact_list_shows_number_of_episodes_and_date_of_last_episode(self):
        podcast, empty_podcast = self.create_podcasts(u'A', u'B')
        Media.example(podcast=podcast, reviewed=True, encoded=True,
                      publishable=True, publish_on=datetime(2020, 2, 1))
        Media.example(podcast=podcast)
        DBSession.commit()

        response = self.call_podcasts_controller('/admin/podcasts/compact')

        grip, title, episodes, last_episode = self.podcast_cells(response, podcast.id)
        assert_equals('<a href="/admin/media?podcast=a">2</a>', episodes)
        assert_equals('Feb 1, 2020', last_episode)
        grip, title, episodes, last_episode = self.podcast_cells(response, empty_podcast.id)
        assert_equals('0', episodes)
        assert_equals('-', last_episode)

    def test_compact_list_has_buttons_to_reorder_podcasts_with_the_keyboard(self):
        podcast, = self.create_podcasts(u'A')

        response = self.call_podcasts_controller('/admin/podcasts/compact')

        handle, title, episodes, last_episode = self.podcast_cells(response, podcast.id)
        title_id = 'podcast-title-%d' % podcast.id
        assert_contains('<a id="%s"' % title_id, title)
        for css_class, label in (('uparrow', 'Up'), ('downarrow', 'Down')):
            button = '<button class="%s" type="button" aria-describedby="%s">%s</button>'
            assert_contains(button % (css_class, title_id, label), handle)

    def test_compact_list_announces_saving_to_screen_readers(self):
        response = self.call_podcasts_controller('/admin/podcasts/compact')

        status = '<div id="podcast-order-status" role="status" aria-live="polite" aria-atomic="true"></div>'
        assert_contains(status, response.body)

    def test_can_save_order(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')

        response = self.call_podcasts_controller('/admin/podcasts/save_order',
            post_vars=[('ids', c.id), ('ids', a.id), ('ids', b.id)])

        assert_equals({'success': True}, response.json)
        assert_equals([c, a, b], Podcast.query.all())

    def test_can_save_order_with_single_id(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')

        response = self.call_podcasts_controller('/admin/podcasts/save_order',
            post_vars=[('ids', c.id)])

        assert_equals({'success': True}, response.json)
        assert_equals([c, a, b], Podcast.query.all())

    def test_rejects_invalid_ids_when_saving_order(self):
        a, b = self.create_podcasts(u'A', u'B')

        response = self.call_podcasts_controller('/admin/podcasts/save_order',
            post_vars=[('ids', b.id), ('ids', 'invalid')])

        assert_equals({'success': False}, response.json)
        assert_equals([a, b], Podcast.query.all())

    def test_saving_order_requires_post_request(self):
        a, b = self.create_podcasts(u'A', u'B')

        response = self.call_podcasts_controller(
            '/admin/podcasts/save_order?ids=%d&ids=%d' % (b.id, a.id))

        assert_equals(405, response.status_int)
        assert_equals([a, b], Podcast.query.all())

    def test_saving_order_requires_login(self):
        a, b = self.create_podcasts(u'A', u'B')
        request = self.init_fake_request(method='POST',
            request_uri='/admin/podcasts/save_order',
            post_vars=[('ids', b.id), ('ids', a.id)])

        response = self.call_controller(PodcastsController, request)

        assert_equals(401, response.status_int)
        assert_equals([a, b], Podcast.query.all())

    # - helpers ---------------------------------------------------------------

    def create_podcasts(self, *titles):
        podcasts = [Podcast.example(title=title) for title in titles]
        DBSession.commit()
        return podcasts

    def call_podcasts_controller(self, request_uri, post_vars=None):
        method = post_vars and 'POST' or 'GET'
        request = self.init_fake_request(method=method,
            request_uri=request_uri, post_vars=post_vars)
        return self.call_controller(PodcastsController, request, user=self.admin)

    def listed_podcast_ids(self, response):
        return [int(id) for id in re.findall(r'<tr id="podcast-(\d+)"', response.body)]

    def podcast_cells(self, response, podcast_id):
        pattern = r'<tr id="podcast-%d"[^>]*>(.*?)</tr>' % podcast_id
        row = re.search(pattern, response.body, re.S).group(1)
        return [cell.strip() for cell in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PodcastsControllerTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
