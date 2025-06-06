from datetime import datetime
from zhdate import ZhDate as lunar_date
import re

# 纪念日
start_date = "2024-02-26"
birthday = "小王 r01-21\n小李 r01-18"

persons = []
birthdays = []


today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# 处理名字和生日数组
def split_birthday():
    if birthday is None:
        return None
    arr = birthday.split('\n')
    for m in arr:
        objArr = m.split(' ')
        persons.append(objArr[0])
        birthdays.append(objArr[1])

split_birthday()

data = {

}

# 纪念日正数
def get_memorial_days_count():
    if start_date is None:
      print('没有设置 START_DATE')
      return 0
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

# 获取当前日期为星期几
def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[today.weekday()]
  return week_day

# 各种倒计时
def get_counter_left(name,aim_date):
  if aim_date is None:
    return 0

  # 为了经常填错日期的同学们
  if re.match(r'^\d{1,2}\-\d{1,2}$', aim_date):
    next = datetime.strptime(str(today.year) + "-" + aim_date, "%Y-%m-%d")
  elif re.match(r'^\d{2,4}\-\d{1,2}\-\d{1,2}$', aim_date):
    next = datetime.strptime(aim_date, "%Y-%m-%d")
    next = next.replace(today.year)
  else:
    print('日期格式不符合要求')
  print(next,today,next.year + 1,(next-today).days)
  if(next.strftime("%Y-%m-%d")==today.strftime("%Y-%m-%d")):
    return "亲爱的%s生日快乐 Happy birthday!" % (name)
  if next < today:
    next = next.replace(year=next.year + 1)
  return "距离%s的生日还有：%d天" % (name, (next - today).days)

for index, aim_date in enumerate(birthdays):
  key_name = "birthday_left"
  if aim_date[0] == "r":
    dArr = aim_date[1:].split("-")
    dArr.insert(0,today.year)
    aim_date = lunar_date(dArr[0],int(dArr[1]),int(dArr[2])).to_datetime()
    aim_date = aim_date.strftime("%m-%d")
  if index != 0:
    key_name = key_name + "_%d" % index
  data[key_name] = {
    "value": get_counter_left(persons[index], aim_date),
  }

print(data,get_memorial_days_count(),get_week_day())