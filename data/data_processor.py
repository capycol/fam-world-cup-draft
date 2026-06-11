import json
import pytz
import datetime
from datetime import time, timedelta, date, datetime, timezone

CITY_TIMEZONES_PATH = "data/city_timezones.json"
WC_FIXTURES_PATH = "data/world_cup_fixtures.json"
PARSED_WC_FIXTURES_PATH = "data/parsed_world_cup_fixtures.json"


def convert_et_to_irl(et_date: str, et_time: str, city: str)->str:
    with open(CITY_TIMEZONES_PATH, "r") as f:
        city_timezones = json.load(f)
    et_time_obj = time.fromisoformat(et_time)
    et_date_obj = date.fromisoformat(et_date)
    et_datetime = datetime.combine(et_date_obj, et_time_obj, tzinfo=timezone(timedelta(hours=city_timezones[city])))
    localDatetime = et_datetime.astimezone(pytz.timezone('Europe/Dublin'))

    return localDatetime.date(), localDatetime.time().isoformat("minutes")

def parse_fixtures():
    with open(WC_FIXTURES_PATH, "r") as file:
        data = json.load(file)
    fixtures = data["matches"]
    parsed_fixtures=[]
    cities = set()
    for f in fixtures:
        parsed_f = {}
        irl_date, irl_time = convert_et_to_irl(f["date"], f["time_local"], city=f["city"])
        parsed_f["date"]=str(irl_date)
        parsed_f["home"]=f["team_a"]
        parsed_f["away"]=f["team_b"]
        parsed_f["time"]=str(irl_time)
        parsed_f["location"]=f"{f['city']}, {f['country']}"
        parsed_fixtures.append(parsed_f)
    return parsed_fixtures

def main():
    parsed_fixtures = parse_fixtures()
    with open(PARSED_WC_FIXTURES_PATH, "w") as file:
        json.dump(parsed_fixtures, file)


if __name__ == "__main__":
    main()
