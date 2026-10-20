# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime, timedelta

from pythonic_testcase import *

from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.model import Author, DBSession, Media, Podcast


class PodcastExampleTest(DBTestCase):
    def test_can_create_example_podcast(self):
        podcast = Podcast.example()

        assert_not_none(podcast.id)
        assert_equals(u'Foo Podcast', podcast.title)
        assert_equals(u'foo-podcast', podcast.slug)
        assert_equals(Author(u'Joe', u'joe@site.example'), podcast.author)

    def test_can_override_example_data(self):
        podcast = Podcast.example(title=u'Bar Podcast')

        assert_equals(u'Bar Podcast', podcast.title)
        assert_equals(u'bar-podcast', podcast.slug)


class PodcastOrderTest(DBTestCase):
    def setUp(self):
        super(PodcastOrderTest, self).setUp()
        # start without the podcast created by the default data
        for podcast in Podcast.query:
            DBSession.delete(podcast)
        DBSession.flush()

    def test_lists_new_podcasts_after_existing_ones(self):
        zebra = Podcast.example(title=u'Zebra')
        aardvark = Podcast.example(title=u'Aardvark')

        assert_equals([1, 2], [zebra.sort_order, aardvark.sort_order])
        assert_equals([zebra, aardvark], Podcast.query.all())

    def test_lists_podcasts_by_sort_order(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')
        a.sort_order, b.sort_order, c.sort_order = 2, 3, 1
        DBSession.flush()

        assert_equals([c, a, b], Podcast.query.all())

    def test_lists_podcasts_with_the_same_sort_order_alphabetically(self):
        b, a, c = self.create_podcasts(u'B', u'A', u'C')
        a.sort_order = b.sort_order = c.sort_order = 0
        DBSession.flush()

        assert_equals([a, b, c], Podcast.query.all())

    def test_can_reorder_podcasts(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')

        Podcast.reorder([c.id, a.id, b.id])
        DBSession.commit()

        assert_equals([c, a, b], Podcast.query.all())
        assert_equals([1, 2, 3], [c.sort_order, a.sort_order, b.sort_order])

    def test_reorder_lists_unmentioned_podcasts_last_in_their_current_order(self):
        a, b, c, d = self.create_podcasts(u'A', u'B', u'C', u'D')

        Podcast.reorder([c.id, a.id])
        DBSession.commit()

        assert_equals([c, a, b, d], Podcast.query.all())

    def test_reorder_ignores_unknown_and_duplicate_ids(self):
        a, b, c = self.create_podcasts(u'A', u'B', u'C')

        Podcast.reorder([b.id, c.id + 100, b.id, a.id])
        DBSession.commit()

        assert_equals([b, a, c], Podcast.query.all())

    def test_reorder_does_not_change_the_modification_date(self):
        a, b = self.create_podcasts(u'A', u'B')
        last_modified = datetime(2020, 1, 1, 12, 0)
        a.modified_on = b.modified_on = last_modified
        DBSession.commit()

        Podcast.reorder([b.id, a.id])
        DBSession.commit()

        assert_equals([b, a], Podcast.query.all())
        assert_equals(last_modified, a.modified_on)
        assert_equals(last_modified, b.modified_on)

    def create_podcasts(self, *titles):
        return [Podcast.example(title=title) for title in titles]


class PodcastEpisodeStatsTest(DBTestCase):
    def test_knows_publish_date_of_newest_published_episode(self):
        podcast = Podcast.example()
        now = datetime.now()
        self.create_episode(podcast, publish_on=datetime(2020, 1, 1))
        self.create_episode(podcast, publish_on=datetime(2020, 2, 1))
        self.create_episode(podcast, publish_on=datetime(2020, 3, 1), publishable=False)
        self.create_episode(podcast, publish_on=now + timedelta(days=30))
        self.create_episode(podcast, publish_on=datetime(2020, 4, 1),
                            publish_until=datetime(2020, 5, 1))
        DBSession.commit()

        assert_equals(datetime(2020, 2, 1), podcast.last_episode_published_on)
        assert_equals(2, podcast.media_count_published)
        assert_equals(5, podcast.media_count)

    def test_publish_date_of_newest_episode_is_none_without_published_episodes(self):
        podcast = Podcast.example()
        self.create_episode(podcast, publish_on=datetime(2020, 1, 1), publishable=False)
        DBSession.commit()

        assert_none(podcast.last_episode_published_on)
        assert_equals(0, podcast.media_count_published)

    def create_episode(self, podcast, **kwargs):
        values = dict(podcast=podcast, reviewed=True, encoded=True,
                      publishable=True)
        values.update(kwargs)
        return Media.example(**values)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PodcastExampleTest))
    suite.addTest(unittest.makeSuite(PodcastOrderTest))
    suite.addTest(unittest.makeSuite(PodcastEpisodeStatsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
