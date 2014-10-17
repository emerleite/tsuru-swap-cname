import unittest

from mock import MagicMock
from mock import Mock
import httpretty
from swap_cname import SwapCname


class TestSwapCname(unittest.TestCase):

    def setUp(self):
        self.swap_cname = SwapCname('token', 'tsuru.globoi.com')
        self.cnames = [u'cname1', u'cname2']

    @httpretty.activate
    def test_get_cname_returns_a_list_when_present(self):
        httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                               body='{"cname":["cname1", "cname2"]}')

        self.assertEqual(self.swap_cname.get_cname('xpto'), self.cnames)

    @httpretty.activate
    def test_get_cname_returns_none_when_empty(self):
        httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                               body='{"cname":[]}')

        self.assertIsNone(self.swap_cname.get_cname('xpto'))

    @httpretty.activate
    def test_remove_cname_return_true_when_can_remove(self):
        httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/cname',
                               data='{"cname":["cname1", "cname2"]}',
                               status=200)

        self.assertTrue(self.swap_cname.remove_cname('xpto', self.cnames))

    @httpretty.activate
    def test_remove_cname_return_false_when_cant_remove(self):
        httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/cname',
                               data='{"cname":["cname1", "cname2"]}',
                               status=500)

        self.assertFalse(self.swap_cname.remove_cname('xpto', self.cnames))

    @httpretty.activate
    def test_set_cname_return_true_when_can_set(self):
        httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/cname',
                               data='{"cname":["cname1", "cname2"]}',
                               status=200)

        self.assertTrue(self.swap_cname.set_cname('xpto', self.cnames))

    @httpretty.activate
    def test_set_cname_return_false_when_cant_set(self):
        httpretty.register_uri(httpretty.POST, 'http://tsuru.globoi.com/apps/xpto/cname',
                               data='{"cname":["cname1", "cname2"]}',
                               status=500)

        self.assertFalse(self.swap_cname.set_cname('xpto', self.cnames))

    @httpretty.activate
    def test_total_units_zero_when_empty(self):
        httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                               body='{"units":[]}',
                               status=500)

        self.assertEqual(self.swap_cname.total_units('xpto'), 0)

    @httpretty.activate
    def test_total_units_gt_zero_when_not_empty(self):
        httpretty.register_uri(httpretty.GET, 'http://tsuru.globoi.com/apps/xpto',
                               body='{"units":["unit1"]}',
                               status=500)

        self.assertGreater(self.swap_cname.total_units('xpto'), 0)

    @httpretty.activate
    def test_remove_units_should_return_true_when_removes(self):
        def side_effect(*args):
            def second_call(*args):
                return 1
            self.swap_cname.total_units.side_effect = second_call
            return 2

        self.swap_cname.total_units = Mock(side_effect=side_effect)

        httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/units',
                               data='1',
                               status=200)

        self.assertTrue(self.swap_cname.remove_units('xpto'))

    @httpretty.activate
    def test_remove_units_should_return_false_when_not_removes(self):
        self.swap_cname.total_units = MagicMock(return_value=2)

        httpretty.register_uri(httpretty.DELETE, 'http://tsuru.globoi.com/apps/xpto/units',
                               data='1',
                               status=500)

        self.assertFalse(self.swap_cname.remove_units('xpto'))

    @httpretty.activate
    def test_add_units_should_return_true_when_adds(self):
        self.swap_cname.total_units = MagicMock(return_value=1)

        httpretty.register_uri(httpretty.PUT, 'http://tsuru.globoi.com/apps/xpto/units',
                               data='1',
                               status=200)

        self.assertTrue(self.swap_cname.add_units('xpto', 2))

    @httpretty.activate
    def test_add_units_should_return_false_when_adds(self):
        self.swap_cname.total_units = MagicMock(return_value=1)

        httpretty.register_uri(httpretty.PUT, 'http://tsuru.globoi.com/apps/xpto/units',
                               data='1',
                               status=500)

        self.assertFalse(self.swap_cname.add_units('xpto', 2))
