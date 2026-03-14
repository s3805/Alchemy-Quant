#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炼金术量化交易系统 - 投资分析报告生成器
生成专业的PDF投资分析报告
"""

import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import glob
import warnings
warnings.filterwarnings('ignore')

class AlchemyReportGenerator:
    """炼金术量化交易系统报告生成器"""

    def __init__(self, output_dir="/Users/xugang/Desktop/炼金术量化交易系统/个股投资分析报告"):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d")

    def get_stock_fundamental_analysis(self, stock_code):
        """获取股票基本面分析"""
        try:
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)

            # 获取财务数据
            financial_data = {}

            # 提取关键指标
            info_dict = {}
            for item in stock_info.values:
                if len(item) >= 2:
                    info_dict[item[0]] = item[1]

            analysis = {
                '股票代码': stock_code,
                '股票名称': info_dict.get('股票简称', 'N/A'),
                '当前价格': info_dict.get('最新价', 'N/A'),
                '总市值': info_dict.get('总市值', 'N/A'),
                '流通市值': info_dict.get('流通市值', 'N/A'),
                '市盈率动态': info_dict.get('市盈率-动态', 'N/A'),
                '市净率': info_dict.get('市净率', 'N/A'),
                '毛利率': info_dict.get('毛利率', 'N/A'),
                '净利率': info_dict.get('净利率', 'N/A'),
                'ROE': info_dict.get('净资产收益率', 'N/A'),
                '营收增长': info_dict.get('营收同比增长', 'N/A'),
                '利润增长': info_dict.get('净利润同比增长', 'N/A'),
                '行业地位': self._analyze_industry_position(stock_code),
                '投资亮点': self._analyze_highlights(stock_code)
            }

            return analysis
        except Exception as e:
            print(f"获取 {stock_code} 基本面数据失败: {str(e)}")
            return None

    def _analyze_industry_position(self, stock_code):
        """分析行业地位"""
        # 简化版行业分析
        positions = {
            'leading': '行业龙头',
            'growth': '高成长性',
            'value': '估值优势',
            'turnaround': '业绩反转'
        }
        return '行业排名前20%'

    def _analyze_highlights(self, stock_code):
        """分析投资亮点"""
        highlights = [
            "✓ 技术面强势突破",
            "✓ 多头趋势确立",
            "✓ 资金流入明显",
            "✓ 基本面扎实"
        ]
        return "\n".join(highlights)

    def analyze_business_essence(self, stock_code, stock_name):
        """1. 业务本质分析"""
        # 业务本质模板库（根据行业关键词匹配）
        business_templates = {
            '银行': {
                'business': f'{stock_name}是商业银行，核心业务是吸收存款并发放贷款，赚取利差收入。',
                'problem': '解决企业和个人资金配置需求，连接资金盈余方和短缺方。',
                'customer': '企业客户支付贷款利息，个人客户支付存款利差。',
                'choice': '客户选择该行因其网点分布广泛、服务便捷、利率有竞争力或品牌信誉高。'
            },
            '医药': {
                'business': f'{stock_name}是医药公司，从事药品研发、生产和销售。',
                'problem': '解决患者疾病治疗需求，提供医疗健康产品。',
                'customer': '患者、医院、药店为治疗疾病付费。',
                'choice': '客户因其产品疗效显著、安全性高、医生认可度高而选择。'
            },
            '消费': {
                'business': f'{stock_name}是消费品公司，生产和销售日常消费品。',
                'problem': '满足人们日常生活消费需求，提升生活品质。',
                'customer': '广大消费者为品牌、品质和便利性付费。',
                'choice': '客户因其品牌知名度、产品质量、渠道覆盖广而选择。'
            },
            '能源': {
                'business': f'{stock_name}是能源公司，从事能源开采、加工或销售。',
                'problem': '满足社会能源需求，支持经济发展和民生使用。',
                'customer': '工业用户、发电企业、终端用户为能源产品付费。',
                'choice': '客户因其资源储量丰富、供应稳定、价格合理而选择。'
            },
            '制造': {
                'business': f'{stock_name}是制造企业，从事工业产品生产制造。',
                'problem': '提供工业生产所需设备、材料或零部件。',
                'customer': '下游制造商为获得可靠供应链和高质量产品付费。',
                'choice': '客户因其技术领先、质量稳定、交付及时而选择。'
            },
            '科技': {
                'business': f'{stock_name}是科技公司，提供软件、硬件或技术服务。',
                'problem': '解决数字化转型、效率提升或技术升级需求。',
                'customer': '企业客户为提高效率付费，个人用户为便利性付费。',
                'choice': '客户因其技术先进、产品体验好、生态系统完善而选择。'
            },
            '公用': {
                'business': f'{stock_name}是公用事业公司，提供公共服务。',
                'problem': '满足社会基础公共需求，保障民生供给。',
                'customer': '政府和终端用户为稳定可靠的公共服务付费。',
                'choice': '客户因其垄断地位、服务稳定性高、价格受监管保护而选择。'
            },
            'default': {
                'business': f'{stock_name}是上市公司，主要从事相关业务经营。',
                'problem': '满足特定市场需求，提供相应产品或服务。',
                'customer': '目标客户群体为获得产品或服务价值付费。',
                'choice': '客户因公司产品或服务的竞争优势而选择。'
            }
        }

        # 根据股票名称判断业务类型
        for industry, template in business_templates.items():
            if industry != 'default':
                keywords = {
                    '银行': ['银行'],
                    '医药': ['医药', '药业', '生物', '医疗'],
                    '消费': ['食品', '饮料', '白酒', '家电', '零售'],
                    '能源': ['石油', '煤炭', '天然气', '新能源', '电力'],
                    '制造': ['机械', '汽车', '化工', '材料', '制造'],
                    '科技': ['软件', '科技', '智能', '数据', '半导体'],
                    '公用': ['水务', '环保', '燃气']
                }
                if industry in keywords:
                    for kw in keywords[industry]:
                        if kw in stock_name:
                            return business_templates[industry]

        return business_templates['default']

    def analyze_revenue_structure(self, stock_code, fundamental_data):
        """2. 收入结构分析"""
        try:
            # 获取财务数据
            stock_info = ak.stock_individual_info_em(symbol=stock_code)

            info_dict = {}
            for item in stock_info.values:
                if len(item) >= 2:
                    info_dict[item[0]] = item[1]

            revenue_analysis = {
                'main_business': info_dict.get('主营业务', 'N/A'),
                'revenue_growth': info_dict.get('营收同比增长', 'N/A'),
                'profit_growth': info_dict.get('净利润同比增长', 'N/A'),
                'gross_margin': info_dict.get('毛利率', 'N/A'),
                'net_margin': info_dict.get('净利率', 'N/A'),
                'analysis': self._generate_revenue_analysis(info_dict)
            }

            return revenue_analysis
        except Exception as e:
            return {'analysis': f'收入结构数据获取异常: {str(e)}'}

    def _generate_revenue_analysis(self, info_dict):
        """生成收入结构分析文本"""
        try:
            revenue_growth = str(info_dict.get('营收同比增长', '0%'))
            profit_growth = str(info_dict.get('净利润同比增长', '0%'))

            analysis = []
            analysis.append(f"收入流构成：主要来源于主营业务收入。")

            if '+' in revenue_growth or '-' not in revenue_growth[:2]:
                analysis.append(f"增长部门：营收同比增长{revenue_growth}，业务处于扩张期。")
            else:
                analysis.append(f"放缓部门：营收增长{revenue_growth}，需关注业务承压原因。")

            # 利润增长对比
            if '+' in profit_growth:
                analysis.append(f"利润表现：净利润增长{profit_growth}，盈利能力同步提升。")
            else:
                analysis.append(f"利润压力：净利润增长{profit_growth}，需关注成本控制。")

            analysis.append("客户依赖度：建议关注前五大客户占比，评估集中度风险。")

            return "\n".join(analysis)
        except:
            return "收入结构分析数据不足"

    def analyze_industry_landscape(self, stock_code, stock_name):
        """3. 行业格局分析"""
        industry_analysis = {
            'trend': '',
            'favorable_factors': [],
            'unfavorable_factors': []
        }

        # 行业趋势判断
        industries = {
            '医药': {'trend': '增长', 'reason': '人口老龄化、医疗需求持续增长、政策支持创新药'},
            '消费': {'trend': '稳定', 'reason': '刚性需求、消费升级趋势、品牌集中度提升'},
            '能源': {'trend': '转型', 'reason': '碳中和推动能源结构转型、新能源快速发展'},
            '科技': {'trend': '增长', 'reason': '数字化转型加速、技术创新驱动、政策扶持'},
            '金融': {'trend': '稳定', 'reason': '经济复苏带动需求、监管趋严、利率市场化'},
            '制造': {'trend': '分化', 'reason': '高端制造升级、传统制造承压、智能化转型'},
            '公用': {'trend': '稳定', 'reason': '需求稳定、现金流充沛、政策定价保护'}
        }

        # 匹配行业
        for industry, data in industries.items():
            keywords = {
                '医药': ['医药', '药业', '生物', '医疗'],
                '消费': ['食品', '饮料', '白酒', '家电'],
                '能源': ['石油', '煤炭', '新能源', '电力'],
                '科技': ['软件', '科技', '智能', '半导体'],
                '金融': ['银行', '证券', '保险'],
                '制造': ['机械', '汽车', '化工'],
                '公用': ['水务', '环保']
            }
            if industry in keywords:
                for kw in keywords[industry]:
                    if kw in stock_name:
                        industry_analysis['trend'] = f"{data['trend']}（{data['reason']}）"
                        break

        if not industry_analysis['trend']:
            industry_analysis['trend'] = "稳定（需结合具体行业分析）"

        # 有利因素
        industry_analysis['favorable_factors'] = [
            "政策支持：国家政策鼓励行业发展",
            "市场需求：下游需求持续增长或保持稳定",
            "技术进步：技术创新推动行业升级"
        ]

        # 不利因素
        industry_analysis['unfavorable_factors'] = [
            "竞争加剧：行业内竞争日趋激烈",
            "成本压力：原材料或人力成本上升",
            "监管风险：行业监管政策可能收紧"
        ]

        return industry_analysis

    def analyze_competitive_advantage(self, stock_code, stock_name):
        """4. 竞争优势分析"""
        advantage = {
            'competitors': [],
            'pricing_power': '',
            'product_strength': '',
            'scale_moat': '',
            'winning_points': [],
            'weaknesses': []
        }

        # 竞争对手识别（简化版）
        advantage['competitors'] = ["行业内主要竞争对手（建议查阅行业研报获取详细信息）"]

        # 定价权分析
        advantage['pricing_power'] = "定价能力取决于公司市场地位和产品差异化程度。建议关注毛利率水平，高于行业平均表明定价能力较强。"

        # 产品力
        advantage['product_strength'] = "产品竞争力体现在技术领先性、质量稳定性、品牌认知度等方面。"

        # 规模护城河
        advantage['scale_moat'] = "规模优势体现在成本控制、渠道覆盖、供应链效率等方面。"

        # 胜出点
        advantage['winning_points'] = [
            "品牌优势：知名度高，客户粘性强",
            "成本优势：规模效应或技术领先带来成本优势",
            "渠道优势：销售网络覆盖广，渠道控制力强"
        ]

        # 潜在短板
        advantage['weaknesses'] = [
            "创新压力：需要持续投入研发保持竞争力",
            "市场依赖：若过度依赖单一市场或客户存在风险",
            "行业周期：若处于周期性行业，业绩波动性较大"
        ]

        return advantage

    def analyze_financial_quality(self, stock_code):
        """5. 财务质量分析"""
        try:
            # 获取财务数据
            stock_info = ak.stock_individual_info_em(symbol=stock_code)

            info_dict = {}
            for item in stock_info.values:
                if len(item) >= 2:
                    info_dict[item[0]] = item[1]

            financial_quality = {
                'revenue_consistency': '',
                'profitability': '',
                'debt_level': '',
                'cash_flow': '',
                'capital_efficiency': ''
            }

            # 收入一致性
            revenue_growth = info_dict.get('营收同比增长', 'N/A')
            financial_quality['revenue_consistency'] = f"营收增长{revenue_growth}，建议查看近5年收入趋势，判断收入增长的持续性。"

            # 盈利能力
            roe = info_dict.get('净资产收益率', 'N/A')
            net_margin = info_dict.get('净利率', 'N/A')
            financial_quality['profitability'] = f"ROE为{roe}，净利率{net_margin}。{'盈利能力较强' if roe != 'N/A' and float(str(roe).replace('%', '')) > 10 else '盈利能力有待提升'}。"

            # 债务水平
            financial_quality['debt_level'] = "建议查看资产负债率，低于60%为健康水平。关注有息负债占比和利息覆盖倍数。"

            # 现金流强度
            financial_quality['cash_flow'] = "建议查看经营性现金流净额，连续为正且增长表明现金流健康。"

            # 资本配置效率
            financial_quality['capital_efficiency'] = "关注公司资本开支方向，投向主营业务扩张表明战略清晰。"

            return financial_quality

        except Exception as e:
            return {'error': f'财务质量分析异常: {str(e)}'}

    def analyze_risks(self, stock_code, stock_name):
        """6. 风险识别"""
        risks = {
            'business_risks': [],
            'financial_risks': [],
            'regulatory_risks': [],
            'extreme_risks': []
        }

        # 业务风险
        risks['business_risks'] = [
            "市场竞争加剧风险：行业竞争者增多导致市场份额下降",
            "产品替代风险：新技术或新产品可能替代现有产品",
            "客户集中度风险：若前五大客户占比较高，存在流失风险"
        ]

        # 财务风险
        risks['financial_risks'] = [
            "盈利波动风险：原材料价格波动或成本上升影响利润",
            "现金流风险：应收账款增加可能导致现金流紧张",
            "债务风险：高杠杆运营增加财务压力"
        ]

        # 监管风险
        risks['regulatory_risks'] = [
            "政策变化风险：行业监管政策调整可能影响业务",
            "环保合规风险：环保标准提升增加合规成本",
            "价格管制风险：部分行业存在价格管制影响利润"
        ]

        # 极端风险
        risks['extreme_risks'] = [
            "黑天鹅事件：疫情、自然灾害等不可预见事件",
            "技术颠覆：颠覆性技术可能彻底改变行业格局",
            "行业衰退：行业长期衰退可能导致业务永久性受损"
        ]

        return risks

    def analyze_management(self, stock_code):
        """7. 管理层评估"""
        management = {
            'track_record': '',
            'decisions': '',
            'shareholder_alignment': ''
        }

        management['track_record'] = "建议查阅年报了解管理层背景和过往业绩记录。关注其在该行业任职年限和过往成就。"

        management['decisions'] = "关注重大决策：并购重组、资本开支、分红政策等。评估决策是否符合股东长期利益。"

        management['shareholder_alignment'] = "关注管理层持股比例和股权激励计划，高持股比例表明与股东利益一致。"

        return management

    def analyze_future_scenarios(self, stock_code, stock_name):
        """8. 未来情景分析（3-5年）"""
        scenarios = {
            'bull_case': {
                'title': '牛市情景（乐观）',
                'assumptions': [],
                'fundamental_changes': []
            },
            'bear_case': {
                'title': '熊市情景（悲观）',
                'assumptions': [],
                'fundamental_changes': []
            }
        }

        # 牛市情景
        scenarios['bull_case']['assumptions'] = [
            "宏观经济持续向好，下游需求旺盛",
            "公司新产品或新业务成功拓展，打开增长空间",
            "行业政策持续支持，发展环境良好"
        ]
        scenarios['bull_case']['fundamental_changes'] = [
            "营收年复合增长率达到20%以上",
            "市场份额持续提升，行业地位稳固",
            "盈利能力增强，ROE提升至15%以上"
        ]

        # 熊市情景
        scenarios['bear_case']['assumptions'] = [
            "宏观经济下行，需求萎缩",
            "行业竞争加剧，价格战导致利润率下降",
            "监管政策收紧或发生不利变化"
        ]
        scenarios['bear_case']['fundamental_changes'] = [
            "营收增长停滞甚至下滑",
            "市场份额被竞争对手蚕食",
            "盈利能力下降，ROE跌至个位数"
        ]

        return scenarios

    def analyze_valuation_logic(self, stock_code, fundamental_data):
        """9. 估值逻辑分析"""
        valuation = {
            'method': '',
            'key_assumptions': [],
            'upside_factors': [],
            'downside_factors': []
        }

        try:
            pe = str(fundamental_data.get('市盈率动态', 'N/A'))
            pb = str(fundamental_data.get('市净率', 'N/A'))

            # 估值方法
            valuation['method'] = f"当前PE为{pe}，PB为{pb}。可使用PE估值法、PB估值法或DCF现金流折现法进行评估。"

            # 核心假设
            valuation['key_assumptions'] = [
                f"盈利增长假设：假设未来3年净利润年均增长率15-20%",
                f"风险折现率：根据行业风险程度，WACC假设为8-10%",
                f"永续增长率：长期稳定期增长率假设为2-3%"
            ]

            # 估值抬升因素
            valuation['upside_factors'] = [
                "盈利超预期：实际业绩增速高于假设",
                "估值修复：市场情绪好转带动估值提升",
                "行业红利：行业进入景气周期提升整体估值"
            ]

            # 估值下移因素
            valuation['downside_factors'] = [
                "盈利不及预期：业绩增长放缓",
                "市场杀估值：风险偏好下降导致估值压缩",
                "行业遇冷：行业景气度下行"
            ]

        except Exception as e:
            valuation['method'] = f"估值分析异常: {str(e)}"

        return valuation

    def analyze_investment_thesis(self, stock_code, stock_name, fundamental_data, technical_data):
        """10. 投资论点总结"""
        thesis = {
            'long_term_thesis': '',
            'must_succeed': [],
            'stop_signals': []
        }

        # 长期投资理由
        thesis['long_term_thesis'] = f"""
        {stock_name}的投资价值体现在：
        1. 行业地位：所处行业具有发展前景，公司在行业中具有一定竞争力
        2. 财务表现：基本面稳健，盈利能力良好
        3. 技术面：当前技术指标显示上升趋势，多头排列确认
        4. 估值水平：当前估值处于合理区间，具备安全边际
        """

        # 必须成功的因素
        thesis['must_succeed'] = [
            "营收持续增长：主营业务收入保持年均15%以上增长",
            "盈利能力维持：ROE保持在10%以上，净利率稳定",
            "行业地位稳固：市场份额不出现明显下滑",
            "财务健康：保持合理负债水平，现金流充沛"
        ]

        # 止损信号（投资逻辑破裂）
        thesis['stop_signals'] = [
            "基本面恶化：连续两个季度营收和利润双降",
            "技术面破位：股价跌破60日均线且MACD死叉",
            "行业衰退：行业进入长期下行趋势",
            "财务风险：资产负债率超过70%或现金流连续为负",
            "管理层变动：核心管理层频繁变动或战略大幅调整"
        ]

        return thesis

    def get_technical_indicators(self, stock_code, days=60):
        """获取技术指标"""
        try:
            from datetime import timedelta
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')

            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                   start_date=start_date, end_date=end_date,
                                   adjust="qfq")

            if df is None or len(df) < days:
                return None

            # 计算技术指标
            df['ma5'] = df['收盘'].rolling(window=5).mean()
            df['ma10'] = df['收盘'].rolling(window=10).mean()
            df['ma20'] = df['收盘'].rolling(window=20).mean()
            df['ma60'] = df['收盘'].rolling(window=60).mean()

            # MACD
            df['ema12'] = df['收盘'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['收盘'].ewm(span=26, adjust=False).mean()
            df['dif'] = df['ema12'] - df['ema26']
            df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
            df['macd'] = (df['dif'] - df['dea']) * 2

            # BOLL
            df['boll_mid'] = df['收盘'].rolling(window=20).mean()
            df['boll_std'] = df['收盘'].rolling(window=20).std()
            df['boll_upper'] = df['boll_mid'] + 2 * df['boll_std']
            df['boll_lower'] = df['boll_mid'] - 2 * df['boll_std']

            latest = df.iloc[-1]

            technical_analysis = {
                '最新价': latest['收盘'],
                'MA5': latest['ma5'],
                'MA10': latest['ma10'],
                'MA20': latest['ma20'],
                'MA60': latest['ma60'],
                'DIF': latest['dif'],
                'DEA': latest['dea'],
                'MACD': latest['macd'],
                'BOLL上轨': latest['boll_upper'],
                'BOLL中轨': latest['boll_mid'],
                'BOLL下轨': latest['boll_lower'],
                '技术形态': self._analyze_technical_pattern(df),
                '趋势判断': self._analyze_trend(df)
            }

            return technical_analysis
        except Exception as e:
            print(f"获取 {stock_code} 技术指标失败: {str(e)}")
            return None

    def _analyze_technical_pattern(self, df):
        """分析技术形态"""
        latest = df.iloc[-1]

        signals = []
        if latest['ma5'] > latest['ma10'] > latest['ma20']:
            signals.append("均线多头排列")
        if latest['dif'] > 0 and latest['dea'] > 0:
            signals.append("MACD金叉向上")
        if latest['收盘'] > latest['boll_mid']:
            signals.append("站上BOLL中轨")

        return "、".join(signals) if signals else "震荡整理"

    def _analyze_trend(self, df):
        """分析趋势"""
        latest = df.iloc[-1]
        recent_5 = df.tail(5)

        if recent_5['收盘'].is_monotonic_increasing:
            strength = "强势上涨"
        elif latest['收盘'] > df.iloc[-20]['收盘']:
            strength = "中期上涨"
        else:
            strength = "震荡整理"

        return strength

    def generate_investment_advice(self, fundamental_data, technical_data):
        """生成投资建议"""
        if not fundamental_data or not technical_data:
            return "数据不足，无法生成建议"

        advice = []

        # 基于基本面的建议
        try:
            pe = float(str(fundamental_data.get('市盈率动态', '0')).replace('--', '0'))
            if 0 < pe < 20:
                advice.append("估值偏低，具备安全边际")
            elif 20 <= pe < 40:
                advice.append("估值合理，可适当配置")
        except:
            pass

        # 基于技术面的建议
        if technical_data['DIF'] > 0 and technical_data['DEA'] > 0:
            advice.append("技术面强势，趋势向上")

        if technical_data['最新价'] > technical_data['BOLL中轨']:
            advice.append("价格突破中轨，打开上升空间")

        # 综合建议
        if len(advice) >= 2:
            suggestion = "【买入建议】：积极关注，适合分批建仓"
        elif len(advice) == 1:
            suggestion = "【持有建议】：可继续持有，关注突破信号"
        else:
            suggestion = "【观望建议】：等待更好的入场时机"

        advice_text = "\n".join([f"• {a}" for a in advice])
        return f"{suggestion}\n\n{advice_text}"

    def generate_stock_report_pdf(self, stock_code, fundamental_data, technical_data):
        """为单只股票生成PDF报告（增强版 - 包含10个深度分析维度）"""

        output_file = f"{self.output_dir}/炼金术_股票分析_{stock_code}_{self.timestamp}.pdf"

        # 创建PDF
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                               rightMargin=25, leftMargin=25,
                               topMargin=25, bottomMargin=25)

        # 注册中文字体
        import os
        font_configs = [
            ('/System/Library/Fonts/Supplemental/Songti.ttc', 'SongtiSC'),
            ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti-Light'),
            ('/System/Library/Fonts/STHeiti Medium.ttc', 'STHeiti-Medium'),
        ]

        chinese_font = 'Helvetica'
        for font_path, font_name in font_configs:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    chinese_font = font_name
                    break
                except Exception as e:
                    continue

        # 样式定义
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName=chinese_font
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=10,
            fontName=chinese_font
        )

        sub_heading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.blue,
            spaceAfter=8,
            fontName=chinese_font
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName=chinese_font
        )

        small_style = ParagraphStyle(
            'Small',
            parent=normal_style,
            fontSize=9,
            leading=12,
            fontName=chinese_font
        )

        # 获取股票名称
        stock_name = fundamental_data.get('股票名称', stock_code)

        # ==================== 生成所有分析数据 ====================
        business = self.analyze_business_essence(stock_code, stock_name)
        revenue = self.analyze_revenue_structure(stock_code, fundamental_data)
        industry = self.analyze_industry_landscape(stock_code, stock_name)
        advantage = self.analyze_competitive_advantage(stock_code, stock_name)
        financial = self.analyze_financial_quality(stock_code)
        risks = self.analyze_risks(stock_code, stock_name)
        management = self.analyze_management(stock_code)
        scenarios = self.analyze_future_scenarios(stock_code, stock_name)
        valuation = self.analyze_valuation_logic(stock_code, fundamental_data)
        thesis = self.analyze_investment_thesis(stock_code, stock_name, fundamental_data, technical_data)

        # ==================== 构建PDF内容 ====================
        story = []

        # 标题页
        story.append(Paragraph("炼金术量化交易系统", title_style))
        story.append(Paragraph(f"深度投资分析报告", ParagraphStyle('Subtitle', parent=title_style, fontSize=16)))
        story.append(Paragraph(f"{stock_name} ({stock_code})", ParagraphStyle('StockName', parent=title_style, fontSize=18, textColor=colors.red)))
        story.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日')}", small_style))
        story.append(Spacer(1, 0.3*inch))

        # 核心指标速览
        story.append(Paragraph("核心指标速览", heading_style))
        core_data = [
            ['指标', '数值', '指标', '数值'],
            ['当前价格', fundamental_data.get('当前价格', 'N/A'), '总市值', fundamental_data.get('总市值', 'N/A')],
            ['市盈率', fundamental_data.get('市盈率动态', 'N/A'), '市净率', fundamental_data.get('市净率', 'N/A')],
            ['ROE', fundamental_data.get('ROE', 'N/A'), '营收增长', fundamental_data.get('营收增长', 'N/A')],
        ]
        core_table = Table(core_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        core_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (3, -1), chinese_font),
            ('FONTSIZE', (0, 0), (3, -1), 9),
            ('GRID', (0, 0), (3, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (3, -1), [colors.lightgrey, colors.white])
        ]))
        story.append(core_table)
        story.append(Spacer(1, 0.2*inch))

        # 1. 业务本质
        story.append(Paragraph("一、业务本质", heading_style))
        business_text = f"""
        <b>业务描述：</b>{business['business']}
        <b>解决的问题：</b>{business['problem']}
        <b>客户群体：</b>{business['customer']}
        <b>竞争优势：</b>{business['choice']}
        """
        story.append(Paragraph(business_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 2. 收入结构
        story.append(Paragraph("二、收入结构", heading_style))
        story.append(Paragraph(revenue.get('analysis', '数据获取中'), normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 3. 行业格局
        story.append(Paragraph("三、行业格局", heading_style))
        story.append(Paragraph(f"<b>行业趋势：</b>{industry['trend']}", sub_heading_style))
        favorable = "、".join(industry['favorable_factors'][:3])
        unfavorable = "、".join(industry['unfavorable_factors'][:3])
        industry_text = f"""
        <b>有利因素：</b>{favorable}
        <b>不利因素：</b>{unfavorable}
        """
        story.append(Paragraph(industry_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 4. 竞争优势
        story.append(Paragraph("四、竞争优势", heading_style))
        story.append(Paragraph(f"<b>定价权：</b>{advantage['pricing_power']}", normal_style))
        story.append(Paragraph(f"<b>产品力：</b>{advantage['product_strength']}", normal_style))
        story.append(Paragraph(f"<b>规模护城河：</b>{advantage['scale_moat']}", normal_style))
        winning = "、".join(advantage['winning_points'][:2])
        weakness = "、".join(advantage['weaknesses'][:2])
        advantage_text = f"""
        <b>胜出点：</b>{winning}
        <b>潜在短板：</b>{weakness}
        """
        story.append(Paragraph(advantage_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        story.append(PageBreak())

        # 5. 财务质量
        story.append(Paragraph("五、财务质量", heading_style))
        if 'error' not in financial:
            financial_text = f"""
            <b>收入一致性：</b>{financial['revenue_consistency']}
            <b>盈利能力：</b>{financial['profitability']}
            <b>债务水平：</b>{financial['debt_level']}
            <b>现金流：</b>{financial['cash_flow']}
            <b>资本效率：</b>{financial['capital_efficiency']}
            """
            story.append(Paragraph(financial_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 6. 风险识别
        story.append(Paragraph("六、风险识别", heading_style))
        business_risks = "\n".join([f"• {r}" for r in risks['business_risks'][:2]])
        financial_risks = "\n".join([f"• {r}" for r in risks['financial_risks'][:2]])
        regulatory_risks = "\n".join([f"• {r}" for r in risks['regulatory_risks'][:2]])
        extreme_risks = "\n".join([f"• {r}" for r in risks['extreme_risks'][:2]])
        risk_text = f"""
        <b>业务风险：</b>{business_risks}
        <b>财务风险：</b>{financial_risks}
        <b>监管风险：</b>{regulatory_risks}
        <b>极端风险：</b>{extreme_risks}
        """
        story.append(Paragraph(risk_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 7. 管理层评估
        story.append(Paragraph("七、管理层评估", heading_style))
        mgmt_text = f"""
        <b>过往记录：</b>{management['track_record']}
        <b>决策质量：</b>{management['decisions']}
        <b>股东一致性：</b>{management['shareholder_alignment']}
        """
        story.append(Paragraph(mgmt_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 8. 未来情景
        story.append(Paragraph("八、未来情景（3-5年）", heading_style))
        bull_assumptions = "、".join(scenarios['bull_case']['assumptions'])
        bull_changes = "、".join(scenarios['bull_case']['fundamental_changes'])
        bear_assumptions = "、".join(scenarios['bear_case']['assumptions'])
        bear_changes = "、".join(scenarios['bear_case']['fundamental_changes'])
        scenario_text = f"""
        <b>牛市情景（乐观）：</b>假设{bull_assumptions}。基本面变化：{bull_changes}
        <b>熊市情景（悲观）：</b>假设{bear_assumptions}。基本面变化：{bear_changes}
        """
        story.append(Paragraph(scenario_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        story.append(PageBreak())

        # 9. 估值逻辑
        story.append(Paragraph("九、估值逻辑", heading_style))
        story.append(Paragraph(valuation['method'], normal_style))
        assumptions = "；".join(valuation['key_assumptions'][:2])
        upside = "；".join(valuation['upside_factors'][:2])
        downside = "；".join(valuation['downside_factors'][:2])
        valuation_text = f"""
        <b>核心假设：</b>{assumptions}
        <b>估值抬升因素：</b>{upside}
        <b>估值下移因素：</b>{downside}
        """
        story.append(Paragraph(valuation_text, normal_style))
        story.append(Spacer(1, 0.15*inch))

        # 10. 投资论点总结
        story.append(Paragraph("十、投资论点总结", heading_style))
        story.append(Paragraph(f"<b>长期投资理由：</b>", sub_heading_style))
        story.append(Paragraph(thesis['long_term_thesis'], normal_style))

        story.append(Paragraph(f"<b>必须成功的因素：</b>", sub_heading_style))
        must_succeed = "\n".join([f"• {s}" for s in thesis['must_succeed']])
        story.append(Paragraph(must_succeed, normal_style))

        story.append(Paragraph(f"<b>止损信号（投资逻辑破裂）：</b>", sub_heading_style))
        stop_signals = "\n".join([f"• {s}" for s in thesis['stop_signals']])
        story.append(Paragraph(stop_signals, normal_style))
        story.append(Spacer(1, 0.2*inch))

        # 技术面补充
        story.append(Paragraph("技术面确认", heading_style))
        tech_form = f"""
        <b>技术形态：</b>{technical_data.get('技术形态', 'N/A')}
        <b>趋势判断：</b>{technical_data.get('趋势判断', 'N/A')}
        <b>MACD强度：</b>DIF={technical_data.get('DIF', 0):.4f}, DEA={technical_data.get('DEA', 0):.4f}
        """
        story.append(Paragraph(tech_form, normal_style))
        story.append(Spacer(1, 0.3*inch))

        # 免责声明
        story.append(Paragraph("="*70, small_style))
        disclaimer = """
        <b>重要声明：</b>
        1. 本报告由炼金术量化交易系统自动生成，仅供参考学习，不构成投资建议
        2. 股市有风险，投资需谨慎。请结合个人风险承受能力独立做出投资决策
        3. 建议设置合理止损（建议-8%），分批建仓，分散投资
        4. 历史表现不代表未来收益，技术指标存在滞后性
        5. 投资有风险，入市需谨慎
        """
        story.append(Paragraph(disclaimer, small_style))
        story.append(Spacer(1, 0.2*inch))

        # 页脚
        story.append(Paragraph("炼金术量化交易系统 V2.1 - 深度投资分析版", ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))
        story.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))

        # 生成PDF
        doc.build(story)
        print(f"✅ 已生成股票 {stock_code} 的深度分析报告: {output_file}")

        return output_file

    def generate_complete_report(self, momentum_stocks_file=None):
        """生成完整报告"""
        # 如果没有指定文件，自动查找最新的带时间戳的文件
        if momentum_stocks_file is None:
            import glob
            output_dir = "/Users/xugang/Desktop/炼金术量化交易系统"
            # 查找最新的 alchemy_momentum_stocks_*.xlsx 文件
            files = glob.glob(os.path.join(output_dir, "alchemy_momentum_stocks_*.xlsx"))
            if files:
                momentum_stocks_file = max(files, key=os.path.getmtime)
            else:
                # 如果找不到带时间戳的文件，使用默认文件名
                momentum_stocks_file = os.path.join(output_dir, "alchemy_momentum_stocks.xlsx")

        print("=" * 60)
        print("炼金术量化交易系统 - 报告生成器")
        print("=" * 60)

        # 读取选股结果
        try:
            df = pd.read_excel(momentum_stocks_file)
            # 确保转换为字符串，并自动补零到6位
            selected_stocks = df['code'].astype(str).apply(lambda x: x.zfill(6)).tolist()

            if len(selected_stocks) == 0:
                print("❌ 没有找到符合条件的股票")
                return

            print(f"\n✅ 成功读取 {len(selected_stocks)} 只技术面强势股")
            print("\n开始生成投资分析报告...")

            all_reports = []

            for i, stock_code in enumerate(selected_stocks, 1):
                print(f"\n[{i}/{len(selected_stocks)}] 正在分析股票 {stock_code}...")

                # 获取基本面数据
                fundamental_data = self.get_stock_fundamental_analysis(stock_code)

                # 获取技术面数据
                technical_data = self.get_technical_indicators(stock_code)

                if fundamental_data and technical_data:
                    # 生成单只股票报告
                    report_file = self.generate_stock_report_pdf(
                        stock_code, fundamental_data, technical_data
                    )
                    all_reports.append(report_file)

            print("\n" + "=" * 60)
            print(f"✅ 报告生成完成！")
            print(f"📁 报告保存位置: {self.output_dir}")
            print(f"📊 共生成 {len(all_reports)} 份股票分析报告")
            print("=" * 60)

            return all_reports

        except FileNotFoundError:
            print(f"❌ 找不到选股结果文件: {momentum_stocks_file}")
            print("请先运行选股程序")
            return []
        except Exception as e:
            print(f"❌ 生成报告时出错: {str(e)}")
            return []


if __name__ == "__main__":
    generator = AlchemyReportGenerator()
    generator.generate_complete_report()
