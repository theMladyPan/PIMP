import unittest, random
from pimp_lib import *

class TestStringMethods(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual(dummy_func("text"), 'texttext')
    def test_median(self):
        self.assertEqual(median([1,2,3,4,5]),3)
        self.assertEqual(median([1,2,4,5]),3)
        self.assertNotEqual(median([1,2,4,5]),2)
    def test_multi_p(self):
        img1 = openImage("img/obr.jpg")
        img2 = multiproc(invert(openImage("img/obr.jpg")), exponential, args=())
        save(img2,"img/out.jpg")
        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main()
