#!/usr/bin/env python3
"""Export privacy-minimized personal Garmin summaries (locally or to a private repository).

Only approved fields are persisted. Raw Garmin responses, routes, locations,
credentials and bearer tokens are never written to the JSON export.
"""

from __future__ import annotations

import getpass
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "training.json"
LOCAL_TZ = ZoneInfo("Europe/Stockholm")
HISTORY_DAYS = 365


def pick(obj: object, *keys: str) -> object | None:
    if not isinstance(obj, dict):
        return None
    for key in keys:
        value = obj.get(key)
        if value is not None and not isinstance(value, (dict, list)):
            return value
    return None


def fields(obj: object, mapping: dict[str, tuple[str, ...]]) -> dict:
    result = {}
    for output_key, source_keys in mapping.items():
        value = pick(obj, *source_keys)
        if value is not None:
            result[output_key] = value
    return result


ACTIVITY_FIELDS = {
    "name": ("activityName",),
    "start_time_local": ("startTimeLocal",),
    "start_time_utc": ("startTimeGMT",),
    "distance_m": ("distance",),
    "duration_s": ("duration",),
    "moving_duration_s": ("movingDuration",),
    "elapsed_duration_s": ("elapsedDuration",),
    "average_hr_bpm": ("averageHR", "averageHeartRate"),
    "max_hr_bpm": ("maxHR", "maxHeartRate"),
    "average_power_w": ("avgPower", "averagePower"),
    "max_power_w": ("maxPower",),
    "calories": ("calories",),
    "elevation_gain_m": ("elevationGain",),
    "average_speed_mps": ("averageSpeed",),
    "average_cadence": ("averageRunningCadenceInStepsPerMinute", "averageBikingCadenceInRevPerMinute", "averageCadence"),
    "average_stroke_rate": ("avgStrokeRate", "averageStrokeRate"),
    "aerobic_training_effect": ("aerobicTrainingEffect", "trainingEffect"),
    "anaerobic_training_effect": ("anaerobicTrainingEffect",),
    "training_load": ("activityTrainingLoad",),
}

SLEEP_FIELDS = {
    "sleep_seconds": ("sleepTimeSeconds", "sleepDuration", "sleepSeconds"),
    "deep_sleep_seconds": ("deepSleepSeconds",),
    "light_sleep_seconds": ("lightSleepSeconds",),
    "rem_sleep_seconds": ("remSleepSeconds",),
    "awake_sleep_seconds": ("awakeSleepSeconds",),
}

HRV_FIELDS = {
    "last_night_average_ms": ("lastNightAvg",),
    "last_night_high_5_min_ms": ("lastNight5MinHigh",),
    "weekly_average_ms": ("weeklyAvg",),
    "status": ("status",),
}

DAILY_FIELDS = {
    "resting_hr_bpm": ("restingHeartRate",),
    "average_stress": ("averageStressLevel",),
    "max_stress": ("maxStressLevel",),
    "active_kcal": ("activeKilocalories",),
    "total_kcal": ("totalKilocalories",),
    "steps": ("totalSteps", "steps"),
    "body_battery_charged": ("bodyBatteryChargedValue",),
    "body_battery_drained": ("bodyBatteryDrainedValue",),
}


def normalize_activity(record: object) -> dict | None:
    activity_id = pick(record, "activityId")
    if activity_id is None:
        return None
    result = {"id": str(activity_id)}
    result.update(fields(record, ACTIVITY_FIELDS))
    if isinstance(record, dict):
        activity_type = record.get("activityType")
        if isinstance(activity_type, dict):
            kind = pick(activity_type, "typeKey", "typeName")
        else:
            kind = activity_type if isinstance(activity_type, str) else None
        if kind is not None:
            result["sport"] = kind
    return result


def normalize_sleep(day: str, payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    dto = payload.get("dailySleepDTO") or payload.get("sleepDTO") or payload
    if not isinstance(dto, dict):
        return None
    result = {"date": day}
    result.update(fields(dto, SLEEP_FIELDS))
    scores = dto.get("sleepScores") or payload.get("sleepScores") or {}
    if isinstance(scores, dict):
        overall = scores.get("overall")
        score = pick(overall, "value", "score") if isinstance(overall, dict) else overall
        if isinstance(score, (int, float)):
            result["sleep_score"] = score
    score = pick(dto, "sleepScore")
    if "sleep_score" not in result and isinstance(score, (int, float)):
        result["sleep_score"] = score
    return result if len(result) > 1 else None


def normalize_hrv(day: str, payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    summary = payload.get("hrvSummary") or payload
    result = {"date": day}
    result.update(fields(summary, HRV_FIELDS))
    return result if len(result) > 1 else None


def normalize_daily(payload: object) -> dict | None:
    day = pick(payload, "calendarDate", "date")
    if not isinstance(day, str) or len(day) < 10:
        return None
    result = {"date": day[:10]}
    result.update(fields(payload, DAILY_FIELDS))
    return result if len(result) > 1 else None


def unwrap_list(payload: object, *keys: str) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in keys:
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError("Garmin returned an unexpected list response")


def retrieve_activities(client: object, start_day: date, end_day: date) -> list[dict]:
    records = []
    page_size = 100
    for page in range(10):
        response = client.search_activities(
            start=page * page_size,
            limit=page_size,
            start_date=start_day.isoformat(),
            end_date=end_day.isoformat(),
        )
        batch = unwrap_list(response, "activities", "data")
        for raw in batch:
            normalized = normalize_activity(raw)
            if normalized:
                records.append(normalized)
        if len(batch) < page_size:
            return records
    raise RuntimeError("Activity page limit reached; refusing incomplete export")


def collect_days(client: object, days: list[str], getter: str, normalizer: object) -> tuple[list, dict]:
    results = []
    failures = 0
    for day in days:
        try:
            payload = getattr(client, getter)(day)
            result = normalizer(day, payload)
            if result:
                results.append(result)
        except Exception as exc:
            failures += 1
            # Never print response bodies (which may contain health or account data).
            print(f"Warning: {getter} failed on {day}: {type(exc).__name__}", file=sys.stderr)
    return results, {"fetched": len(results), "errors": failures}


def merge(old: object, new: list, key: str, cutoff: date) -> list:
    by_id = {}
    for item in (old if isinstance(old, list) else []) + new:
        if not isinstance(item, dict) or not item.get(key):
            continue
        item_date = str(item.get("start_time_local") or item.get("start_time_utc") or item.get("date") or "")[:10]
        if len(item_date) != 10 or item_date < cutoff.isoformat():
            continue
        by_id[str(item[key])] = item
    return sorted(by_id.values(), key=lambda v: str(v.get("start_time_local") or v.get("start_time_utc") or v.get("date") or ""), reverse=True)


def synchronize(client: object, existing: dict, today: date) -> dict:
    first_run = not bool(existing.get("last_sync_utc"))
    activities_since = today - timedelta(days=90 if first_run else 30)
    health_days = [(today - timedelta(days=d)).isoformat() for d in range(7, -1, -1)]
    cutoff = today - timedelta(days=HISTORY_DAYS)

    # Activity retrieval is mandatory: fail without overwriting last good snapshot.
    activities = retrieve_activities(client, activities_since, today)
    sleep, sleep_status = collect_days(client, health_days, "get_daily_sleep", normalize_sleep)
    hrv, hrv_status = collect_days(client, health_days, "get_daily_hrv", normalize_hrv)

    daily_status = {"fetched": 0, "errors": 0}
    daily = []
    try:
        response = client.get_daily_summaries(health_days[0], health_days[-1])
        for item in unwrap_list(response, "dailySummaries", "summaries", "data"):
            row = normalize_daily(item)
            if row:
                daily.append(row)
        daily_status["fetched"] = len(daily)
    except Exception as exc:
        daily_status["errors"] = 1
        print(f"Warning: get_daily_summaries failed: {type(exc).__name__}", file=sys.stderr)

    return {
        "schema_version": 1,
        "source": "Garmin Connect Personal API",
        "timezone": "Europe/Stockholm",
        "last_sync_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sync_status": {
            "activities": {"fetched": len(activities), "errors": 0},
            "sleep": sleep_status,
            "hrv": hrv_status,
            "daily": daily_status,
        },
        "activities": merge(existing.get("activities"), activities, "id", cutoff),
        "sleep": merge(existing.get("sleep"), sleep, "date", cutoff),
        "hrv": merge(existing.get("hrv"), hrv, "date", cutoff),
        "daily": merge(existing.get("daily"), daily, "date", cutoff),
    }


def main() -> int:
    key = os.environ.get("GARMIN_PERSONAL_API_KEY", "").strip()
    if not key and sys.stdin.isatty():
        key = getpass.getpass("Garmin Personal API key (hidden): ").strip()
    if not key:
        print("Missing GARMIN_PERSONAL_API_KEY. Add a GitHub Actions secret or run locally in an interactive terminal.", file=sys.stderr)
        return 1

    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    if not isinstance(existing, dict):
        raise ValueError("Existing training snapshot is invalid")

    # Delayed imports let unit tests run without external credentials.
    from garmin_personal_api import GarminPersonalApiClient, PersonalApiAuthenticator

    with PersonalApiAuthenticator() as auth:
        token = auth.obtain_token(key)
    with GarminPersonalApiClient(token.access_token) as client:
        snapshot = synchronize(client, existing, datetime.now(LOCAL_TZ).date())

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    print(
        "Garmin sync complete: "
        f"{len(snapshot['activities'])} activities, {len(snapshot['sleep'])} sleep days, "
        f"{len(snapshot['hrv'])} HRV days, {len(snapshot['daily'])} daily summaries"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Not printing exception strings: server errors may include private data.
        print(f"Garmin sync failed: {type(exc).__name__}. Check key and Actions logs.", file=sys.stderr)
        sys.exit(1)
