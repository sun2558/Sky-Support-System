# run_pipeline.py - 绕过 normalization.py 问题版
import os
import sys
import pandas as pd
import importlib.util

print("=" * 60)
print("气象数据处理管道 - 绕过标准化模块版")
print("=" * 60)

# 项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"项目根目录: {current_dir}")

# src/date 目录
src_date_dir = os.path.join(current_dir, "src", "date")
print(f"模块目录: {src_date_dir}")

if not os.path.exists(src_date_dir):
    print("❌ 错误: 找不到 src/date/ 目录")
    sys.exit(1)

# 检查文件
print("\n📁 检查模块文件...")
module_files = {
    "loader": "loader.py",
    "imputation": "imputation.py", 
    "quality_check": "quality_check.py",
    "report_generator": "report_generator.py"
}

modules = {}
for name, filename in module_files.items():
    path = os.path.join(src_date_dir, filename)
    if os.path.exists(path):
        print(f"  ✅ {filename}: 存在")
        modules[name] = path
    else:
        print(f"  ❌ {filename}: 不存在")

print("\n" + "=" * 60)
print("开始导入模块...")
print("=" * 60)

# 导入模块函数
def import_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # 导入三个正常模块
    loader = import_module("loader", modules["loader"])
    imputation = import_module("imputation", modules["imputation"])
    quality_check = import_module("quality_check", modules["quality_check"])
    report_generator = import_module("report_generator", modules["report_generator"])
    
    # 获取函数
    load_weather_data = loader.load_weather_data
    linear_impute = imputation.linear_impute
    ThreeSigmaDetector = quality_check.ThreeSigmaDetector
    generate_quality_report = report_generator.generate_quality_report
    
    # 内置标准化函数（绕过有问题的 normalization.py）
    def zscore_normalize(data, columns=None):
        """Z-score标准化（内置版本）"""
        if columns is None:
            columns = data.select_dtypes(include=['number']).columns
        
        result = data.copy()
        for col in columns:
            if col in data.columns:
                mean_val = data[col].mean()
                std_val = data[col].std()
                if std_val > 0:
                    result[col] = (data[col] - mean_val) / std_val
        return result
    
    print("✅ 模块导入成功（标准化函数已内置）")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 数据文件
data_path = os.path.join(current_dir, "data", "raw", "weather.csv")
print(f"\n📊 数据文件: {data_path}")

if not os.path.exists(data_path):
    print("❌ 错误: 找不到数据文件")
    sys.exit(1)

print("\n" + "=" * 60)
print("开始处理数据...")
print("=" * 60)

# 1. 加载数据
print("\n[1/5] 加载数据...")
try:
    raw_df = load_weather_data(data_path)
    print(f"   ✅ 加载成功: {raw_df.shape}")
    
    # 确定分析列
    if 'temperature' in raw_df.columns:
        target_col = 'temperature'
    else:
        numeric_cols = raw_df.select_dtypes(include=['number']).columns
        target_col = numeric_cols[0] if len(numeric_cols) > 0 else raw_df.columns[0]
    
    print(f"   分析列: {target_col}")
    
except Exception as e:
    print(f"   ❌ 加载失败: {e}")
    sys.exit(1)

# 2. 异常检测
print(f"\n[2/5] 异常检测 ({target_col})...")
try:
    detector = ThreeSigmaDetector(sigma_level=3)
    detector.fit(raw_df[target_col].dropna())
    
    mean_val = raw_df[target_col].mean()
    std_val = raw_df[target_col].std()
    upper = mean_val + 3 * std_val
    lower = mean_val - 3 * std_val
    
    outlier_mask = (raw_df[target_col] > upper) | (raw_df[target_col] < lower)
    outlier_count = outlier_mask.sum()
    
    print(f"   ✅ 检测完成: {outlier_count}个异常值")
    
except Exception as e:
    print(f"   ❌ 异常检测失败: {e}")
    outlier_mask = None

# 3. 数据处理
cleaned_df = raw_df.copy()

# 4. 缺失值插值
print(f"\n[3/5] 缺失值插值 ({target_col})...")
try:
    missing_before = cleaned_df[target_col].isna().sum()
    cleaned_df = linear_impute(cleaned_df, column=target_col, max_gap=5, method='linear')
    missing_after = cleaned_df[target_col].isna().sum()
    print(f"   ✅ 插值完成: 修复{missing_before - missing_after}个缺失值")
except Exception as e:
    print(f"   ❌ 插值失败: {e}")

# 5. 数据标准化（使用内置函数）
print(f"\n[4/5] 数据标准化 ({target_col})...")
try:
    cleaned_df = zscore_normalize(cleaned_df, columns=[target_col])
    print(f"   ✅ 标准化完成 (Z-score)")
except Exception as e:
    print(f"   ❌ 标准化失败: {e}")

# 6. 生成报告
print(f"\n[5/5] 生成质量报告...")
try:
    reports_dir = os.path.join(current_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "quality_report.txt")
    
    report_gen = generate_quality_report(
        raw_df=raw_df,
        cleaned_df=cleaned_df,
        column=target_col,
        outlier_mask=outlier_mask,
        save_format="txt",
        save_path=report_path
    )
    
    print(f"   ✅ 报告生成成功！")
    print(f"   报告位置: {report_path}")
    
    # 显示报告头
    if os.path.exists(report_path):
        print(f"\n📄 报告前3行:")
        with open(report_path, 'r', encoding='utf-8') as f:
            for i in range(3):
                line = f.readline()
                if line:
                    print(f"   {line.rstrip()}")
    
except Exception as e:
    print(f"   ❌ 报告生成失败: {e}")

print("\n" + "=" * 60)
print("🎉 数据处理管道执行完成！")
print("=" * 60)
print(f"原始数据: {raw_df.shape}")
print(f"清洗后数据: {cleaned_df.shape}")

if outlier_mask is not None:
    print(f"检测异常值: {outlier_mask.sum()}个")

print(f"\n📁 报告文件: {report_path}")
print("=" * 60)