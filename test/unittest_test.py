import unittest 

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_increment(self):
        self.assertEqual(sum([3, 4]), 7)


if __name__ == '__main__':
    unittest.main()
