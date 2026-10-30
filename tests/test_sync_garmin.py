"""Offline tests: no Garmin key, network or health data required."""

import unittest
from datetime import date

from scripts.sync_garmin import (
    merge,
    normalize_activity,
    normalize_daily,
    normalize_hrv,
    normalize_sleep,
    synchronize,
)


class NormalizeTests(unittest.TestCase):
    def test_activity_keeps_useful_fields_but_not_routes(self):
        sample = {
            "activityId": 123,
            "activityName": "SkiErg",
            "activityType": {"typeKey": "fitness_equipment"},
            "startTimeLocal": "2026-10-30 17:20:00",
            "distance": 0.0,
            "duration": 1800.0,
            "averageHR": 145,
            "avgPower": 120,
            "startLatitude": 59.0,
            "startLongitude": 17.0,
            "geoPolylineDTO": {"polyline": "secret"},
            "userProfile": {"email": "private@example.com"},
        }
        result = normalize_activity(sample)
        self.assertEqual(result["distance_m"], 0.0)
        self.assertEqual(result["sport"], "fitness_equipment")
        self.assertEqual(result["average_power_w"], 120)
        self.assertNotIn("startLatitude", result)
        self.assertNotIn("startLongitude", result)
        self.assertNotIn("geoPolylineDTO", result)
        self.assertNotIn("userProfile", result)

    def test_sleep_nested_score(self):
        payload = {"dailySleepDTO": {
            "sleepTimeSeconds": 27000,
            "sleepScores": {"overall": {"value": 79}},
            "deepSleepSeconds": 3600,
        }}
        result = normalize_sleep("2026-10-30", payload)
        self.assertEqual(result["sleep_score"], 79)
        self.assertEqual(result["sleep_seconds"], 27000)

    def test_hrv_summary(self):
        result = normalize_hrv("2026-10-30", {
            "hrvSummary": {"lastNightAvg": 49, "weeklyAvg": 52, "status": "BALANCED"}
        })
        self.assertEqual(result["last_night_average_ms"], 49)

    def test_daily_summary(self):
        result = normalize_daily({
            "calendarDate": "2026-10-30",
            "restingHeartRate": 54,
            "steps": 10000,
            "location": "private",
        })
        self.assertEqual(result["resting_hr_bpm"], 54)
        self.assertNotIn("location", result)

    def test_merge_overwrites_only_same_id_and_prunes_old(self):
        older = [{"id": "1", "start_time_local": "2026-09-20 08:00", "average_hr_bpm": 120}]
        recent = [{"id": "1", "start_time_local": "2026-09-20 08:00", "average_hr_bpm": 130},
                  {"id": "2", "start_time_local": "2026-10-30 08:00", "distance_m": 0}]
        result = merge(older, recent, "id", date(2026, 9, 1))
        self.assertEqual(len(result), 2)
        self.assertEqual(next(x for x in result if x["id"] == "1")["average_hr_bpm"], 130)


class FakeClient:
    def search_activities(self, **kwargs):
        return [{
            "activityId": 444,
            "startTimeLocal": "2026-10-30 12:00:00",
            "duration": 1200,
        }]

    def get_daily_sleep(self, day):
        return {"dailySleepDTO": {"sleepTimeSeconds": 22000}}

    def get_daily_hrv(self, day):
        return {"hrvSummary": {"lastNightAvg": 50}}

    def get_daily_summaries(self, start_date, end_date):
        return [{"calendarDate": end_date, "restingHeartRate": 60}]


class SyncTests(unittest.TestCase):
    def test_sync_builds_snapshot(self):
        snapshot = synchronize(FakeClient(), {}, date(2026, 10, 30))
        self.assertEqual(snapshot["activities"][0]["id"], "444")
        self.assertEqual(len(snapshot["sleep"]), 8)
        self.assertEqual(len(snapshot["hrv"]), 8)
        self.assertEqual(snapshot["daily"][0]["resting_hr_bpm"], 60)
        self.assertEqual(snapshot["sync_status"]["activities"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
