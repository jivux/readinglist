try:
    import unittest2 as unittest
except ImportError:
    import unittest

import threading

from readinglist.utils import timestamper, msec_time


class TimeStamperTest(unittest.TestCase):
    def test_timestamps_are_based_on_real_time(self):
        msec_before = msec_time()
        now = timestamper.now()
        msec_after = msec_time()
        self.assertTrue(msec_before - 1 < now < msec_after + 1)

    def test_timestamp_are_always_different(self):
        before = timestamper.now()
        now = timestamper.now()
        after = timestamper.now()
        self.assertTrue(before < now < after)

    def test_timestamp_have_under_one_millisecond_precision(self):
        msec_before = msec_time()
        now1 = timestamper.now()
        now2 = timestamper.now()
        msec_after = msec_time()
        self.assertNotEqual(now1, now2)
        # Assert than less than 1 msec elapsed (Can fail on very slow machine)
        self.assertTrue(msec_before - msec_after <= 1)

    def test_timestamp_are_thread_safe(self):
        obtained = []

        def hit_timestamp():
            for i in range(1000):
                obtained.append(timestamper.now())

        thread1 = threading.Thread(target=hit_timestamp)
        thread2 = threading.Thread(target=hit_timestamp)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # With CPython (GIL), list appending is thread-safe
        self.assertEqual(len(obtained), 2000)
        # No duplicated timestamps
        self.assertEqual(len(set(obtained)), len(obtained))
