import requests
from bs4 import BeautifulSoup
import csv

def get_weather_data(city_code):
    # 构建URL
    url = f'http://www.weather.com.cn/weather/{city_code}.shtml'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=header, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        print(f"网页请求成功，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求网页错误: {e}")
        return []
    
    # 解析网页内容
    final_data = []
    bs = BeautifulSoup(html, "html.parser")
    
    # 首先尝试获取城市名称
    try:
        city_name = bs.find('div', class_='ctop').find('a').text
        print(f"获取到城市: {city_name}")
    except:
        print("未能获取城市名称")
        city_name = "未知城市"
    
    # 查找7天天气预报数据
    data_div = bs.find('div', {'id': '7d'})
    
    if data_div:
        print("找到7天天气预报数据")
        ul = data_div.find('ul')
        li_list = ul.find_all('li')
        
        for day in li_list:
            temp = []
            try:
                # 提取日期
                date = day.find('h1').string
                temp.append(date)
                
                # 提取天气状况
                inf = day.find_all('p')
                weather_condition = inf[0].string
                temp.append(weather_condition)
                
                # 提取温度
                tem_low = inf[1].find('i').string # 最低温
                if inf[1].find('span') is not None:
                    tem_high = inf[1].find('span').string # 最高温
                    tem_high = tem_high.replace('℃', '')
                else:
                    tem_high = ''
                tem_low = tem_low.replace('℃', '')
                
                temp.append(tem_high)
                temp.append(tem_low)
                
                final_data.append(temp)
                print(f"解析成功: {date} - {weather_condition} - 高温{tem_high}°C - 低温{tem_low}°C")
            except Exception as e:
                print(f"解析某天数据时出错: {e}")
                continue
    else:
        print("未找到7天天气预报数据，尝试查找其他结构...")
        # 可以添加其他数据结构的解析逻辑
    
    return final_data, city_name

def write_to_csv(data, city_name, filename=None):
    if filename is None:
        filename = f'{city_name}_weather.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['日期', '天气', '最高温(℃)', '最低温(℃)'])
        writer.writerows(data)
    print(f"数据已保存到 {filename}")

# 调试石家庄鹿泉区天气
if __name__ == '__main__':
    city_code = '101090114'  # 石家庄鹿泉区
    print(f"开始获取城市代码 {city_code} 的天气数据...")
    
    weather_result, city_name = get_weather_data(city_code)
    
    if weather_result:
        write_to_csv(weather_result, city_name)
        print(f"成功获取 {city_name} 的 {len(weather_result)} 天天气预报")
    else:
        print("未获取到数据，可能的原因：")
        print("1. 城市代码错误")
        print("2. 网页结构发生变化")
        print("3. 网络连接问题")
        print("4. 网站反爬虫机制")