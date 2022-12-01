import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

create_table = """
CREATE TABLE IF NOT EXISTS weather (
    forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
	weekday TEXT,
	month TEXT,
	weather TEXT,
	temperature_day TEXT,
	temperature_night TEXT,
	ctl_id INTEGER,
	ctl_date TEXT,
	ctl_action TEXT
)
"""
cur.execute(create_table)


data = [
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
    ("monday", "dec", "weather", "day", "night", 1, "01.12.2022", "A"),
]
insert = """
INSERT INTO weather(
	weekday,
	month,
	weather,
	temperature_day,
	temperature_night,
	ctl_id,
	ctl_date,
	ctl_action
) 
VALUES(?, ?, ?, ?, ?, ?, ?, ?)
"""
cur.executemany(insert, data)

select_all = """
select *
from weather
"""
for each_row in cur.execute(select_all):
    print(each_row)


