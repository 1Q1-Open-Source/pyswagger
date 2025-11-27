from __future__ import absolute_import
import unittest
import datetime

from pyswagger import utils


class ISO8601NegativeTestCase(unittest.TestCase):
    """Additional positive/negative tests for utils.from_iso8601 (Step 6).

    Strengthens coverage around raw-string regex normalization and parsing
    behavior across Python versions.
    """

    def test_positive_with_timezones_and_fraction(self):
        # Leap day with Zulu
        dt = utils.from_iso8601('2020-02-29T12:34:56Z')
        self.assertEqual(dt, datetime.datetime(2020, 2, 29, 12, 34, 56, tzinfo=utils.FixedTZ(0, 0)))

        # Fractional seconds and positive offset
        dt = utils.from_iso8601('2020-02-29T12:34:56.123456+08:00')
        self.assertEqual(dt.year, 2020)
        self.assertEqual(dt.month, 2)
        self.assertEqual(dt.day, 29)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 34)
        self.assertEqual(dt.second, 56)
        self.assertEqual(dt.microsecond, 123456)
        self.assertEqual(dt.tzinfo.utcoffset(None), utils.FixedTZ(8, 0).utcoffset(None))

        # Negative offset with minutes
        dt = utils.from_iso8601('2020-02-29T12:34:56-05:30')
        self.assertEqual(dt.tzinfo.utcoffset(None), utils.FixedTZ(-5, -30).utcoffset(None))

    def test_negative_invalid_dates_and_formats(self):
        # Invalid month
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-13-01T00:00:00Z')

        # Invalid day
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-30T00:00:00Z')

        # Missing 'T'
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-29 12:34:56Z')

        # Wrong separators
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-29T12-34-56Z')

        # Bad timezone format (no colon)
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-29T12:34:56+0800')

        # Bad timezone hour width
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-29T12:34:56+8:00')

        # Timezone provided but missing time
        with self.assertRaises(ValueError):
            utils.from_iso8601('2020-02-29+08:00')
