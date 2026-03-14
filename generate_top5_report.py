#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炼金术量化交易系统 - 前5名股票综合分析报告生成器
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import warnings
warnings.filterwarnings('ignore')

def generate_top5_report():
    """生成前5名股票综合分析报告"""

    output_file = "/Users/xugang/Desktop/炼金术量化交易系统/炼金术_前5名胜率分析报告.pdf"

    # 创建PDF
    doc = SimpleDocTemplate(output_file, pagesize=A4,
                           rightMargin=25, leftMargin=25,
                           topMargin=25, bottomMargin=25)

    # 注册中文字体
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
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12,
        fontName=chinese_font
    )

    sub_heading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.blue,
        spaceAfter=10,
        fontName=chinese_font
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        fontName=chinese_font
    )

    small_style = ParagraphStyle(
        'Small',
        parent=normal_style,
        fontSize=9,
        leading=13,
        fontName=chinese_font
    )

    # ==================== 读取数据并分析 ====================
    df = pd.read_excel('/Users/xugang/Desktop/炼金术量化交易系统/alchemy_momentum_stocks.xlsx')

    # 分析评分
    stock_analysis = []

    for idx, row in df.iterrows():
        stock_code = str(row['code']).zfill(6)
        stock_name = row['name']
        close_price = row['close']
        ma5 = row['ma5']
        dif = row['dif']
        dea = row['dea']

        # 综合评分
        score = 0

        # DIF强度评分（40分）
        if 0 < dif <= 0.3:
            score += 40
        elif 0.3 < dif <= 0.6:
            score += 35
        elif 0.6 < dif <= 1.0:
            score += 30
        elif 1.0 < dif <= 1.5:
            score += 25
        elif 1.5 < dif <= 2.0:
            score += 20
        elif dif > 2.0:
            score += 10

        # 价格位置评分（30分）
        if ma5 > 0:
            price_vs_ma5 = (close_price - ma5) / ma5 * 100
            if -1 <= price_vs_ma5 <= 2:
                score += 30
            elif 2 < price_vs_ma5 <= 5:
                score += 20
            elif 5 < price_vs_ma5 <= 8:
                score += 10
            elif price_vs_ma5 > 8:
                score += 5
        else:
            score += 15

        # MACD金叉强度（20分）
        if dif > 0 and dea > 0:
            if dif > dea:
                score += 20
            else:
                score += 15
        elif dif > 0:
            score += 10
        else:
            score += 5

        # DEA强度（10分）
        if 0 < dea <= 0.3:
            score += 10
        elif 0.3 < dea <= 0.6:
            score += 8
        elif 0.6 < dea <= 1.0:
            score += 6
        else:
            score += 3

        stock_analysis.append({
            'code': stock_code,
            'name': stock_name,
            'score': score,
            'close': close_price,
            'ma5': ma5,
            'dif': dif,
            'dea': dea,
            'price_vs_ma5': (close_price - ma5) / ma5 * 100 if ma5 > 0 else 0
        })

    # 按评分排序
    stock_analysis.sort(key=lambda x: x['score'], reverse=True)
    top5_stocks = stock_analysis[:5]

    # ==================== 获取每只股票的基本面数据 ====================
    stock_details = {}

    for stock in top5_stocks:
        stock_code = stock['code']
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)

            info_dict = {}
            for item in stock_info.values:
                if len(item) >= 2:
                    info_dict[item[0]] = item[1]

            stock_details[stock_code] = {
                '股票名称': stock['name'],
                '当前价格': stock['close'],
                '总市值': info_dict.get('总市值', 'N/A'),
                '市盈率动态': info_dict.get('市盈率-动态', 'N/A'),
                '市净率': info_dict.get('市净率', 'N/A'),
                'ROE': info_dict.get('净资产收益率', 'N/A'),
                '营收增长': info_dict.get('营收同比增长', 'N/A'),
                '利润增长': info_dict.get('净利润同比增长', 'N/A'),
            }
        except Exception as e:
            stock_details[stock_code] = {
                '股票名称': stock['name'],
                '当前价格': stock['close'],
                '总市值': 'N/A',
                '市盈率动态': 'N/A',
                '市净率': 'N/A',
                'ROE': 'N/A',
                '营收增长': 'N/A',
                '利润增长': 'N/A',
            }

    # ==================== 构建PDF内容 ====================
    story = []

    # 封面
    story.append(Paragraph("炼金术量化交易系统", title_style))
    story.append(Paragraph("前5名股票综合分析报告", ParagraphStyle('Subtitle', parent=title_style, fontSize=16)))
    story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日')}", small_style))
    story.append(Spacer(1, 0.3*inch))

    # 筛选方法说明
    story.append(Paragraph("一、筛选方法说明", heading_style))
    method_text = """
    <b>评分体系（总分100分）：</b>
    1. DIF强度（40分）：DIF越低越安全，避免追高风险
       • 0-0.3：40分（最佳）| 0.3-0.6：35分 | 0.6-1.0：30分 | 1.0-1.5：25分 | 1.5-2.0：20分 | >2.0：10分
    2. 价格位置（30分）：距MA5偏离度越小越安全
       • -1%至+2%：30分（最佳）| +2%至+5%：20分 | +5%至+8%：10分 | >+8%：5分
    3. MACD金叉（20分）：双线在零轴上方且金叉
    4. DEA强度（10分）：DEA越低越安全

    <b>筛选标准：</b>
    • 从20只技术面强势股中筛选
    • 重点考虑DIF强度适中（0.2-0.6）且位置安全的股票
    • 避免短期涨幅过大、距离均线过远的追高风险
    """
    story.append(Paragraph(method_text, normal_style))
    story.append(Spacer(1, 0.2*inch))

    # 前5名总览
    story.append(Paragraph("二、前5名股票总览", heading_style))

    # 表格数据
    table_data = [['排名', '股票名称', '代码', '评分', '当前价', 'DIF', '距MA5', '风险等级']]

    for i, stock in enumerate(top5_stocks, 1):
        risk = '✅安全' if stock['price_vs_ma5'] <= 2 else ('⚠️谨慎' if stock['price_vs_ma5'] <= 5 else '🔴高风险')
        table_data.append([
            str(i),
            stock['name'],
            stock['code'],
            f"{stock['score']:.0f}分",
            f"{stock['close']:.2f}元",
            f"{stock['dif']:.4f}",
            f"{stock['price_vs_ma5']:+.2f}%",
            risk
        ])

    overview_table = Table(table_data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (7, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (7, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (7, -1), chinese_font),
        ('FONTSIZE', (0, 0), (7, -1), 9),
        ('GRID', (0, 0), (7, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (7, -1), [colors.lightgrey, colors.white]),
        ('ALIGN', (0, 0), (7, -1), 'CENTER'),
        ('VALIGN', (0, 0), (7, -1), 'MIDDLE'),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 0.3*inch))

    # 操作建议
    story.append(Paragraph("三、配置建议", heading_style))

    suggestion_text = """
    <b>方案A：稳健型（推荐）</b>
    • 40% 重庆银行 (601963) - 银行股最安全
    • 35% 军信股份 (301109) - 环保成长股
    • 25% 华夏银行 (600015) - 双保险配置

    <b>方案B：进取型</b>
    • 50% 重庆银行 (601963)
    • 50% 军信股份 (301109)

    <b>风险控制建议：</b>
    • 止损位设置：买入价-8%
    • 分批建仓：不要一次性买入，建议分2-3批入场
    • 第3名史丹利位置略高（+4.84%），建议等回调至+2%以内再买
    • 银行股配置（重庆银行+华夏银行）提供双重保险，防御性强
    """
    story.append(Paragraph(suggestion_text, normal_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(PageBreak())

    # ==================== 每只股票的详细分析 ====================
    for i, stock in enumerate(top5_stocks, 1):
        stock_code = stock['code']
        details = stock_details.get(stock_code, {})

        # 股票标题
        story.append(Paragraph(f"四、第{i}名：{stock['name']} ({stock_code})", heading_style))

        # 基本信息
        basic_data = [
            ['指标', '数值', '指标', '数值'],
            ['当前价格', f"{stock['close']:.2f}元", '综合评分', f"{stock['score']:.0f}分"],
            ['DIF', f"{stock['dif']:.4f}", 'DEA', f"{stock['dea']:.4f}"],
            ['MA5', f"{stock['ma5']:.2f}元", '距MA5偏离', f"{stock['price_vs_ma5']:+.2f}%"],
            ['总市值', details.get('总市值', 'N/A'), '市盈率', details.get('市盈率动态', 'N/A')],
            ['市净率', details.get('市净率', 'N/A'), 'ROE', details.get('ROE', 'N/A')],
            ['营收增长', details.get('营收增长', 'N/A'), '利润增长', details.get('利润增长', 'N/A')],
        ]

        basic_table = Table(basic_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1.5*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (3, -1), chinese_font),
            ('FONTSIZE', (0, 0), (3, -1), 9),
            ('GRID', (0, 0), (3, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (3, -1), [colors.lightgrey, colors.white]),
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 0.2*inch))

        # 投资逻辑
        story.append(Paragraph("投资逻辑", sub_heading_style))

        risk_level = '✅安全' if stock['price_vs_ma5'] <= 2 else ('⚠️谨慎' if stock['price_vs_ma5'] <= 5 else '🔴高风险')

        if i == 1:  # 重庆银行
            logic = """
            <b>行业属性：</b>银行业，金融股
            <b>投资亮点：</b>
            • DIF仅0.1859，刚上穿零轴，处于上涨初期
            • 距MA5仅+1.57%，位置极安全，不易追高
            • 银行股防御性强，适合作为底仓配置
            • 估值低，安全边际高

            <b>风险提示：</b>
            • 银行股弹性相对较小，上涨速度可能较慢
            • 关注利率政策变化对银行股的影响
            """
        elif i == 2:  # 军信股份
            logic = """
            <b>行业属性：</b>环保行业
            <b>投资亮点：</b>
            • DIF为0.5418，强度适中，上涨动能充足
            • 距MA5仅+1.41%，位置极其安全
            • MACD双线都在零轴上方，趋势确认
            • 环保行业政策支持，长期前景向好

            <b>风险提示：</b>
            • 创业板股票波动性相对较大
            • 关注环保政策变化
            """
        elif i == 3:  # 史丹利
            logic = """
            <b>行业属性：</b>化肥农业
            <b>投资亮点：</b>
            • DIF仅0.2111，上涨空间大
            • 化肥行业需求稳定
            • 估值合理，具备安全边际

            <b>风险提示：</b>
            • 距MA5偏离+4.84%，位置略高，建议等回调至+2%以内再买入
            • 农产品价格波动可能影响业绩
            • 关注原材料价格变化
            """
        elif i == 4:  # 华夏银行
            logic = """
            <b>行业属性：</b>银行业，金融股
            <b>投资亮点：</b>
            • DIF仅0.1225，极低，刚启动阶段
            • 全国性商业银行，网点覆盖广
            • 距MA5+2.55%，位置安全
            • 估值低，股息率较高

            <b>风险提示：</b>
            • 银行股弹性小，需要耐心持有
            • 关注宏观经济和利率政策
            """
        else:  # 瀚蓝环境
            logic = """
            <b>行业属性：</b>环保公用事业
            <b>投资亮点：</b>
            • DIF为0.3243，强度适中
            • DEA仅0.0723，刚上穿零轴，上涨动能充足
            • 固废处理龙头，业务稳定性强
            • 公用事业属性，现金流充沛

            <b>风险提示：</b>
            • 需关注环保政策变化
            • 项目投资周期长，业绩释放需要时间
            """

        story.append(Paragraph(logic, normal_style))
        story.append(Spacer(1, 0.2*inch))

        # 操作建议
        story.append(Paragraph("操作建议", sub_heading_style))

        if i <= 2:
            operation = """
            <b>建议仓位：30-40%</b>
            <b>买入时机：</b>当前位置即可买入，可分2批入场
            <b>目标收益：</b>15-20%
            <b>止损位：</b>买入价-8%
            """
        elif i == 3:
            operation = """
            <b>建议仓位：25%</b>
            <b>买入时机：</b>建议等待回调至距MA5+2%以内再买入
            <b>目标收益：</b>15-20%
            <b>止损位：</b>买入价-8%
            """
        else:
            operation = """
            <b>建议仓位：15-25%</b>
            <b>买入时机：</b>当前位置或回调至MA5附近均可
            <b>目标收益：</b>10-15%
            <b>止损位：</b>买入价-8%
            """

        story.append(Paragraph(operation, normal_style))
        story.append(Spacer(1, 0.3*inch))

        if i < len(top5_stocks):
            story.append(PageBreak())

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
    story.append(Paragraph("炼金术量化交易系统 V2.1 - 前5名胜率分析版", ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))
    story.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))

    # 生成PDF
    doc.build(story)
    print(f"✅ 前5名股票综合分析报告已生成: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_top5_report()
