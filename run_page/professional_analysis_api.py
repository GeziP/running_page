"""
Professional Running Analysis API
专业跑步分析API

提供基于权威理论的跑步数据分析服务
"""

from flask import Flask, request, jsonify
from run_page.analysis.professional_analyzer import ProfessionalAnalyzer
import json
from datetime import datetime
from typing import Dict, Any


def create_professional_analysis_api(app: Flask):
    """创建专业分析API路由"""
    
    analyzer = ProfessionalAnalyzer()
    
    @app.route('/api/professional-analysis/vdot', methods=['POST'])
    def calculate_vdot():
        """计算VDOT值和训练配速"""
        try:
            data = request.get_json()
            distance_km = float(data.get('distance', 0))
            time_seconds = int(data.get('time_seconds', 0))
            
            if distance_km <= 0 or time_seconds <= 0:
                return jsonify({'error': '距离和时间必须大于0'}), 400
            
            # 计算VDOT
            vdot = analyzer.vdot_calc.calculate_vdot_from_race(distance_km, time_seconds)
            
            # 获取训练配速
            training_paces = analyzer.vdot_calc.get_training_paces(vdot)
            
            # 预测比赛时间
            race_predictions = analyzer.vdot_calc.predict_race_times(vdot)
            
            # 分类健身水平
            fitness_level = analyzer._classify_fitness_level(vdot)
            
            return jsonify({
                'vdot': vdot,
                'fitness_level': fitness_level,
                'training_paces': training_paces,
                'race_predictions': race_predictions,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': f'计算错误: {str(e)}'}), 500
    
    @app.route('/api/professional-analysis/maf', methods=['POST'])
    def calculate_maf():
        """计算MAF心率和训练区间"""
        try:
            data = request.get_json()
            age = int(data.get('age', 0))
            health_category = data.get('health_category', 'healthy')
            
            if age <= 0 or age > 100:
                return jsonify({'error': '年龄必须在1-100之间'}), 400
            
            # 计算MAF心率
            maf_hr = analyzer.maf_calc.calculate_maf_heart_rate(age, health_category)
            
            # 获取心率区间
            hr_zones = analyzer.maf_calc.get_heart_rate_zones(maf_hr)
            
            return jsonify({
                'maf_heart_rate': maf_hr,
                'training_zones': hr_zones,
                'recommendation': f"大部分训练应保持在{maf_hr-10}-{maf_hr}心率区间",
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': f'计算错误: {str(e)}'}), 500
    
    @app.route('/api/professional-analysis/tss', methods=['POST'])
    def calculate_tss():
        """计算训练压力评分"""
        try:
            data = request.get_json()
            duration_minutes = float(data.get('duration_minutes', 0))
            avg_pace_per_km = int(data.get('avg_pace_per_km', 0))
            threshold_pace_per_km = int(data.get('threshold_pace_per_km', 0))
            
            if duration_minutes <= 0:
                return jsonify({'error': '训练时长必须大于0'}), 400
            
            # 计算TSS
            tss = analyzer.tss_calc.calculate_running_tss(
                duration_minutes, avg_pace_per_km, threshold_pace_per_km
            )
            
            # 评估训练负荷
            if tss < 50:
                interpretation = '轻松训练'
                advice = '适合恢复日或技术训练'
            elif tss < 100:
                interpretation = '中等强度训练'
                advice = '标准训练强度，可以每天进行'
            elif tss < 200:
                interpretation = '高强度训练'
                advice = '需要1-2天恢复时间'
            else:
                interpretation = '极高强度训练'
                advice = '需要2-3天恢复时间，谨慎安排'
            
            return jsonify({
                'tss': tss,
                'interpretation': interpretation,
                'training_advice': advice,
                'intensity_factor': threshold_pace_per_km / avg_pace_per_km if avg_pace_per_km > 0 else 0,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': f'计算错误: {str(e)}'}), 500
    
    @app.route('/api/professional-analysis/comprehensive', methods=['POST'])
    def comprehensive_analysis():
        """综合专业分析"""
        try:
            data = request.get_json()
            age = int(data.get('age', 0))
            race_distance = float(data.get('race_distance', 0))
            race_time = int(data.get('race_time', 0))
            health_status = data.get('health_status', 'healthy')
            
            if age <= 0 or race_distance <= 0 or race_time <= 0:
                return jsonify({'error': '所有参数必须大于0'}), 400
            
            # 生成综合分析报告
            analysis_result = analyzer.analyze_runner_profile(
                age, race_distance, race_time, health_status
            )
            
            return jsonify(analysis_result)
            
        except Exception as e:
            return jsonify({'error': f'分析错误: {str(e)}'}), 500
    
    @app.route('/api/professional-analysis/training-load', methods=['POST'])
    def analyze_training_load():
        """分析训练负荷趋势"""
        try:
            data = request.get_json()
            activities = data.get('activities', [])
            
            if not activities:
                return jsonify({'error': '活动数据不能为空'}), 400
            
            # 分析训练负荷
            load_analysis = analyzer.analyze_training_load(activities)
            
            return jsonify(load_analysis)
            
        except Exception as e:
            return jsonify({'error': f'分析错误: {str(e)}'}), 500
    
    @app.route('/api/professional-analysis/theory', methods=['GET'])
    def get_theory_info():
        """获取理论基础信息"""
        theory_info = {
            'vdot': {
                'name': 'VDOT训练系统',
                'developer': 'Jack Daniels博士',
                'description': '基于VO2max的跑步训练配速计算系统',
                'benefits': [
                    '精确的训练配速指导',
                    '科学的能力评估',
                    '比赛成绩预测'
                ]
            },
            'maf': {
                'name': 'MAF 180心率训练法',
                'developer': 'Phil Maffetone博士',
                'description': '最大有氧心率训练法，强调有氧基础建设',
                'benefits': [
                    '提高脂肪燃烧效率',
                    '减少受伤风险',
                    '建立强大有氧基础'
                ]
            },
            'tss': {
                'name': '训练压力评分系统',
                'developer': 'TrainingPeaks / Dr. Andrew Coggan',
                'description': '量化训练负荷和恢复需求的科学系统',
                'benefits': [
                    '客观量化训练强度',
                    '科学安排恢复时间',
                    '预防过度训练'
                ]
            }
        }
        
        return jsonify(theory_info)
    
    @app.route('/api/professional-analysis/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'healthy',
            'message': '专业分析API运行正常',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })


def register_professional_analysis_routes(app: Flask):
    """注册专业分析路由到Flask应用"""
    create_professional_analysis_api(app) 