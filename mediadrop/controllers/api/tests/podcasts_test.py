# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import app_globals

from mediadrop.lib.test import *
from mediadrop.model import DBSession, Podcast
from ..podcasts import PodcastsController


__all__ = ['PodcastsAPITest']

class PodcastsAPITest(ControllerTestCase, RequestMixin):
    def tearDown(self):
        self.remove_globals()
        super(PodcastsAPITest, self).tearDown()

    def test_can_list_podcasts_in_the_order_chosen_by_admins(self):
        app_globals.settings['api_secret_key_required'] = 'false'
        hello_world = Podcast.query.one()
        alpha = Podcast.example(title=u'Alpha Show')
        beta = Podcast.example(title=u'Beta Show')
        Podcast.reorder([beta.id, hello_world.id, alpha.id])
        DBSession.commit()

        request = self.init_fake_request(method='GET',
            request_uri='/api/podcasts?order=sort_order%20asc')
        response = self.call_controller(PodcastsController, request)

        assert_equals(200, response.status_int)
        slugs = [podcast['slug'] for podcast in response.json['podcasts']]
        assert_equals([u'beta-show', u'hello-world', u'alpha-show'], slugs)


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PodcastsAPITest))
    return suite
