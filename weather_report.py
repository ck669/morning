# 安装依赖 pip3 install requests html5lib bs4 schedule
import os
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from zhdate import ZhDate as lunar_date

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# 储存名字和生日
persons = []
birthdays = []

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId = os.environ.get("OPEN_ID")
# 城市
city = os.environ.get('CITY')
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")
# 纪念日
start_date = os.environ.get('START_DATE')
# 人员-生日
birthday = os.getenv('BIRTHDAY')

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

def get_weather(my_city):
    if city is None:
      print('请设置城市')
      return None
    urls = ["http://www.weather.com.cn/textFC/hb.shtml",
            "http://www.weather.com.cn/textFC/db.shtml",
            "http://www.weather.com.cn/textFC/hd.shtml",
            "http://www.weather.com.cn/textFC/hz.shtml",
            "http://www.weather.com.cn/textFC/hn.shtml",
            "http://www.weather.com.cn/textFC/xb.shtml",
            "http://www.weather.com.cn/textFC/xn.shtml"
            ]
    for url in urls:
        resp = requests.get(url)
        text = resp.content.decode("utf-8")
        soup = BeautifulSoup(text, 'html5lib')
        div_conMidtab = soup.find("div", class_="conMidtab")
        tables = div_conMidtab.find_all("table")
        for table in tables:
            trs = table.find_all("tr")[2:]
            for index, tr in enumerate(trs):
                tds = tr.find_all("td")
                # 这里倒着数，因为每个省会的td结构跟其他不一样
                city_td = tds[-8]
                this_city = list(city_td.stripped_strings)[0]
                if this_city == my_city:

                    high_temp_td = tds[-5]
                    low_temp_td = tds[-2]
                    weather_type_day_td = tds[-7]
                    weather_type_night_td = tds[-4]
                    wind_td_day = tds[-6]
                    wind_td_day_night = tds[-3]

                    high_temp = list(high_temp_td.stripped_strings)[0]
                    low_temp = list(low_temp_td.stripped_strings)[0]
                    weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                    weather_type_night = list(weather_type_night_td.stripped_strings)[0]

                    wind_day = list(wind_td_day.stripped_strings)[0] + list(wind_td_day.stripped_strings)[1]
                    wind_night = list(wind_td_day_night.stripped_strings)[0] + list(wind_td_day_night.stripped_strings)[1]

                    # 如果没有白天的数据就使用夜间的
                    temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"
                    return this_city, temp, weather_typ, wind

weather = get_weather(city)

def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

# 纪念日正数
def get_memorial_days_count():
    if start_date is None:
      print('没有设置 START_DATE')
      return 0
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_daily_love():
    # 每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love

data = {
    "date": {
        "value": today.strftime("%Y年%m月%d日")
    },
    "region": {
        "value": weather[0]
    },
    "weather": {
        "value": weather[2]
    },
    "temp": {
        "value": weather[1]
    },
    "wind_dir": {
        "value": weather[3]
    },
    "love_days": {
      "value": get_memorial_days_count(),
    },
    "today_note": {
        "value": get_daily_love()
    }
}

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

def send_weather(access_token, value):
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值

    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": value
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)



def weather_report():
    # 1.获取access_token
    access_token = get_access_token()
    # 2. 获取天气
    
    print(f"天气信息： {weather}")
    # 3. 发送消息
    send_weather(access_token, weather)



if __name__ == '__main__':
    weather_report()