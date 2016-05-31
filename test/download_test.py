import unittest

import tvshows
import rss_download as ut 	# Unit under test

class FilterDataTest(unittest.TestCase):

	def setUp(self):
		self.entries = [
			{'title': 'Modern Family S07E21 Crazy Train 480p WEB-DL DD5.1 H.264-Oosh', 'link': ''},
			{'title': 'Modern Family S07E21 Crazy Train 1080p WEB-DL DD5.1 H.264-Oosh', 'link': ''},
			{'title': 'Modern Family S07E21 Crazy Train 720p WEB-DL DD5.1 H.264-Oosh', 'link': ''},
			{'title': 'Supernatural S11E21 All in the Family 480p WEB-DL DD5.1 H.264-Oosh', 'link': ''},
			{'title': 'Supernatural S11E21 All in the Family 720p WEB-DL DD5.1 H.264-Oosh', 'link': ''},
			{'title': 'The Vampire Diaries S07E22 HDTV x264-LOL', 'link': ''},
			{'title': 'Assassins Creed Collection', 'link': ''},
			{'title': 'Catfish The TV Show S05E12 720p HDTV x264-W4F', 'link': ''},
			{'title': 'Catfish The TV Show S05E12 PROPER HDTV x264-W4F', 'link': ''},
			{'title': 'Deadliest Catch S12E06 100 Percent Injury Rate HDTV x264-W4F', 'link': ''},
			{'title': 'Bella and the Bulldogs S02E17 720p HDTV x264-W4F', 'link': ''},
			{'title': 'Clarence US S02E19 Mystery Girl 720p HDTV x264-W4F', 'link': ''}
		];

	def test_filter_no_quality_found(self):
		filters = [tvshows.make_filter('Supernatural')];
		matches = ut.filter_data(self.entries, filters);
		expect = [{'name': 'Supernatural', 'season': 11, 'episode': 21, 'link': ''}];
		self.assertEqual(matches, expect);

	def test_filter_no_quality_not_found(self):
		filters = [tvshows.make_filter('sex and the city')];
		matches = ut.filter_data(self.entries, filters);
		self.assertEqual(matches, []);

	def test_filter_quality_found(self):
		filters = [tvshows.make_filter('Supernatural', quality='720p')];
		matches = ut.filter_data(self.entries, filters);
		expect = [{'name': 'Supernatural', 'season': 11, 'episode': 21, 'link': ''}];
		self.assertEqual(matches, expect);

	def test_filter_quality_not_found(self):
		filters = [tvshows.make_filter('Supernatural', quality='1080p')];
		matches = ut.filter_data(self.entries, filters);
		self.assertEqual(matches, []);

	def test_filter_entries_none(self):
		filters = [tvshows.make_filter('Supernatural', quality='720p')];
		result = ut.filter_data(None, filters);
		self.assertEqual(result, []);

	def test_filter_filters_none(self):
		result = ut.filter_data(self.entries, None);
		self.assertEqual(result, []);

	def test_filter_entries_empty(self):
		filters = [tvshows.make_filter('Supernatural', quality='720p')];
		result = ut.filter_data([], filters);
		self.assertEqual(result, []);

	def test_filter_filters_empty(self):
		result = ut.filter_data(self.entries, []);
		self.assertEqual(result, []);

	def tearDown(self):
		self.entries = None;

if __name__ == '__main__':
	unittest.main();