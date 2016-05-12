import unittest
import rss_download as ut

class TvTest(unittest.TestCase):
	def test_show_info(self):
		result = ut.show_info('new girl s04e03 hdtv 720p');
		expect = {'name': 'New Girl', 'season': 4, 'episode': 3};
		self.assertEqual(result, expect);

		result = ut.show_info('new.girl.s03e21 hdtv 720p asdf');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 21};
		self.assertEqual(result, expect);

		result = ut.show_info('new girl 304 hdtv');
		expect = {'name': 'New Girl', 'season': 3, 'episode': 4};
		self.assertEqual(result, expect);

		with self.assertRaises(ValueError):
			result = ut.show_info('');

		with self.assertRaises(ValueError):
			result = ut.show_info('new girl');

		result = ut.show_info('30 rock s13e24 hdtv');
		expect = {'name': '30 Rock', 'season': 13, 'episode': 24};
		self.assertEqual(result, expect);

if __name__ == '__main__':
	unittest.main();