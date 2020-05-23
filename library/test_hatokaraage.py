import unittest
from library.hatokaraage import hato_ha_karaage

class TestHatoHaKaraage(unittest.TestCase):

    def test_normal(self):
        self.assertEqual(hato_ha_karaage('hoge'), 'hoge')

    def test_include_hato(self):
        self.assertEqual(hato_ha_karaage('鳩は唐揚げではない'), '鳩は唐揚げ')

if __name__ == '__main__':
    unittest.main()
