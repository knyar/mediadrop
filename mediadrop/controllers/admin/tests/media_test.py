# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re
from xml.sax.saxutils import unescape

from pythonic_testcase import *

from mediadrop.lib.test import ControllerTestCase
from mediadrop.model import DBSession, Podcast, User


class MediaControllerTest(ControllerTestCase):
    def test_lists_podcasts_in_display_order_when_editing_media(self):
        hello_world = Podcast.query.one()
        alpha = Podcast.example(title=u'Alpha Show')
        beta = Podcast.example(title=u'Beta Show')
        Podcast.reorder([beta.id, hello_world.id, alpha.id])
        DBSession.commit()
        admin = DBSession.query(User).filter(User.user_name == u'admin').one()

        request = self.init_fake_request(method='GET', request_uri='/admin/media/new/edit')
        # the module uses url_for() on import, which requires a request
        from mediadrop.controllers.admin.media import MediaController
        response = self.call_controller(MediaController, request, user=admin)

        assert_equals(200, response.status_int)
        # the test setup renders ToscaWidgets forms as escaped text
        body = unescape(response.body, {'&quot;': '"'})
        podcast_select = re.search(r'<select name="podcast"[^>]*>(.*?)</select>',
                                   body, re.S).group(1)
        options = re.findall(r'<option value="([^"]*)"', podcast_select)
        assert_equals(['', str(beta.id), str(hello_world.id), str(alpha.id)], options)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaControllerTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
