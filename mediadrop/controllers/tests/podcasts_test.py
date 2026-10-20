# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from mediadrop.controllers.podcasts import PodcastsController
from mediadrop.lib.test import ControllerTestCase
from mediadrop.model import DBSession, Podcast


class PodcastsControllerTest(ControllerTestCase):
    def test_lists_podcasts_in_the_order_chosen_by_admins(self):
        hello_world = Podcast.query.one()
        alpha = Podcast.example(title=u'Alpha Show')
        beta = Podcast.example(title=u'Beta Show')
        Podcast.reorder([beta.id, hello_world.id, alpha.id])
        DBSession.commit()

        request = self.init_fake_request(method='GET', request_uri='/podcasts')
        response = self.call_controller(PodcastsController, request)

        assert_equals(200, response.status_int)
        body = response.body
        assert_true(body.index('Beta Show') < body.index('Hello World') < body.index('Alpha Show'))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PodcastsControllerTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
