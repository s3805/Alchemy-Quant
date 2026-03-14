#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炼金术量化交易系统 - 系统介绍PDF生成器 (紧凑版)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

def generate_system_intro():
    """生成系统介绍PDF (紧凑版 - 4页)"""

    output_file = "/Users/xugang/Desktop/炼金术量化交易系统/炼金术系统介绍.pdf"

    doc = SimpleDocTemplate(output_file, pagesize=A4,
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=30)

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
                print(f"✓ 成功加载中文字体: {font_name}")
                break
            except Exception as e:
                print(f"✗ 字体加载失败 {font_name}: {e}")
                continue

    if chinese_font == 'Helvetica':
        print("⚠️  警告: 未能加载中文字体，中文可能显示异常")

    styles = getSampleStyleSheet()

    # 紧凑样式 - 更小的间距
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=chinese_font
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=8,
        fontName=chinese_font
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY,
        fontName=chinese_font
    )

    small_style = ParagraphStyle(
        'Small',
        parent=normal_style,
        fontSize=9,
        leading=13,
        fontName=chinese_font
    )

    story = []

    # 第1页: 封面 + 系统概述 + 核心功能
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("炼金术量化交易系统", title_style))
    story.append(Paragraph("Alchemy Quant Trading System V2.1", ParagraphStyle(
        'Subtitle', parent=title_style, fontSize=14, textColor=colors.blue)))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("技术面动量选股 + 基本面价值投资", normal_style))
    story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日')}", small_style))
    story.append(Spacer(1, 0.4*inch))

    # 系统概述
    story.append(Paragraph("一、系统概述", heading_style))
    overview = """
    <b>炼金术量化交易系统</b>是一套基于Python开发的智能A股量化交易系统，
    采用"炼金术"命名,寓意通过科学的量化方法,从海量股票中提炼出具备投资价值的优质标的。

    <b>核心特点:</b>
    • <b>双模式选股</b>: 技术面动量 + 基本面价值双重筛选
    • <b>智能筛选</b>: 609只基础池股票多维度技术分析
    • <b>金字塔仓位</b>: 动态仓位管理,风险可控
    • <b>行业分散</b>: 跨行业配置,降低集中度风险
    • <b>回测验证</b>: 基于Backtrader引擎的历史回测
    • <b>专业报告</b>: 自动生成PDF投资分析报告
    """
    story.append(Paragraph(overview, normal_style))
    story.append(Spacer(1, 0.2*inch))

    # 核心功能表格
    story.append(Paragraph("二、核心功能", heading_style))
    functions = [
        ['功能模块', '描述'],
        ['技术面选股', 'MACD、多均线、BOLL等多指标筛选'],
        ['基本面选股', 'PE、PB、ROE、增长率等财务指标'],
        ['组合策略', '技术+基本面双验证,提高胜率'],
        ['回测引擎', '基于Backtrader框架的历史数据回测'],
        ['风险管理', '金字塔加仓、分批止盈策略'],
        ['报告生成', '自动生成专业PDF投资分析报告'],
    ]

    func_table = Table(functions, colWidths=[2.2*inch, 3.3*inch])
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (1, -1), 8),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (1, -1), [colors.lightgrey, colors.white])
    ]))
    story.append(func_table)
    story.append(Spacer(1, 0.3*inch))

    # 第2页: 选股策略详解
    story.append(Paragraph("三、选股策略", heading_style))

    # 技术面策略
    story.append(Paragraph("<b>3.1 技术面动量选股</b>", ParagraphStyle(
        'SubHeading', parent=heading_style, fontSize=12, fontName=chinese_font)))

    tech_strategy = """
    系统采用<b>多指标共振</b>策略,要求股票同时满足:

    <b>① 多均线多头排列</b> - 5日>10日>30日均线,确保中期趋势向上

    <b>② MACD正向金叉</b> - DIF>0且DEA>0,表明动量强劲

    <b>③ 突破BOLL中轨</b> - 当前价格>BOLL中轨(20日均线),打开上升通道

    <b>④ 3日累计上涨</b> - 最近3日累计涨幅为正,确认短期动能
    """
    story.append(Paragraph(tech_strategy, normal_style))
    story.append(Spacer(1, 0.2*inch))

    # 基本面策略
    story.append(Paragraph("<b>3.2 基本面价值选股</b>", ParagraphStyle(
        'SubHeading', parent=heading_style, fontSize=12, fontName=chinese_font)))

    fund_strategy = """
    基本面选股采用<b>价值投资</b>理念:

    <b>① 市值筛选</b> - 总市值>100亿元,确保流动性

    <b>② 估值筛选</b> - 0<市盈率(动态)<30,避免估值过高和亏损企业

    <b>③ 行业分散</b> - 跨行业配置(金融、医药、消费、能源、制造、公用)

    <b>④ 质量筛选</b> - 排除ST股票,换手率>0.5%保证流动性
    """
    story.append(Paragraph(fund_strategy, normal_style))
    story.append(Spacer(1, 0.2*inch))

    # 第3页: 技术指标 + 使用指南
    story.append(Paragraph("四、技术指标", heading_style))

    indicators = [
        ['指标', '计算公式', '应用说明'],
        ['MA均线', 'N日收盘价平均值', '判断趋势方向'],
        ['MACD', 'DIF=EMA12-EMA26', '判断动量强弱'],
        ['BOLL', '中轨±2倍标准差', '判断波动通道'],
        ['RSI', '相对强弱指标', '判断超买超卖'],
        ['KDJ', '随机指标', '判断买卖时机'],
    ]

    indi_table = Table(indicators, colWidths=[1.3*inch, 2.2*inch, 2*inch])
    indi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (2, -1), chinese_font),
        ('FONTSIZE', (0, 0), (2, -1), 8),
        ('BOTTOMPADDING', (0, 0), (2, -1), 6),
        ('GRID', (0, 0), (2, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (2, -1), [colors.lightgrey, colors.white])
    ]))
    story.append(indi_table)
    story.append(Spacer(1, 0.3*inch))

    # 使用指南
    story.append(Paragraph("五、使用指南", heading_style))

    guide_text = """
    <b>步骤一: 运行选股程序</b>
    <font face="Courier" size="9">
    # 技术面动量选股(默认选20只)
    python alchemy_system.py --mode momentum --max-stocks 20

    # 基本面价值选股
    python alchemy_system.py --mode value

    # 组合模式(两者结合)
    python alchemy_system.py --mode both
    </font>

    <b>步骤二: 查看选股结果</b>
    系统自动生成Excel文件: alchemy_momentum_stocks.xlsx
    包含股票代码、名称、技术指标等详细信息,按MACD-DIF强度排序

    <b>步骤三: 生成投资分析报告</b>
    <font face="Courier" size="9">
    python generate_alchemy_report.py
    </font>
    自动为每只股票生成PDF分析报告,包含基本面、技术面、投资建议等

    <b>步骤四: 查看回测结果</b>
    系统自动运行回测,输出收益率、最大回撤等指标和交易信号明细
    """
    story.append(Paragraph(guide_text, small_style))

    # 第4页: 风险提示
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("六、风险提示", heading_style))

    risk_warning = """
    <b><font color="red" size="12">重要风险提示</font></b>

    <b>1. 历史表现不代表未来收益</b>
    • 系统基于历史数据回测,市场环境不断变化
    • 过去业绩不预示未来表现

    <b>2. 技术分析局限性</b>
    • 技术指标存在滞后性
    • 突发事件无法预测
    • 需结合基本面分析

    <b>3. 资金管理建议</b>
    • 单只股票仓位不超过20%
    • 设置止损位(建议-8%)
    • 分批建仓,分批止盈
    • 保留现金储备

    <b>4. 系统性风险</b>
    • 市场整体下跌风险
    • 政策变化风险
    • 黑天鹅事件风险

    <b>5. 使用建议</b>
    • 本系统仅供参考,不构成投资建议
    • 请结合自身风险承受能力
    • 建议咨询专业投资顾问
    • <font color="red" size="11">股市有风险,投资需谨慎</font>
    """
    story.append(Paragraph(risk_warning, normal_style))
    story.append(Spacer(1, 0.3*inch))

    # 页脚
    story.append(Paragraph("=" * 70, small_style))
    story.append(Paragraph("<b>炼金术量化交易系统 V2.1</b> - 技术面选股 + 基本面选股双模式",
                          ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))
    story.append(Paragraph(f"© {datetime.now().year} Alchemy Quant. 本系统仅供学习研究使用",
                          ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)))

    # 生成PDF
    doc.build(story)
    print(f"✅ 系统介绍PDF已生成(紧凑版): {output_file}")
    return output_file


if __name__ == "__main__":
    generate_system_intro()
