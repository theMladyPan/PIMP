import unittest
from pimp_lib import *

class TestStringMethods(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual(dummy_func("text"), 'texttext')
    def test_median(self):
        self.assertEqual(median([1,2,3,4,5]),3)
        self.assertEqual(median([1,2,4,5]),3)
        self.assertNotEqual(median([1,2,4,5]),2)

if __name__ == '__main__':
    unittest.main()
