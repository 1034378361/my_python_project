"""
测试数据分析模块
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from my_python_project.data_analysis import (
    # 数据处理函数
    load_data, clean_data, validate_data_quality,
    # 分析函数
    basic_statistics, correlation_analysis, detect_outliers,
    # 可视化函数
    create_histogram, create_scatter_plot, create_correlation_heatmap,
    # 导出函数
    export_results, generate_report
)


class TestDataLoading:
    """数据加载测试"""
    
    def test_load_csv_data(self):
        """测试CSV数据加载"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        
        with patch('pandas.read_csv', return_value=test_data) as mock_read:
            result = load_data('test.csv')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5
            assert list(result.columns) == ['A', 'B', 'C']
            mock_read.assert_called_once_with('test.csv')
    
    def test_load_excel_data(self):
        """测试Excel数据加载"""
        test_data = pd.DataFrame({'value': [1, 2, 3]})
        
        with patch('pandas.read_excel', return_value=test_data) as mock_read:
            result = load_data('test.xlsx')
            
            assert isinstance(result, pd.DataFrame)
            mock_read.assert_called_once_with('test.xlsx')
    
    def test_load_json_data(self):
        """测试JSON数据加载"""
        test_data = pd.DataFrame({'value': [1, 2, 3]})
        
        with patch('pandas.read_json', return_value=test_data) as mock_read:
            result = load_data('test.json')
            
            assert isinstance(result, pd.DataFrame)
            mock_read.assert_called_once_with('test.json')
    
    def test_load_unsupported_format(self):
        """测试不支持的文件格式"""
        with pytest.raises(ValueError, match="不支持的文件格式"):
            load_data('test.txt')


class TestDataCleaning:
    """数据清理测试"""
    
    def test_clean_data_basic(self):
        """测试基本数据清理"""
        # 创建包含缺失值和重复行的数据
        dirty_data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 4],
            'B': [10, np.nan, 30, 40, 40],
            'C': ['a', 'b', 'c', 'd', 'd']
        })
        
        cleaned = clean_data(dirty_data)
        
        # 检查缺失值被处理
        assert not cleaned.isna().any().any()
        
        # 检查重复行被移除
        assert len(cleaned) == len(cleaned.drop_duplicates())
    
    def test_clean_data_custom_options(self):
        """测试自定义清理选项"""
        dirty_data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 4],
            'B': [10, np.nan, 30, 40, 40]
        })
        
        # 不删除重复行
        cleaned = clean_data(dirty_data, remove_duplicates=False)
        assert len(cleaned) == 5  # 原始行数
        
        # 不填充缺失值
        cleaned = clean_data(dirty_data, fill_missing=False)
        assert cleaned.isna().sum().sum() > 0
    
    def test_validate_data_quality(self):
        """测试数据质量验证"""
        # 高质量数据
        good_data = pd.DataFrame({
            'A': range(100),
            'B': range(100, 200)
        })
        
        quality_report = validate_data_quality(good_data)
        
        assert quality_report['missing_percentage'] == 0.0
        assert quality_report['duplicate_percentage'] == 0.0
        assert quality_report['total_rows'] == 100
        assert quality_report['total_columns'] == 2
        
        # 低质量数据
        bad_data = pd.DataFrame({
            'A': [1, np.nan, 1, np.nan],
            'B': [10, 20, 10, 20]
        })
        
        quality_report = validate_data_quality(bad_data)
        
        assert quality_report['missing_percentage'] == 25.0  # 2/8 = 25%
        assert quality_report['duplicate_percentage'] == 50.0  # 2/4 = 50%


class TestStatisticalAnalysis:
    """统计分析测试"""
    
    def test_basic_statistics(self):
        """测试基本统计分析"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['x', 'y', 'z', 'x', 'y']  # 分类数据
        })
        
        stats = basic_statistics(data)
        
        # 数值列统计
        assert 'A' in stats
        assert 'B' in stats
        assert stats['A']['mean'] == 3.0
        assert stats['A']['std'] == pytest.approx(1.58, rel=1e-2)
        assert stats['B']['min'] == 10
        assert stats['B']['max'] == 50
        
        # 分类列不应包含在数值统计中
        assert 'C' not in stats
    
    def test_correlation_analysis(self):
        """测试相关性分析"""
        # 创建有相关性的数据
        np.random.seed(42)
        data = pd.DataFrame({
            'A': range(50),
            'B': range(0, 100, 2),  # 与A完全相关
            'C': np.random.randn(50)  # 随机数据
        })
        
        correlations = correlation_analysis(data)
        
        assert isinstance(correlations, pd.DataFrame)
        assert correlations.shape == (3, 3)
        
        # A和B应该高度相关
        assert correlations.loc['A', 'B'] == pytest.approx(1.0, rel=1e-2)
        assert correlations.loc['B', 'A'] == pytest.approx(1.0, rel=1e-2)
        
        # 对角线应该为1
        assert correlations.loc['A', 'A'] == 1.0
    
    def test_detect_outliers(self):
        """测试异常值检测"""
        # 创建包含异常值的数据
        normal_data = np.random.normal(0, 1, 100)
        outliers = np.array([10, -10, 15])  # 明显的异常值
        data_with_outliers = np.concatenate([normal_data, outliers])
        
        df = pd.DataFrame({'value': data_with_outliers})
        outlier_indices = detect_outliers(df, 'value')
        
        assert isinstance(outlier_indices, list)
        assert len(outlier_indices) > 0
        
        # 检查检测到的异常值确实是异常的
        detected_values = df.loc[outlier_indices, 'value'].values
        assert any(abs(val) > 3 for val in detected_values)
    
    def test_detect_outliers_no_outliers(self):
        """测试无异常值的情况"""
        # 创建正常分布数据
        normal_data = np.random.normal(0, 1, 100)
        df = pd.DataFrame({'value': normal_data})
        
        outlier_indices = detect_outliers(df, 'value')
        
        # 可能有少数异常值，但不应该太多
        assert len(outlier_indices) < 10


class TestVisualization:
    """可视化测试"""
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_histogram(self, mock_figure, mock_savefig):
        """测试直方图创建"""
        data = pd.Series(np.random.normal(0, 1, 100))
        
        create_histogram(data, 'test_column', save_path='test.png')
        
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with('test.png', dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_scatter_plot(self, mock_figure, mock_savefig):
        """测试散点图创建"""
        x_data = np.random.randn(50)
        y_data = x_data + np.random.randn(50) * 0.5
        
        create_scatter_plot(x_data, y_data, 'X', 'Y', save_path='scatter.png')
        
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with('scatter.png', dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_correlation_heatmap(self, mock_figure, mock_savefig):
        """测试相关性热图创建"""
        data = pd.DataFrame({
            'A': range(20),
            'B': range(0, 40, 2),
            'C': np.random.randn(20)
        })
        
        create_correlation_heatmap(data, save_path='heatmap.png')
        
        mock_figure.assert_called_once()
        mock_savefig.assert_called_once_with('heatmap.png', dpi=300, bbox_inches='tight')


class TestExportFunctions:
    """导出功能测试"""
    
    @patch('pandas.DataFrame.to_csv')
    def test_export_results_csv(self, mock_to_csv):
        """测试CSV导出"""
        data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        export_results(data, 'results.csv', format='csv')
        
        mock_to_csv.assert_called_once_with('results.csv', index=False)
    
    @patch('pandas.DataFrame.to_excel')
    def test_export_results_excel(self, mock_to_excel):
        """测试Excel导出"""
        data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        export_results(data, 'results.xlsx', format='excel')
        
        mock_to_excel.assert_called_once_with('results.xlsx', index=False)
    
    def test_export_results_unsupported(self):
        """测试不支持的导出格式"""
        data = pd.DataFrame({'A': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="不支持的导出格式"):
            export_results(data, 'results.txt', format='txt')
    
    @patch('builtins.open', new_callable=lambda: MagicMock())
    @patch('my_python_project.data_analysis.basic_statistics')
    @patch('my_python_project.data_analysis.validate_data_quality')
    def test_generate_report(self, mock_quality, mock_stats, mock_open):
        """测试报告生成"""
        # 模拟数据和函数返回值
        data = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        
        mock_quality.return_value = {
            'total_rows': 5,
            'total_columns': 1,
            'missing_percentage': 0.0,
            'duplicate_percentage': 0.0
        }
        
        mock_stats.return_value = {
            'A': {'mean': 3.0, 'std': 1.58, 'min': 1, 'max': 5}
        }
        
        # 配置mock文件对象
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        generate_report(data, 'report.txt')
        
        # 验证文件被打开和写入
        mock_open.assert_called_once_with('report.txt', 'w', encoding='utf-8')
        assert mock_file.write.call_count > 0
        
        # 验证调用了分析函数
        mock_quality.assert_called_once_with(data)
        mock_stats.assert_called_once_with(data)


class TestIntegration:
    """集成测试"""
    
    @patch('my_python_project.data_analysis.load_data')
    @patch('my_python_project.data_analysis.export_results')
    def test_complete_analysis_workflow(self, mock_export, mock_load):
        """测试完整的分析工作流"""
        # 模拟加载数据
        test_data = pd.DataFrame({
            'sales': [100, 150, 120, 200, 180],
            'profit': [20, 30, 25, 40, 35],
            'region': ['A', 'B', 'A', 'C', 'B']
        })
        mock_load.return_value = test_data
        
        # 执行分析流程
        data = load_data('test.csv')
        cleaned_data = clean_data(data)
        stats = basic_statistics(cleaned_data)
        quality = validate_data_quality(cleaned_data)
        
        # 验证结果
        assert isinstance(cleaned_data, pd.DataFrame)
        assert isinstance(stats, dict)
        assert isinstance(quality, dict)
        
        # 验证数据质量
        assert quality['total_rows'] == 5
        assert quality['missing_percentage'] == 0.0
        
        # 验证统计结果
        assert 'sales' in stats
        assert 'profit' in stats
        assert stats['sales']['mean'] == 150.0


if __name__ == "__main__":
    pytest.main([__file__])