from datetime import date, datetime, timedelta

# 纪念日
start_date = "2021-12-18"

today = datetime.now()

# 纪念日正数
def get_memorial_days_count():
    if start_date is None:
      print('没有设置 START_DATE')
      return 0
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

print(today,get_memorial_days_count())