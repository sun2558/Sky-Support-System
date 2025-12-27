"""
标准化模块 - 极简实用版
只做项目要求的功能，不多不少
"""

import pandas as pd
import numpy as np

def zscore_normalize(data, columns=None):
    """Z-score标准化"""
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns
    
    result = data.copy()
    params = {}
    
    for col in columns:
        mean = data[col].mean()
        std = data[col].std()
        params[col] = {'mean': mean, 'std': std}
        result[col] = (data[col] - mean) / max(std, 1e-10)  # 避免除零
    
    return result, params

def minmax_normalize(data, columns=None):
    """Min-Max标准化"""
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns
    
    result = data.copy()
    params = {}
    
    for col in columns:
        min_val = data[col].min()
        max_val = data[col].max()
        range_val = max_val - min_val
        params[col] = {'min': min_val, 'max': max_val}
        result[col] = (data[col] - min_val) / max(range_val, 1e-10)
    
    return result, params

def normalize_weather_data(data, method='zscore'):
    """
    主函数：标准化气象数据
    返回：标准化后的数据
    """
    numeric_cols = ['temperature', 'pressure', 'humidity', 'wind_speed']
    numeric_cols = [col for col in numeric_cols if col in data.columns]
    
    if method == 'zscore':
        normalized, params = zscore_normalize(data, numeric_cols)
    elif method == 'minmax':
        normalized, params = minmax_normalize(data, numeric_cols)
    else:
        raise ValueError(f"未知方法: {method}")
    
    print(f"✅ 已完成{method}标准化")
    print(f"   处理列: {numeric_cols}")
    print(f"   数据形状: {data.shape} -> {normalized.shape}")
    
    return normalized

# 演示代码
if __name__ == "__main__":
    # 示例数据
    weather_data = pd.DataFrame({
        'temperature': [20, 22, 19, 25, 18, 30, 15],
        'pressure': [1013, 1012, 1015, 1010, 1014, 1011, 1016],
        'humidity': [60, 65, 58, 70, 55, 75, 50]
    })
    
    print("原始数据:")
    print(weather_data)
    
    # 标准化
    normalized = normalize_weather_data(weather_data, 'zscore')
    print("\n标准化后:")
    print(normalized)
    
    print("\n统计摘要(标准化后):")
print(normalized.describe().round(3))

print("\n验证9应接近0和1):")
print("各列均值:", normalized.mean().round(5).tolist())
print("各列标准差:", normalized.std().round(5).tolist())

    # 也可以试试minmax
    # normalized = normalize_weather_data(weather_data, 'minmax')