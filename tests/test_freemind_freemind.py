import unittest

from collections import OrderedDict
from freemind import traverse_xml, traverse, freemind_load, select_bottom, print_as_tree


PATH_TO_TEST_FILE = './tests/TestFP.mm'

class FreemindTestCase(unittest.TestCase):

    def test_bottom(self):
        result = freemind_load(PATH_TO_TEST_FILE)
        bottom = select_bottom(result)
        self.assertEqual('In progress', bottom[0].get_title())
        self.assertEqual('Canceled', bottom[1].get_title())

    def test_traverse(self):
        doc = freemind_load(PATH_TO_TEST_FILE)
        nodes = traverse(doc, lambda n: n.get_title() == 'Task1')
        self.assertEqual(1, len(nodes))
        self.assertEqual('Task1', nodes[0].get_title())

    def test_content(self):
        doc = freemind_load(PATH_TO_TEST_FILE)
        node = doc[0][2]
        self.assertEqual('In progress', node.get_title())
        self.assertEqual("abc\ndef", node.get_content())

    def test_content2(self):
        doc = freemind_load(PATH_TO_TEST_FILE)
        node = doc[0][1]
        self.assertEqual('Stop', node.get_title())
        # print(node.get_content())
        # self.assertEqual("abc\ndef", node.get_content())


if __name__ == "__main__":
    unittest.main()
