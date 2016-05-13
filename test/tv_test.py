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


if __name__ == '__main__':
	unittest.main();