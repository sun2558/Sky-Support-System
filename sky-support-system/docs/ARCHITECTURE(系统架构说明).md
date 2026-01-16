# 天擎系统架构

## 模块设计
- **loader.py**：加载CSV气象数据
- **quality_check.py**：用3σ原则检测异常值  
- **imputation.py**：线性插值填充缺失数据
- **normalization.py**：Z-score标准化数据
- **report_generator.py**：生成数据质量报告

## 运行流程
数据 → 加载 → 异常检测 → 缺失值填充 → 标准化 → 报告生成

## 技术特点
- 纯Python + Pandas实现
- 模块化设计，便于扩展
- 自动生成可读报告