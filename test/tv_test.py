import unittest
import rss_download as ut

class ShowInfoTest(unittest.TestCase):
	def test_spaces_format_sxxeyy(self):
		result = ut.show_info('new girl s04e03 hdtv 720p');
		expect = {'name': 'New Girl', 'season': 4, 'episode': 3};
		self.assertEqual(result, expect);

	def test_dots_format_sxxeyy(self):
		result = ut.show_info('new.girl.s03e21 hdtv 720p asdf');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 21};
		self.assertEqual(result, expect);

	def test_spaces_format_xyz(self):
		result = ut.show_info('new girl 304 hdtv');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 4};
		self.assertEqual(result, expect);

	def test_dots_format_xyz(self):
		result = ut.show_info('new.girl.304.hdtv');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 4};
		self.assertEqual(result, expect);

	def test_number_in_title(self):
		result = ut.show_info('30 rock s13e24 hdtv');
		expect = {'name': '30 Rock', 'season': 13, 'episode': 24};
		self.assertEqual(result, expect);

	def test_empty_string(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('');

	def test_only_title(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('new girl');

	def test_title_and_season(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('new girl s05 hdrip');

	def test_title_and_episode(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('new girl e05 hdrip');

	def test_only_season(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('s05');

	def test_only_episode(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('e13');

	def test_no_title(self):
		with self.assertRaises(ValueError):
			result = ut.show_info('s04e15');


class ContainsEpisodeTest(unittest.TestCase):
	def setUp(self):
		matched_list = [];
		matched_list.append({'name': 'New Girl', 'season': 3,'episode': 15});
		matched_list.append({'name': 'New Girl', 'season': 3,'episode': 17});
		matched_list.append({'name': 'New Girl', 'season': 4,'episode': 17});
		matched_list.append({'name': 'New Girl', 'season': 4,'episode': 15});
		matched_list.append({'name': 'Supernatural', 'season': 3,'episode': 17});
		matched_list.append({'name': 'Sex And The City', 'season': 2,'episode': 5});

		self.matched_list = matched_list;

	def test_distinct_item_found(self):
		info = {'name': 'Sex And The City', 'season': 2, 'episode': 5};
		self.assertTrue(ut.contains_episode(self.matched_list, info));

	def test_distinct_item_not_found(self):
		info = {'name': 'Seinfeld', 'season': 2, 'episode': 5};
		self.assertFalse(ut.contains_episode(self.matched_list, info));

	def test_similar_item_found(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 17};
		self.assertTrue(ut.contains_episode(self.matched_list, info));

	def test_similar_item_not_found(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 2};
		self.assertFalse(ut.contains_episode(self.matched_list, info));

	def test_name_lowercase(self):
		info = {'name': 'new girl', 'season': 3, 'episode': 17};
		self.assertTrue(ut.contains_episode(self.matched_list, info));

	def test_no_info(self):
		with self.assertRaises(TypeError):
			ut.contains_episode(self.matched_list, None);

	def test_no_list(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 17};
		with self.assertRaises(TypeError):
			ut.contains_episode(None, info);

	def test_no_episode(self):
		info = {'name': 'New Girl', 'season': 3};
		with self.assertRaises(KeyError):
			ut.contains_episode(self.matched_list, info);

	def test_no_season(self):
		info = {'name': 'New Girl', 'episode': 17};
		with self.assertRaises(KeyError):
			ut.contains_episode(self.matched_list, info);

	def tearDown(self):
		self.matched_list = None;

class rssFilterTest(unittest.TestCase):
	
	def test_filter_uppercase(self):
		filt = ut.rss_filter('New Girl', '720P');
		expect = 'new[\s_\.]?girl.*720p.*';
		self.assertEqual(filt, expect);

	def test_filter_lowercase(self):
		filt = ut.rss_filter('new girl', '720p');
		expect = 'new[\s_\.]?girl.*720p.*';
		self.assertEqual(filt, expect);

	def test_filter_no_quality(self):
		filt = ut.rss_filter('new girl', None);
		expect = 'new[\s_\.]?girl.*';
		self.assertEqual(filt, expect);

	def test_filter_no_name(self):
		with self.assertRaises(ValueError):
			filt = ut.rss_filter(None, '720p');


class filterDataTest(unittest.TestCase):

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
		filters = [ut.rss_filter('Supernatural', None)];
		matches = ut.filter_data(self.entries, filters);
		expect = [{'name': 'Supernatural', 'season': 11, 'episode': 21, 'link': ''}];
		self.assertEqual(matches, expect);

	def test_filter_no_quality_not_found(self):
		filters = [ut.rss_filter('sex and the city', None)];
		matches = ut.filter_data(self.entries, filters);
		self.assertEqual(matches, []);

	def test_filter_quality_found(self):
		filters = [ut.rss_filter('Supernatural', '720p')];
		matches = ut.filter_data(self.entries, filters);
		expect = [{'name': 'Supernatural', 'season': 11, 'episode': 21, 'link': ''}];
		self.assertEqual(matches, expect);

	def test_filter_quality_not_found(self):
		filters = [ut.rss_filter('Supernatural', '1080p')];
		matches = ut.filter_data(self.entries, filters);
		self.assertEqual(matches, []);

	def test_filter_entries_none(self):
		filters = [ut.rss_filter('Supernatural', '720p')];
		result = ut.filter_data(None, filters);
		self.assertEqual(result, []);

	def test_filter_filters_none(self):
		result = ut.filter_data(self.entries, None);
		self.assertEqual(result, []);

	def test_filter_entries_empty(self):
		filters = [ut.rss_filter('Supernatural', '720p')];
		result = ut.filter_data([], filters);
		self.assertEqual(result, []);

	def test_filter_filters_empty(self):
		result = ut.filter_data(self.entries, []);
		self.assertEqual(result, []);

	def tearDown(self):
		self.entries = None;


if __name__ == '__main__':
	unittest.main();