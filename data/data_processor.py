import json
import pytz
import datetime
from datetime import time, timedelta

WC_FIXTURES_PATH = "data/world_cup_fixtures.json"
PARSED_WC_FIXTURES_PATH = "data/parsed_world_cup_fixtures.json"

def convert_et_to_irl(et_time: time)->str:
    return et_time.replace(hour=(et_time.hour+5)%24).isoformat(timespec="minutes")

def parse_fixtures():
    with open(WC_FIXTURES_PATH, "r") as file:
        data = json.load(file)
    fixtures = data["matches"]
    parsed_fixtures=[]
    for f in fixtures:
        parsed_f = {}
        parsed_f["date"]=f["date"]
        parsed_f["home"]=f["team_a"]
        parsed_f["away"]=f["team_b"]
        parsed_f["time"]=convert_et_to_irl(time.fromisoformat(f["time_et"]))
        parsed_fixtures.append(parsed_f)
    return parsed_fixtures

def main():
    parsed_fixtures = parse_fixtures()
    with open(PARSED_WC_FIXTURES_PATH, "w") as file:
        json.dump(parsed_fixtures, file)


if __name__ == "__main__":
    main()
