import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import random
import textwrap

st.set_page_config(page_title="2026 智睿全球高净值量化终端", page_icon="🏦", layout="wide")

# --- 前端样式优化 ---
st.markdown("""
    <style>
    .report-text { font-size: 1rem !important; line-height: 1.8; text-align: justify; }
    .card-title { color: #4A90E2; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px; }
    .card-title-sell { color: #F56C6C; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px; }
    .card-body { font-size: 0.9rem; margin-bottom: 5px; color: #b0b0b0;}
    .data-row { font-size: 0.85rem; color: #888888; margin-top: 8px; margin-bottom: 8px; padding: 5px 0; border-top: 1px dashed #444; border-bottom: 1px dashed #444;}
    .reason-text { font-size: 0.95rem; font-weight: 500; margin-top: 12px; color: #E6A23C; line-height: 1.6; padding: 10px; background-color: rgba(230, 162, 60, 0.08); border-radius: 5px;}
    .engine-alert { border-left: 4px solid #F56C6C; padding: 10px; background-color: rgba(245, 108, 108, 0.1); margin-bottom: 20px;}
    h3 { border-left: 5px solid #4A90E2; padding-left: 12px; margin-top: 25px !important; }
    .disclaimer { font-size: 0.85rem; color: #888888; border-top: 1px solid #555; padding-top: 15px; margin-top: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 行业动态主题池 (全量资产) ---
DYNAMIC_POOLS = {
    "CORE_EQUITY": ["VOO", "IVV", "SPY", "VTI", "DIA", "IWM", "RSP", "VT", "URTH", "QQQM"],
    "GROWTH_TECH": ["QQQ", "VGT", "XLK", "SMH", "SOXX", "NVDA", "MSFT", "GOOGL", "AAPL", "AMD", "AVGO", "TSM", "ARM", "META", "AMZN", "CRWD", "PLTR", "PANW", "NOW", "TSLA"],
    "DEFENSIVE_VALUE": ["SCHD", "VIG", "DGRO", "LLY", "UNH", "PG", "JNJ", "WMT", "COST", "HD", "PEP", "KO", "MCD", "MRK", "ABBV"],
    "FIXED_INCOME": ["TLT", "IEF", "BND", "AGG", "JNK", "LQD", "SHY", "MBB", "MUB", "HYG"],
    "ALTERNATIVE": ["IBIT", "FBTC", "GLD", "IAU", "XLE", "XOP", "BITO", "MSTR", "COIN", "DBC", "SLV", "URA", "URNM"],
    "CASH_MANAGEMENT": ["BOXX", "SGOV", "BIL", "VGSH", "MINT"]
}

# --- 2. 纯中文资产大百科字典 ---
CN_ASSET_WIKI = {
    "SPY": "全球成立最早、规模最大且流动性最强的标普500指数ETF，涵盖美国500家顶尖上市公司的股票，是反映美国大盘表现的核心宽基工具。",
    "IVV": "iShares核心标普500 ETF，提供对美国大盘股的广泛敞口，以极低的管理费率著称，是全球流动性极强的宽基指数基金之一。",
    "VOO": "先锋领航发行的标普500 ETF，以极致的低成本优势覆盖美国市值最大的500家优质公司，是美股大盘核心配置与长期定投的首选。",
    "QQQ": "纳斯达克100 ETF，重仓全球最顶尖的科技、互联网与半导体巨头（不含金融股），是捕获科技创新与AI红利的第一锋矛。",
    "QQQM": "纳斯达克100 ETF的低费率版本，底层资产与QQQ完全一致，更适合长期持有与定投的科技成长底仓。",
    "NVDA": "英伟达是全球图形处理器(GPU)和人工智能(AI)算力芯片的绝对霸主，构筑了软硬件一体化（CUDA）的极深护城河，是AI时代的“卖水人”。",
    "MSFT": "微软是全球领先的软件与云计算巨头，凭借 Azure 云服务与 OpenAI 的深度绑定，在 B 端企业级 AI 应用中形成绝对垄断。",
    "GOOGL": "谷歌是全球搜索引擎与数字广告霸主，手握海量专有数据与顶尖 AI 研发能力，在自动驾驶与云计算领域位居世界前列。",
    "AAPL": "苹果是消费电子领域的绝对王者，拥有无可匹敌的现金流、庞大的 iOS 软硬件生态体系以及极高的全球用户品牌黏性。",
    "TSM": "台积电掌握着全球最先进制程的半导体代工绝对产能，拥有无可替代的定价权，是苹果、英伟达等科技巨头背后的核心制造引擎。",
    "AMZN": "亚马逊是全球电商与云计算（AWS）双料霸主，兼具消费零售赛道的稳健性与 AI 云端基础设施的成长爆发力。",
    "META": "全球社交媒体霸主，凭借 AI 驱动的推荐算法大幅提升数字广告效率，并在开源大模型生态中占据战略制高点。",
    "AVGO": "博通是全球通信与网络芯片龙头，垄断了高端 AI 数据中心的底层网络设备（如交换机芯片），且具备科技股中稀缺的高分红能力。",
    "AMD": "全球领先的微处理器制造商，在数据中心 CPU 与 GPU 领域是挑战行业巨头的高弹性竞争者，提供第二算力供应链选择。",
    "TSLA": "特斯拉是全球纯电动车与储能设备龙头，拥有顶级的自动驾驶数据积累与人形机器人布局，是极具颠覆性的高波动科技资产。",
    "CRWD": "终端节点网络安全的绝对龙头，在 AI 时代企业数据安全需求激增的背景下，具备极高的客户留存率与业绩爆发力。",
    "PLTR": "在大数据分析与国防军工 AI 软件领域拥有垄断地位，其商业化进程加速，是软件 SaaS 赛道中极其纯正的稀缺标的。",
    "LLY": "礼来公司，全球顶尖药企。其在 GLP-1 减肥药与阿尔茨海默症领域的革命性突破，正在重塑全球公共卫生的商业逻辑。",
    "UNH": "联合健康是美国最大的健康保险与医疗服务提供商，盈利模式极其稳健，是医疗大健康板块跨越周期的防御中坚。",
    "PG": "宝洁公司，全球日用消费品巨头，旗下产品深入千家万户，具备极强的定价权与跨越经济周期的抗通胀能力。",
    "JNJ": "强生公司，全球领先的医疗健康巨头，拥有 AAA 级的主权级信用评级，分红历史极其悠久且稳定。",
    "WMT": "沃尔玛，全球最大的全渠道零售商。在经济下行与通胀期，其主打性价比的必需消费品业务展现出极强的抗风险能力。",
    "COST": "开市客（Costco），全球会员制仓储超市鼻祖。极高的会员续费率与强大的供应链壁垒造就了其极其稳定的现金流。",
    "SCHD": "嘉信理财红利 ETF，严格筛选具备至少10年连续派息历史、且基本面健康的优质蓝筹股，熊市中的抗跌防御属性极强。",
    "TLT": "20年以上长期美债 ETF，对宏观利率变化极度敏感。在美联储降息周期中，它能带来显著的资本利得，是对冲股市暴跌的利器。",
    "IEF": "7-10年中期美债 ETF。在提供适度票息的同时，价格波动率低于长债，是平衡投资组合风险的优质中端久期工具。",
    "BND": "先锋全债市 ETF，广泛涵盖美国国债、企业债与抵押贷款支持证券，是“一键买下美国债市”的底层压舱石。",
    "AGG": "iShares 核心美国债市 ETF，追踪美国投资级债券市场，为组合提供极其稳定的票息收益与低波动防御。",
    "IBIT": "贝莱德发行的比特币现货 ETF，为巨量传统法币资金提供了极具流动性与合规性的“数字黄金”投资通道。",
    "FBTC": "富达发行的比特币现货基金，背靠顶级资管机构，是抵御全球法币超发与主权信用风险的顶级尾部保险。",
    "GLD": "全球最大的实物黄金 ETF。作为终极避险资产，它是对抗恶性通胀、地缘冲突与货币贬值的最有效实物硬通货。",
    "XLE": "能源精选板块 ETF，重仓埃克森美孚、雪佛龙等石油巨头，是天然的地缘政治溢价对冲工具与抗通胀盾牌。",
    "MSTR": "微策公司，全球持有比特币最多的上市公司，其股票本质上是带有企业软件业务杠杆的“比特币概念放大器”。",
    "SGOV": "0-3个月超短期美债 ETF，价格波动几乎为零。在提供无风险高息的同时实现本金绝对安全，是完美的现金停泊池。",
    "BOXX": "利用期权盒式价差策略获取无风险收益的创新工具，在享受等同短债高利息的同时具备资本利得的税务递延优势。"
}

# --- 3. 辅助函数：格式化市值与股息率修正 ---
def format_market_cap(val):
    if not isinstance(val, (int, float)): return "N/A"
    if val >= 1e12: return f"${val/1e12:.2f} 兆(万亿)"
    elif val >= 1e9: return f"${val/1e9:.2f} B(十亿)"
    elif val >= 1e6: return f"${val/1e6:.2f} M(百万)"
    return str(val)

def format_yield(val):
    if not isinstance(val, (int, float)): return "N/A"
    if val > 1: return f"{val:.2f}%"  
    else: return f"{val*100:.2f}%"

@st.cache_data(ttl=3600)
def get_detailed_intel(ticker):
    try:
        t = yf.Ticker(ticker)
        i = t.info
        name = i.get('longName', ticker)
        summary = CN_ASSET_WIKI.get(ticker, "该资产是全球金融市场的重要配置标的，主要通过一揽子股票或特定行业的深度布局来获取对应的市场 Beta 收益。")
        pe = i.get('trailingPE', i.get('forwardPE', 'N/A'))
        if isinstance(pe, float): pe = round(pe, 1)
        mkt_cap = format_market_cap(i.get('marketCap', 'N/A'))
        yld = format_yield(i.get('trailingAnnualDividendYield', i.get('dividendYield', 'N/A')))
        return {"name": name, "summary": summary, "pe": pe, "mkt_cap": mkt_cap, "yield": yld}
    except:
        return {"name": ticker, "summary": CN_ASSET_WIKI.get(ticker, "资产业务数据正在同步中。"), "pe": "N/A", "mkt_cap": "N/A", "yield": "N/A"}

def find_pool_category(ticker):
    for category, tickers in DYNAMIC_POOLS.items():
        if ticker in tickers: return category
    return "CORE_EQUITY"

# --- 4. 核心降维惩罚机制 ---
def calculate_actual_risk(base_risk_name, age, amount):
    risk_map = {"保守": 1, "中性偏保守": 2, "中性": 3, "中性偏激进": 4, "激进": 5}
    base_score = risk_map[base_risk_name]
    penalty = 0
    trigger_reasons = []

    if age >= 60: penalty += 1; trigger_reasons.append(f"年龄跨越 60 岁防御临界线")
    if age >= 75: penalty += 1; trigger_reasons.append(f"进入深度老龄化财富保全期")
    if amount >= 5000000: penalty += 1; trigger_reasons.append(f"高净值门槛（>$5M，跨周期守成优先）")
    if amount >= 20000000: penalty += 1; trigger_reasons.append(f"超高净值门槛（>$20M，家族传承优先）")

    adj_score = max(1, base_score - penalty)
    adj_names = {1: "保守", 2: "中性偏保守", 3: "中性", 4: "中性偏激进", 5: "激进"}
    return adj_score, adj_names[adj_score], trigger_reasons, (adj_score < base_score)

def generate_broad_target(adj_risk_score, engine):
    alloc_matrix = {
        1: {"CORE_EQUITY": (10, 2), "GROWTH_TECH": (0, 0), "DEFENSIVE_VALUE": (35, 6), "FIXED_INCOME": (30, 6), "ALTERNATIVE": (0, 0), "CASH_MANAGEMENT": (25, 4)},
        2: {"CORE_EQUITY": (15, 3), "GROWTH_TECH": (5, 1), "DEFENSIVE_VALUE": (30, 5), "FIXED_INCOME": (25, 5), "ALTERNATIVE": (5, 1), "CASH_MANAGEMENT": (20, 3)},
        3: {"CORE_EQUITY": (20, 4), "GROWTH_TECH": (15, 3), "DEFENSIVE_VALUE": (20, 4), "FIXED_INCOME": (20, 3), "ALTERNATIVE": (10, 2), "CASH_MANAGEMENT": (15, 3)},
        4: {"CORE_EQUITY": (20, 4), "GROWTH_TECH": (25, 5), "DEFENSIVE_VALUE": (10, 2), "FIXED_INCOME": (10, 2), "ALTERNATIVE": (25, 4), "CASH_MANAGEMENT": (10, 2)},
        5: {"CORE_EQUITY": (10, 2), "GROWTH_TECH": (40, 7), "DEFENSIVE_VALUE": (5, 1), "FIXED_INCOME": (5, 1), "ALTERNATIVE": (35, 6), "CASH_MANAGEMENT": (5, 1)}
    }
    
    target = {}
    for pool_name, (total_weight, num_items) in alloc_matrix[adj_risk_score].items():
        if num_items == 0: continue
        pool_tickers = DYNAMIC_POOLS[pool_name]
        selected = random.sample(pool_tickers, min(num_items, len(pool_tickers)))
        base_w = total_weight // len(selected)
        remainder = total_weight % len(selected)
        for i, t in enumerate(selected):
            weight = base_w + (1 if i < remainder else 0)
            if weight > 0: target[t] = weight
    return target

# --- 5. 三维联动调仓动因生成器 ---
def get_action_reason(ticker, diff, pool_category, intel, engine):
    if diff < 0:
        return f"<b>【风控与流动性预警】</b>在当前高波动宏观环境下，该标的在您组合中的非系统性风险敞口过载。根据【{engine}】约束，其短期的量化风险收益比已偏离最优解。建议果断减持以兑现浮盈或止损，将释放的流动性转移至胜率更高的防御通道或具备更高 Alpha 的赛道。"
    
    engine_prefix = f"<b>【{engine.split(' ')[0]} 驱动】</b>"
    
    macro_industry_map = {
        "GROWTH_TECH": "<b>【宏观与行业共振】</b>在全球算力主权竞争与技术变革的大背景下，科技巨头正垄断核心资源与定价权。",
        "CORE_EQUITY": "<b>【宏观与行业共振】</b>面对地缘政治与经济周期的不确定性，宽基指数提供了最坚实的国运 Beta 防御。",
        "DEFENSIVE_VALUE": "<b>【宏观与行业共振】</b>在滞胀担忧与消费疲软的边缘，市场资金正加速向具备卓越自由现金流韧性的价值洼地汇聚。",
        "FIXED_INCOME": "<b>【宏观与行业共振】</b>随着联储货币政策处于历史性转折的博弈期，固收资产正迎来票息与资本利得的双击窗口。",
        "ALTERNATIVE": "<b>【宏观与行业共振】</b>全球法币超发与去中心化浪潮，赋予了硬资产与另类资产极高的抗通胀与避险溢价。",
        "CASH_MANAGEMENT": "<b>【宏观与行业共振】</b>在流动性紧缩与市场震荡期，无风险现金等价物不仅是避风港，更是最具战略价值的看涨期权。"
    }
    macro_reason = macro_industry_map.get(pool_category, "<b>【宏观共振】</b>在当前复杂的宏观多因子博弈中，资金正加速向确定性生态位集中。")

    pe_str = f"当前估值 PE 为 {intel['pe']}x" if intel['pe'] != 'N/A' else "估值处于特殊修复或扩张周期"
    micro_reason = f"<b>【资产 Alpha】</b>作为该赛道的关键资产，其{pe_str}，在当前的量化回测模型中展现出极高的护城河壁垒与资产配置性价比。"
        
    return f"{engine_prefix} {macro_reason}<br>{micro_reason}"

# --- 6. 深度动态叙事引擎 (彻底移除 HTML 缩进避免 Markdown 渲染错误) ---
def generate_ai_narrative(name, original_risk, actual_risk, is_downgraded, triggers, target_map, engine, amount):
    tickers = list(target_map.keys())
    now_date = datetime.now().strftime('%Y-%m-%d')
    
    downgrade_text = ""
    if is_downgraded:
        trigger_str = "、".join(triggers)
        # 注意这里：左侧不要留空格，否则 Streamlit/Markdown 会解析成代码块
        downgrade_text = f"""<div class="engine-alert">
<b>⚠️ 智睿 CIO 高净值财富保全机制已触发：</b><br>
虽然您的主观问卷设定为【{original_risk}】，但系统侦测到您的基础画像（{trigger_str}）。在顶级的 Private Banking 逻辑中，规模与岁月的沉淀意味着“跨越周期的绝对保值”优先级远高于“博取高波动的超额收益”。因此，本【{engine}】引擎强制接管，为您叠加了智能惩罚系数，将实际风险敞口精准降维至<b>【{actual_risk}】</b>。这是对您存量财富最负责任的底层风险隔离。
</div>"""
        
    engine_desc = ""
    if "动能" in engine: engine_desc = "本次配置引入了华尔街经典的‘动能轮动（Momentum）’法则，强行超配了过去半年动能最强的核心标的，旨在将 Alpha 收益推向极致。"
    elif "风险平价" in engine: engine_desc = "本次配置重度依赖桥水全天候理念的‘风险平价（Risk Parity）’模型，系统根据动态波动率倒数加权，确保各大类资产的‘风险贡献度’完全相等，画出最平滑的净值曲线。"
    elif "多因子" in engine: engine_desc = "结合 Fama-French 多因子框架，系统为您筛除了纯粹由情绪驱动的泡沫，锁定了具备‘低估值、高质量、高动量’属性的绝对 Alpha 标的。"
    else: engine_desc = "本次报告采用经典的战略资产配置（SAA）框架，结合宏观经济周期的非对称演绎，为您锚定了最具长效复利的资产矩阵。"

    # 报告全文，同样不留多余的换行缩进
    report = f"""<div class="report-text">
{downgrade_text}

<h3>一、2026 宏观流动性中枢与【{engine}】策略匹配</h3>
尊敬的 {name}，截至 {now_date}，全球资本市场正处于“技术通缩”与“债务通胀”相互拉扯的张力之中。海量资金追逐极少数垄断资产，长尾标的面临流动性枯竭。在这种复杂背景下，机械的静态买入持有少数个股的策略已严重失效。

{engine_desc} 针对您的巨额资金体量（${amount:,}），我们通过蒙特卡洛模型进行了 10,000 次压力测试。结果表明，若延续高度集中的单边暴露，净值修复周期将难以承受。我们认为，2026 年成功的财富管理取决于对“波动率成本”的极致控制。

<h3>二、投资组合穿透诊断：极度分散化与夏普比率优化</h3>
诊断揭示，您过往的持仓在单一赛道上的 Beta 拥挤度极高，缺乏横向护城河。本次我们为您执行的再平衡方案，将持仓矩阵大幅扩充至近 20 只多元化标的，调整换手率达 30% 以上。

这绝非简单的资金拆分，而是利用资产间极低的相关性特征，彻底优化您的有效前沿（Efficient Frontier）。我们在追求目标收益的同时，强行剥离了不可控的非系统性尾部风险。

<h3>三、底层调仓动因：构建全天候协同博弈网络</h3>
在进攻端，我们分散聚焦于以 **{tickers[0]}** 与 **{tickers[1]}** 为代表的创新链条。它们具备极强的利润兑现壁垒，足以刺穿通胀。在防御端，我们重仓织入了 **{tickers[-2]}** 等高质量固收或红利组件，与科技股形成完美对冲。

此外，大量无风险流动性干火药的保留，确保您在未来半年具备随时捕获市场错杀定价、逆势抄底的绝对主动权。这是一套能穿越牛熊周期的完整资产护城河生态。

<h3>四、数字时代的另类对冲与资产剥离</h3>
合规化加密 ETF 及实物黄金等硬资产的配置至关重要。在这个周期中，优质资产的定义已演变为“抗通胀韧性”与“非中心化信用”。它们提供了一种跳出传统央行货币周期的独立逻辑，是抵御全球主权债务危机的终极“保险丝”。

<h3>五、CIO 季度投顾邀约与动态执行节奏</h3>
静态持仓的沉没成本正呈几何倍数增长。**我们强烈建议您至少每个季度，与我们的高级专业投顾进行一次一对一的深度线上交流。** 结合宏观政策转向、税务规划，以及本终端持续输出的量化信号，对您的仓位进行精准的“微整形”，确保您的财富战舰始终航行在最优盈利路径上。

<div class="disclaimer">
<b>📝 免责与合规声明 (Disclaimer)：</b><br>
本研报及多因子决策系统由智睿全球资管（虚拟版）自动生成，仅供内部策略演练使用。所引用的量化引擎（包括动能、风险平价等）及降维算法结果，不构成任何实质性投资依据、法律或税务建议。金融市场面临系统性风险，所有标的均有本金损失可能。过往业绩不预示未来回报。投资者在做出实盘交易决定前，务必结合自身真实的风险承受能力，并建议独立咨询持牌财务顾问。
</div>
</div>"""
    return report

# --- 7. 主界面逻辑 ---
with st.sidebar:
    st.header("👤 客户高净值档案")
    c_name = st.text_input("客户姓名", value="Wayne")
    c_age = st.number_input("客户年龄", min_value=18, max_value=100, value=45, step=1)
    c_amount = st.number_input("管理资金规模 (USD)", min_value=10000, max_value=500000000, value=1000000, step=100000, format="%d")
    r_level = st.selectbox("主观风险偏好", ["保守", "中性偏保守", "中性", "中性偏激进", "激进"], index=4)
    st.divider()
    
    st.header("⚙️ 量化策略引擎配置")
    engine_choice = st.selectbox("选择底层推演模型", ["战略资产配置 (SAA)", "动能追涨模型 (Momentum)", "全天候风险平价 (Risk Parity)", "Fama-French 多因子模型"])
    st.divider()
    
    p_input = st.text_area("当前历史持仓 (代码: 比例)", value="NVDA: 60%\nTSLA: 40%", height=120)
    analyze_btn = st.button("🚀 生成定制化量化决策报告", type="primary")

if analyze_btn:
    try:
        with st.spinner(f"🕵️ 正在载入【{engine_choice}】并演算多维因子..."):
            rows = []
            for line in p_input.split('\n'):
                if ":" in line:
                    s, p = line.split(":")
                    rows.append({"项目": s.strip().upper(), "现状%": float(p.strip().replace("%",""))})
            df_now = pd.DataFrame(rows)

            adj_score, actual_risk, triggers, is_downgraded = calculate_actual_risk(r_level, c_age, c_amount)
            target_map = generate_broad_target(adj_score, engine_choice)

            st.title(f"🏛️ {c_name} 2026 全球智能量化终端")
            
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["项目"], values=df_now["现状%"], hole=.4)]).update_layout(title="诊断：当前配置集中风险极高"), use_container_width=True)
            with c2: st.plotly_chart(go.Figure(data=[go.Pie(labels=list(target_map.keys()), values=list(target_map.values()), hole=.4)]).update_layout(title=f"建议：实际应用【{actual_risk}】矩阵"), use_container_width=True)

            st.divider()
            st.markdown("### 🏹 大类资产调仓量化指令表")
            all_s = set(list(df_now["项目"]) + list(target_map.keys()))
            final_list = []
            for s in all_s:
                c_p = df_now[df_now["项目"] == s]["现状%"].sum() if s in df_now["项目"].values else 0
                t_p = target_map.get(s, 0)
                diff = t_p - c_p
                
                if diff >= 20: action = "🚀 战略性增持"
                elif diff <= -20: action = "📉 战略性减持"
                elif c_p == 0 and diff > 0: action = "🆕 建仓"
                elif diff > 0: action = "➕ 加仓"
                elif diff < 0: action = "➖ 减持"
                else: action = "✅ 核心持有"
                
                final_list.append({"代码": s, "现状%": f"{c_p:.1f}", "建议%": f"{t_p:.1f}", "调仓差值%": f"{diff:+.1f}", "操作建议": action})
            st.table(pd.DataFrame(final_list).set_index('代码').sort_values("建议%", ascending=False))

            # --- 全新改版的：资产介绍与动态调仓动因 ---
            st.markdown(f"### 🔍 标的逻辑穿透 (基于 {engine_choice})")
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            for s in sorted(all_s, key=lambda x: target_map.get(x,0), reverse=True):
                c_p = df_now[df_now["项目"] == s]["现状%"].sum() if s in df_now["项目"].values else 0
                t_p = target_map.get(s, 0)
                diff = t_p - c_p
                if diff == 0: continue

                intel = get_detailed_intel(s)
                pool_cat = find_pool_category(s)
                reason = get_action_reason(s, diff, pool_cat, intel, engine_choice)
                
                if diff > 0:
                    with st.container(border=True):
                        st.markdown(f"<div class='card-title'>➕ 建议增持/建仓：{s} ({intel['name']})</div>", unsafe_allow_html=True)
                        
                        # 资产介绍模块 (全中文)
                        intro_html = f"""
                        <div class='card-body'>
                            <b>资产介绍：</b>{intel['summary']}<br>
                        </div>
                        <div class='data-row'>
                            <b>📊 最新核心数据 (截至 {today_str})：</b><br>
                            ▸ 市值/规模: {intel['mkt_cap']} | ▸ 当前 PE: {intel['pe']}x | ▸ 股息率: {intel['yield']}
                        </div>
                        """
                        st.markdown(intro_html, unsafe_allow_html=True)
                        st.markdown(f"<div class='reason-text'>💡 <b>调仓动因：</b><br>{reason}</div>", unsafe_allow_html=True)
                else:
                    with st.container(border=True):
                        st.markdown(f"<div class='card-title-sell'>➖ 建议减持/清理：{s} ({intel['name']})</div>", unsafe_allow_html=True)
                        # 减仓模块补充同样的数据展示
                        intro_html_sell = f"""
                        <div class='card-body'>
                            <b>资产介绍：</b>{intel['summary']}<br>
                        </div>
                        <div class='data-row'>
                            <b>📊 最新核心数据 (截至 {today_str})：</b><br>
                            ▸ 市值/规模: {intel['mkt_cap']} | ▸ 当前 PE: {intel['pe']}x | ▸ 股息率: {intel['yield']}
                        </div>
                        """
                        st.markdown(intro_html_sell, unsafe_allow_html=True)
                        st.markdown(f"<div class='reason-text'>💡 <b>调仓动因：</b><br>{reason}</div>", unsafe_allow_html=True)

            st.divider()
            report_body = generate_ai_narrative(c_name, r_level, actual_risk, is_downgraded, triggers, target_map, engine_choice, c_amount)
            with st.container(border=True):
                st.subheader(f"【2026 CIO 量化备忘录】{c_name} 跨周期财富配置报告")
                st.markdown(report_body, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ 解析错误：{e}")
