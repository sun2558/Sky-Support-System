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
        print("未找到7天天气预报数据,尝试查找其他结构...")
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

class WeatherCrawler:
    """天气数据采集器 - 天擎系统专用模块"""
    
    def __init__(self, config=None):
        # 保持你现有配置，增加扩展性
        self.config = config or {
            'timeout': 30,
            'retry_times': 3,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.quality_checker = None  # 为明天的3σ检测预留
    
    def fetch_weather(self, city_code, save_to_csv=True):
        """
        获取天气数据 - 直接重用你验证过的代码
        """
        # 直接调用你上面已经写好的函数！
        data, city_name = get_weather_data(city_code)
        
        # 保持你原有的保存逻辑
        if save_to_csv and data:
            write_to_csv(data, city_name)
            
        return data, city_name
    
    def batch_fetch(self, city_codes):
        """批量获取多个城市数据 - 新增功能"""
        results = {}
        for code in city_codes:
            print(f"正在获取城市 {code} 的数据...")
            results[code] = self.fetch_weather(code, save_to_csv=False)
        return results

# ==================== 测试新旧架构共存 ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("天擎系统天气模块测试")
    print("="*50)
    
    # 测试1：你原来的方式（确保不破坏）
    print("=== 测试原有函数 ===")
    data, city = get_weather_data('101090114')
    print(f"✅ 原有函数正常: {city} - {len(data)}天数据")
    
    # 测试2：新的类方式
    print("\n=== 测试新架构 ===")
    crawler = WeatherCrawler()
    data, city = crawler.fetch_weather('101090114')
    print(f"✅ 新架构正常: {city} - {len(data)}天数据")
    
    # 测试3：批量功能
    print("\n=== 测试批量获取 ===")
    cities = ['101090114', '101010100']  # 鹿泉区 + 北京
    results = crawler.batch_fetch(cities)
    for code, (data, name) in results.items():
        if data:
            print(f"✅ {name}: {len(data)}天数据")
        else:
            print(f"❌ {name}: 获取失败")