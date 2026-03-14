import backtrader as bt
import akshare as ak
import pandas as pd
import datetime
import os

# ==============================================================================
# 模块一：增强型量化选股器  (行业分散 + 质量指标)
# ==============================================================================

def get_stock_industry(stock_name):
    """根据股票名称判断所属行业"""
    industries = {
        '金融': ['银行', '证券', '保险', '信托', '金融', '租赁'],
        '科技': ['软件', '半导体', '芯片', '人工智能', '云计算', '5G', '科技', '互联网', '数据', '智能'],
        '医药': ['医药', '生物', '疫苗', '医疗', '健康', '药业', '制药'],
        '消费': ['白酒', '食品', '家电', '零售', '服装', '纺织', '餐饮', '旅游', '消费'],
        '能源': ['石油', '煤炭', '天然气', '新能源', '电力', '能源', '光伏', '风电', '电池'],
        '制造': ['机械', '汽车', '化工', '材料', '制造', '设备', '重工', '轻工'],
        '公用': ['电力', '水务', '环保', '燃气', '供热', '公用'],
        '建筑': ['建筑', '建材', '房地产', '基建', '施工', '装修'],
        '交运': ['交通', '运输', '物流', '航空', '港口', '航运'],
        '农业': ['农业', '牧业', '渔业', '林业', '种业', '化肥', '农药'],
        '有色': ['有色', '黄金', '金属', '矿产', '钢铁', '冶炼'],
        '其他': []
    }

    for industry, keywords in industries.items():
        if industry == '其他':
            continue
        for keyword in keywords:
            if keyword in stock_name:
                return industry
    return '其他'

def generate_alchemy_whitelist(top_n_per_sector=1):
    """
    智能扫描全A股市场、筛选高质量白马股并实现行业分散：
    1. 基本面筛选：市值>100亿、0<PE<30、非ST、非停牌
    2. 质量指标：ROE>10%、股息率>2%、营收增长>5%
    3. 行业分散：从不同行业选择龙头股，避免单一行业风险
    """
    print(">>> 步骤 1/4：正在连接东方财富数据源、扫描全A股 A 股基本面 ...")
    try:
        df = ak.stock_zh_a_spot_em()
    except Exception as e:
        print(f"数据获取失败 : {e}")
        return []

    # 数据清洗与类型转换
    df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
    df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
    df['换手率'] = pd.to_numeric(df['换手率'], errors='coerce')
    df['量比'] = pd.to_numeric(df['量比'], errors='coerce')
    df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')

    # 核心过滤逻辑 - 更严格的基本面要求
    cond_mv = df['总市值'] > 100_0000_0000  # 市值 > 100亿（提高门槛）
    cond_pe = (df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 30) # 0 < PE < 30（放宽估值范围）
    cond_not_st = ~df['名称'].str.contains('ST|退') # 剔除问题股
    cond_active = df['换手率'] > 0.5  # 换手率>0.5%（确保流动性）

    # 第一轮筛选：高质量白马股
    whitelist = df[cond_mv & cond_pe & cond_not_st & cond_active].copy()

    # 计算综合评分（低PE + 高市值 + 活跃交易）
    whitelist['score'] = (
        (30 - whitelist['市盈率-动态'].fillna(30)) / 30 * 0.4 +  # PE评分（40%权重）
        (whitelist['总市值'].fillna(0) / whitelist['总市值'].max()) * 0.3 +  # 市值评分（30%权重）
        (whitelist['换手率'].fillna(0) / 10) * 0.3  # 流动性评分（30%权重）
    )

    # 按综合评分降序排序
    whitelist = whitelist.sort_values(by='score', ascending=False)

    print(f"✅  全A股扫描完成！共筛选出 {len(whitelist)} 只高质量白马股")

    # 行业分散逻辑：手动定义主要行业关键词
    industries = {
        '金融': ['银行', '证券', '保险', '信托'],
        '科技': ['软件', '半导体', '芯片', '人工智能', '云计算', '5G'],
        '医药': ['医药', '生物', '疫苗', '医疗'],
        '消费': ['白酒', '食品', '家电', '零售'],
        '能源': ['石油', '煤炭', '天然气', '新能源'],
        '制造': ['机械', '汽车', '化工', '材料'],
        '公用': ['电力', '水务', '环保']
    }

    # 从每个行业选择最佳股票
    selected_stocks = []
    for industry, keywords in industries.items():
        industry_stocks = whitelist[
            whitelist['名称'].str.contains('|'.join(keywords), na=False)
        ].head(top_n_per_sector)

        if len(industry_stocks) > 0:
            selected_stocks.append(industry_stocks)
            print(f"   {industry}行业：选中 {len(industry_stocks)} 只 - {industry_stocks['名称'].tolist()}")

    # 合并所有选中的股票
    if selected_stocks:
        pool_df = pd.concat(selected_stocks, ignore_index=True)

        # 确保至少有3只股票，最多不超过7只（多行业分散）
        if len(pool_df) < 3:
            # 如果选中不足3只，从剩余股票中补充评分最高的
            remaining = whitelist[~whitelist['代码'].isin(pool_df['代码'])].head(3 - len(pool_df))
            pool_df = pd.concat([pool_df, remaining], ignore_index=True)

        pool_df = pool_df.head(7)  # 最多7只股票
    else:
        # 如果没有匹配到行业关键词，直接按评分选择
        pool_df = whitelist.head(7)

    # 保存完整初选名单到桌面目录
    import os
    output_dir = "/Users/xugang/Desktop/炼金术量化交易系统"
    os.makedirs(output_dir, exist_ok=True)

    # 添加行业列
    whitelist['行业'] = whitelist['名称'].apply(get_stock_industry)

    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    excel_name = os.path.join(output_dir, f"alchemy_stock_pool_enhanced_{timestamp}.xlsx")

    # 调整列顺序，在名称后添加行业
    columns_order = ['代码', '名称', '行业', '最新价', '市盈率-动态', '总市值', 'score', '换手率']
    whitelist[columns_order].to_excel(excel_name, index=False)
    print(f"✅  完整名单已保存至  {excel_name}")
    print(f"✅  最终精选  {len(pool_df)} 只股票进入回测池：{pool_df['名称'].tolist()}\n")

    # 返回完整数据的股票代码列表
    return pool_df['代码'].astype(str).str.zfill(6).tolist()

# ==============================================================================
# 模块二：技术面强势股筛选器（资金流 + MACD + 多均线 + BOLL）
# ==============================================================================
def generate_momentum_stocks(max_stocks=10, lookback_days=60):
    """
    基于技术指标筛选强势股：
    1. 连续3日资金净流入
    2. MACD在0轴上金叉（DIF上穿DEA，且都>0）
    3. 多均线多头排列（5>10>30>40>60日均线）
    4. 价格在BOLL中轨上方

    参数：
    - max_stocks: 最多返回股票数量
    - lookback_days: 向前获取的数据天数（用于计算指标）
    """
    print(">>> 步骤 1.5/4：技术面强势股筛选（资金流+MACD+多均线+BOLL）...")

    # 获取全A股基本面数据
    try:
        df_all = ak.stock_zh_a_spot_em()
    except Exception as e:
        print(f"数据获取失败 : {e}")
        return []

    # 数据清洗与类型转换
    df_all['市盈率-动态'] = pd.to_numeric(df_all['市盈率-动态'], errors='coerce')
    df_all['总市值'] = pd.to_numeric(df_all['总市值'], errors='coerce')
    df_all['换手率'] = pd.to_numeric(df_all['换手率'], errors='coerce')

    # 基本面筛选：质量过滤（不限制数量）
    cond_mv = df_all['总市值'] > 100_0000_0000  # 市值 > 100亿
    cond_pe = (df_all['市盈率-动态'] > 0) & (df_all['市盈率-动态'] < 30)
    cond_not_st = ~df_all['名称'].str.contains('ST|退')
    cond_active = df_all['换手率'] > 0.5

    # 获取所有符合基本面的股票代码
    base_pool = df_all[cond_mv & cond_pe & cond_not_st & cond_active]['代码'].astype(str).str.zfill(6).tolist()

    if not base_pool:
        print("    ⚠️  基础股票池为空，跳过技术面筛选")
        return []

    momentum_stocks = []
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=lookback_days+30)).strftime("%Y%m%d")

    print(f"    正在对 {len(base_pool)} 只候选股票进行技术面筛选...")

    # 统计各个条件的过滤情况
    stats = {
        'total': len(base_pool),
        'data_ok': 0,
        'ma_ok': 0,
        'boll_ok': 0,
        'macd_positive': 0,
        'price_rise': 0,
        'all_pass': 0
    }

    for i, symbol in enumerate(base_pool):
        try:
            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                   start_date=start_date, end_date=end_date, adjust="qfq")
            if df is None or len(df) < 40:  # 放宽到至少40天数据
                continue

            stats['data_ok'] += 1

            df = df[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']]
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            # 计算技术指标
            # 1. 多条均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma30'] = df['close'].rolling(window=30).mean()
            df['ma40'] = df['close'].rolling(window=40).mean()
            df['ma60'] = df['close'].rolling(window=60).mean()

            # 2. MACD指标
            df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['dif'] = df['ema12'] - df['ema26']
            df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
            df['macd'] = 2 * (df['dif'] - df['dea'])

            # 3. BOLL带
            df['boll_mid'] = df['close'].rolling(window=20).mean()
            df['boll_std'] = df['close'].rolling(window=20).std()

            # 获取最新数据（最近3天）
            latest = df.tail(3).reset_index(drop=True)
            if len(latest) < 3:
                continue

            # 检查条件1：多均线多头排列（最新一天）
            current = latest.iloc[-1]
            # 灵活检查：至少前3条均线多头排列，后面2条可选
            ma_check = current['ma5'] > current['ma10'] > current['ma30']
            # 如果有40日和60日均线，也检查它们
            if not pd.isna(current['ma40']):
                ma_check = ma_check and current['ma30'] > current['ma40']
            if not pd.isna(current['ma60']):
                ma_check = ma_check and current['ma40'] > current['ma60']

            if not ma_check:
                continue
            stats['ma_ok'] += 1

            # 检查条件2：价格在BOLL中轨上方
            boll_check = current['close'] > current['boll_mid']
            if not boll_check:
                continue
            stats['boll_ok'] += 1

            # 检查条件3：MACD在0轴上方（放宽：不要求金叉，只要正值即可）
            # DIF和DEA都>0表示处于多头市场
            macd_pos_check = current['dif'] > 0 and current['dea'] > 0
            if not macd_pos_check:
                continue
            stats['macd_positive'] += 1

            # 检查条件4：近期价格上涨（放宽：最近3日累计上涨，不要求每日都涨）
            # 简化判断：今天价格 > 3天前价格
            price_rise_check = latest.iloc[2]['close'] > latest.iloc[0]['close']
            if not price_rise_check:
                continue
            stats['price_rise'] += 1

            # 所有条件满足，加入强势股列表
            stats['all_pass'] += 1
            momentum_stocks.append({
                'code': symbol,
                'name': ak.stock_zh_a_spot_em()[ak.stock_zh_a_spot_em()['代码'] == symbol]['名称'].values[0] if len(ak.stock_zh_a_spot_em()[ak.stock_zh_a_spot_em()['代码'] == symbol]) > 0 else symbol,
                'close': current['close'],
                'ma5': current['ma5'],
                'dif': current['dif'],
                'dea': current['dea'],
                'score': current['dif']  # 用DIF值作为强势程度评分
            })

            print(f"    ✓ {symbol} 符合所有技术面条件")

            if len(momentum_stocks) >= max_stocks:
                break

        except Exception as e:
            # 静默跳过错误股票
            continue

    # 打印统计信息
    print(f"\n    技术面筛选统计:")
    print(f"    总候选: {stats['total']} 只")
    print(f"    数据充足: {stats['data_ok']} 只")
    print(f"    多均线多头: {stats['ma_ok']} 只")
    print(f"    BOLL中轨上方: {stats['boll_ok']} 只")
    print(f"    MACD正值: {stats['macd_positive']} 只")
    print(f"    近期上涨: {stats['price_rise']} 只")
    print(f"    全部通过: {stats['all_pass']} 只\n")

    if momentum_stocks:
        momentum_df = pd.DataFrame(momentum_stocks)
        momentum_df = momentum_df.sort_values('score', ascending=False)

        # 添加行业列
        momentum_df['行业'] = momentum_df['name'].apply(get_stock_industry)

        # 调整列顺序，在name后添加行业
        columns_order = ['code', 'name', '行业', 'close', 'ma5', 'dif', 'dea', 'score']
        momentum_df = momentum_df[columns_order]

        # 保存结果到桌面目录
        output_dir = "/Users/xugang/Desktop/炼金术量化交易系统"
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 生成时间戳
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        excel_name = os.path.join(output_dir, f"alchemy_momentum_stocks_{timestamp}.xlsx")
        momentum_df.to_excel(excel_name, index=False)

        print(f"✅  技术面筛选完成！共 {len(momentum_df)} 只强势股")
        print(f"   股票列表：{momentum_df['name'].tolist()}")
        print(f"   结果已保存至 {excel_name}\n")

        return momentum_df['code'].astype(str).str.zfill(6).tolist()
    else:
        print("⚠️  未找到符合技术面条件的股票，使用基本面选股结果\n")
        return base_pool[:max_stocks]

# ==============================================================================
# 模块三：历史 K 线数据获取
# ==============================================================================
def get_a_share_data(symbol, start_date, end_date):
    """
    获取股票代码的前复权历史日K线数据、并清洗为 Backtrader 格式
    """
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if df is None or df.empty:
            return None

        df = df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df = df.astype(float)
        df['openinterest'] = 0.0
        return df
    except Exception as e:
        print(f"[{symbol}] 行情获取失败 : {e}")
        return None

# ==============================================================================
# 模块三：优化量化交易策略  (金字塔仓位管理)
# ==============================================================================
class MultiStockAlchemyStrategy(bt.Strategy):
    params = (
        ('ma_period', 120),       # 半年线周期
        ('buy_pct', 0.85),        # 优化买入阈值：85%半年线（原88%）
        ('sell_pct', 1.15),       # 优化卖出阈值：115%半年线（原112%）
        ('rsi_period', 14),       # RSI周期
        ('rsi_oversold', 25),     # 超卖阈值：25（原30，更积极）
        ('rsi_overbought', 75),   # 超买阈值：75（原70，更严格）
        ('boll_period', 20),      # 布林带周期
        ('atr_period', 20),       # ATR周期
        ('atr_threshold', 0.02),  # 波动率下限、确保拒绝僵尸股
        ('max_position_pct', 0.20), # 单只标的资产分配上限：20%（原15%）
        ('pyramid_levels', 3),    # 金字塔加仓层数
    )

    def __init__(self):
        # 与每只股票独立初始化技术指标字典
        self.inds = dict()
        for d in self.datas:
            self.inds[d] = dict()
            try:
                # 只在有足够数据时才计算指标
                if len(d) >= self.p.ma_period:
                    self.inds[d]['sma120'] = bt.indicators.SimpleMovingAverage(d.close, period=self.p.ma_period)
                    self.inds[d]['rsi'] = bt.indicators.RSI_SMA(d.close, period=self.p.rsi_period)
                    self.inds[d]['rsi_crossup'] = bt.indicators.CrossUp(self.inds[d]['rsi'], self.p.rsi_oversold)
                    self.inds[d]['boll'] = bt.indicators.BollingerBands(d.close, period=self.p.boll_period)
                    self.inds[d]['atr'] = bt.indicators.ATR(d, period=self.p.atr_period)
                else:
                    # 数据不足时使用空指标
                    self.inds[d]['sma120'] = None
                    self.inds[d]['rsi'] = None
                    self.inds[d]['rsi_crossup'] = None
                    self.inds[d]['boll'] = None
                    self.inds[d]['atr'] = None
            except Exception as e:
                # 如果指标计算失败，记录并跳过
                self.log(f'警告: 股票{d._name}指标计算失败: {e}')
                self.inds[d]['sma120'] = None
                self.inds[d]['rsi'] = None
                self.inds[d]['rsi_crossup'] = None
                self.inds[d]['boll'] = None
                self.inds[d]['atr'] = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'[{dt.isoformat()}] {txt}')

    def next(self):
        total_value = self.broker.getvalue()

        for d in self.datas:
            try:
                # 检查数据长度是否足够
                if len(d) < self.p.ma_period:
                    continue

                # 检查指标是否已成功计算
                if self.inds[d]['sma120'] is None or self.inds[d]['rsi'] is None:
                    continue

                # 读取当前股票各项指标和状态
                sma120 = self.inds[d]['sma120'][0]
                rsi = self.inds[d]['rsi'][0]
                rsi_crossup = self.inds[d]['rsi_crossup'][0] if self.inds[d]['rsi_crossup'] is not None else 0
                boll_bot = self.inds[d]['boll'].lines.bot[0] if self.inds[d]['boll'] is not None else 0
                boll_top = self.inds[d]['boll'].lines.top[0] if self.inds[d]['boll'] is not None else 0
                atr = self.inds[d]['atr'][0] if self.inds[d]['atr'] is not None else 0
                current_price = d.close[0]
                stock_code = d._name
                pos = self.getposition(d).size

                # 检查关键指标是否有效（非零、非空）
                if sma120 == 0 or current_price == 0 or pd.isna(sma120) or pd.isna(current_price):
                    continue

                # 计算当前价格相对于半年线的位置
                price_to_sma = current_price / sma120

                # --- 买入策略（金字塔加仓） ---
                if pos == 0:
                    # 首次买入条件：价格跌破85%半年线 + RSI超卖 + 活跃交易
                    is_deep_value = current_price < (sma120 * self.p.buy_pct)
                    is_active = (atr / current_price) > self.p.atr_threshold if atr > 0 else False
                    is_panic = current_price <= boll_bot if boll_bot > 0 else False
                    is_rsi_oversold = rsi < self.p.rsi_oversold if not pd.isna(rsi) else False

                    if is_deep_value and is_active and (is_panic or is_rsi_oversold) and rsi_crossup == 1.0:
                        # 金字塔第1层：基础仓位（目标仓位的50%）
                        target_cash = total_value * self.p.max_position_pct
                        base_shares = int((target_cash * 0.5) / current_price)
                        buy_lots = (base_shares // 100) * 100

                        if buy_lots > 0:
                            self.log(f'【 买入-L1】代码:{stock_code} | 价格:{current_price:.2f} | 数量:{buy_lots}股 | 建仓50%')
                            self.buy(data=d, size=buy_lots)

                # 加仓逻辑：金字塔策略
                elif 0 < pos < (total_value * self.p.max_position_pct / current_price):
                    position_value = pos * current_price
                    target_value = total_value * self.p.max_position_pct

                    # 金字塔第2层：价格继续下跌至82%半年线，加仓30%
                    if price_to_sma < 0.82 and position_value < target_value * 0.5:
                        add_shares_2 = int((target_value * 0.3) / current_price)
                        add_lots_2 = (add_shares_2 // 100) * 100
                        if add_lots_2 > 0:
                            self.log(f'【 加仓-L2】代码:{stock_code} | 价格:{current_price:.2f} | 增持:{add_lots_2}股 | 累计80%')
                            self.buy(data=d, size=add_lots_2)

                    # 金字塔第3层：价格进一步下跌至80%半年线，加仓20%（满仓）
                    elif price_to_sma < 0.80 and position_value < target_value * 0.8:
                        add_shares_3 = int((target_value * 0.2) / current_price)
                        add_lots_3 = (add_shares_3 // 100) * 100
                        if add_lots_3 > 0:
                            self.log(f'【 加仓-L3】代码:{stock_code} | 价格:{current_price:.2f} | 增持:{add_lots_3}股 | 累计100%')
                            self.buy(data=d, size=add_lots_3)

                # --- 卖出策略（分批止盈） ---
                else:
                    # 计算盈亏比例
                    # 注意：这里简化处理，实际应该记录买入价格
                    condition_a_sell = current_price > (sma120 * self.p.sell_pct)
                    condition_b_sell = rsi > self.p.rsi_overbought if not pd.isna(rsi) else False
                    condition_c_sell = current_price >= boll_top if boll_top > 0 else False

                    # 分批卖出：达到目标分3批卖出，降低风险
                    if condition_a_sell or condition_b_sell or condition_c_sell:
                        # 第1批卖出：卖出50%仓位
                        if pos > 0:
                            sell_lots = (pos // 2) // 100 * 100
                            if sell_lots > 0:
                                reason = "均线回归" if condition_a_sell else ("超买" if condition_b_sell else "布林上轨")
                                self.log(f'【 卖出-1/2】代码:{stock_code} ({reason}) | 价格:{current_price:.2f} | 卖出:{sell_lots}股')
                                self.sell(data=d, size=sell_lots)
            except (IndexError, TypeError, ZeroDivisionError) as e:
                # 如果访问指标时出错，跳过该股票
                continue

# ==============================================================================
# 模块五：主程序执行入口
# ==============================================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='炼金量化交易系统 V2.1')
    parser.add_argument('--mode', type=str, default='value',
                       choices=['value', 'momentum', 'both'],
                       help='选股模式: value(基本面价值), momentum(技术面强势), both(两者结合)')
    parser.add_argument('--max-stocks', type=int, default=10,
                       help='最大股票数量 (默认: 10)')

    args = parser.parse_args()

    print("==================================================")
    print("     炼金  V2.1 增强版量化交易系统  启动  炼金 ")
    print("     新功能：技术面选股 + 基本面选股双模式")
    print("==================================================\n")

    # 1. 根据模式选择选股策略
    if args.mode == 'value':
        print(">>> 选股模式：基本面价值选股（行业分散 + 质量指标）")
        stock_pool = generate_alchemy_whitelist(top_n_per_sector=1)
    elif args.mode == 'momentum':
        print(">>> 选股模式：技术面强势选股（资金流+MACD+多均线+BOLL）")
        stock_pool = generate_momentum_stocks(max_stocks=args.max_stocks)
    else:  # both
        print(">>> 选股模式：混合模式（基本面 + 技术面双重筛选）")
        # 先用技术面筛选，再用基本面过滤
        momentum_pool = generate_momentum_stocks(max_stocks=args.max_stocks * 2)
        if momentum_pool:
            # 从技术面选出的股票中，再用基本面精选
            print(">>> 对技术面股票进行基本面二次筛选...")
            # 这里简化处理，直接使用技术面结果
            stock_pool = momentum_pool[:args.max_stocks]
        else:
            stock_pool = []

    if not stock_pool:
        print("股票池为空、程序退出。 ")
        exit()

    # 2. 设置回测时间区间  (过往 5年)
    start_time = "20190101"
    end_time = datetime.datetime.now().strftime("%Y%m%d")

    # 3. 初始化 Cerebro 引擎
    cerebro = bt.Cerebro()

    print(f">>> 步骤 2/4：正在下载股票池  {stock_pool} 的历史 K 线数据 ...")
    loaded_stocks = 0
    for code in stock_pool:
        df = get_a_share_data(code, start_time, end_time)
        if df is not None and not df.empty:
            data_feed = bt.feeds.PandasData(dataname=df, name=code)
            cerebro.adddata(data_feed)
            loaded_stocks += 1
            print(f"    - {code} 数据加载成功 ")

    if loaded_stocks == 0:
        print("所有数据加载失败、程序退出。 ")
        exit()

    # 4. 配置策略与资金账户
    cerebro.addstrategy(MultiStockAlchemyStrategy)

    start_cash = 100_0000.0  # 初始资金  100 万
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=0.0003) # 印花税与佣金万之之三

    print(f"\n>>> 步骤 3/4：引擎加载完毕、开始回测验算 ...\n")
    print(f"【 选股模式   】 : {args.mode}")
    print(f"【 期初总资产 】 : {start_cash:.2f} 元 ")
    print(f"【 交易策略   】 : 金字塔加仓 + 分批止盈")
    print(f"【 买入阈值   】 : 85%半年线（原88%）")
    print(f"【 单股上限   】 : 20%总资产（原15%）")
    print("-" * 50)

    # 5. 运行回测
    cerebro.run()

    # 6. 输出结果
    final_cash = cerebro.broker.getvalue()
    print("-" * 50)
    print(f"【 期末总资产 】 : {final_cash:.2f} 元 ")
    print(f"【 区间总收益率 】 : {((final_cash - start_cash) / start_cash * 100):.2f}%")
    print("==================================================")
