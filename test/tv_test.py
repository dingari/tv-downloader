import unittest

import os
import tvshows as ut 	# Unit under test

class ShowInfoTest(unittest.TestCase):
	def test_spaces_format_sxxeyy(self):
		result = ut.get_info('new girl s04e03 hdtv 720p');
		expect = {'name': 'New Girl', 'season': 4, 'episode': 3};
		self.assertEqual(result, expect);

	def test_dots_format_sxxeyy(self):
		result = ut.get_info('new.girl.s03e21 hdtv 720p asdf');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 21};
		self.assertEqual(result, expect);

	def test_spaces_format_xyz(self):
		result = ut.get_info('new girl 304 hdtv');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 4};
		self.assertEqual(result, expect);

	def test_dots_format_xyz(self):
		result = ut.get_info('new.girl.304.hdtv');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 4};
		self.assertEqual(result, expect);

	def test_number_in_title(self):
		result = ut.get_info('30 rock s13e24 hdtv');
		expect = {'name': '30 Rock', 'season': 13, 'episode': 24};
		self.assertEqual(result, expect);

	def test_empty_string(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('');

	def test_only_title(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('new girl');

	def test_title_and_season(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('new girl s05 hdrip');

	def test_title_and_episode(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('new girl e05 hdrip');

	def test_only_season(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('s05');

	def test_only_episode(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('e13');

	def test_no_title(self):
		with self.assertRaises(ValueError):
			result = ut.get_info('s04e15');


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
		self.assertTrue(ut.is_contained(self.matched_list, info));

	def test_distinct_item_not_found(self):
		info = {'name': 'Seinfeld', 'season': 2, 'episode': 5};
		self.assertFalse(ut.is_contained(self.matched_list, info));

	def test_similar_item_found(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 17};
		self.assertTrue(ut.is_contained(self.matched_list, info));

	def test_similar_item_not_found(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 2};
		self.assertFalse(ut.is_contained(self.matched_list, info));

	def test_name_lowercase(self):
		info = {'name': 'new girl', 'season': 3, 'episode': 17};
		self.assertTrue(ut.is_contained(self.matched_list, info));

	def test_no_info(self):
		with self.assertRaises(TypeError):
			ut.is_contained(self.matched_list, None);

	def test_no_list(self):
		info = {'name': 'New Girl', 'season': 3, 'episode': 17};
		with self.assertRaises(TypeError):
			ut.is_contained(None, info);

	def test_no_episode(self):
		info = {'name': 'New Girl', 'season': 3};
		with self.assertRaises(KeyError):
			ut.is_contained(self.matched_list, info);

	def test_no_season(self):
		info = {'name': 'New Girl', 'episode': 17};
		with self.assertRaises(KeyError):
			ut.is_contained(self.matched_list, info);

	def tearDown(self):
		self.matched_list = None;

class RssFilterTest(unittest.TestCase):
	
	def test_filter_uppercase(self):
		filt = ut.make_filter('New Girl', quality='720P');
		expect = 'new[\s_\.]?girl.*720p.*';
		self.assertEqual(filt, expect);

	def test_filter_lowercase(self):
		filt = ut.make_filter('new girl', quality='720p');
		expect = 'new[\s_\.]?girl.*720p.*';
		self.assertEqual(filt, expect);

	def test_filter_no_quality(self):
		filt = ut.make_filter('new girl');
		expect = 'new[\s_\.]?girl.*';
		self.assertEqual(filt, expect);

	def test_filter_no_name(self):
		with self.assertRaises(ValueError):
			filt = ut.make_filter(None, quality='720p');

class SearchTest(unittest.TestCase):
	def setUp(self):
		self.root_dir = os.path.join(os.getcwd(), 'test', 'root');

		self.name = 'New Girl';
		self.season = 4;
		self.episode = 15;

	def test_search_found(self):
		self.path = os.path.join(self.root_dir, 'new.girl.s04e15.720p.hdtv.asdf.fdsa');
		os.mkdir(self.root_dir);
		open(self.path, 'w+');
		self.assertTrue(ut.search(self.root_dir, name=self.name, season=self.season, episode=self.episode));

	def test_search_not_found(self):
		self.path = self.root_dir;
		os.mkdir(self.root_dir);

		self.assertFalse(ut.search(self.root_dir, name=self.name, season=self.season, episode=self.episode));

	def tearDown(self):
		if(os.path.exists(self.path) and os.path.isfile(self.path)):
			os.remove(self.path);
		os.removedirs(self.root_dir);

if __name__ == '__main__':
	unittest.main();