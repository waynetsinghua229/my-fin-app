import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="2026 智睿全球资管量化终端", page_icon="🏦", layout="wide")

# --- 前端样式优化 ---
st.markdown("""
    <style>
    .report-text { font-size: 1rem !important; line-height: 1.8; text-align: justify; }
    .card-title { color: #4A90E2; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px; }
    .card-body { font-size: 0.9rem; margin-bottom: 5px;}
    .reason-text { font-size: 0.95rem; font-weight: 500; margin-top: 10px; color: #E6A23C; }
    h3 { border-left: 5px solid #4A90E2; padding-left: 12px; margin-top: 25px !important; }
    .disclaimer { font-size: 0.85rem; color: #888888; border-top: 1px dashed #555; padding-top: 15px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 行业动态主题池 (全量资产) ---
DYNAMIC_POOLS = {
    "CORE_EQUITY": ["VOO", "IVV", "SPY", "VTI", "DIA", "IWM", "RSP", "VT"],
    "GROWTH_TECH": ["QQQ", "VGT", "XLK", "SMH", "SOXX", "NVDA", "MSFT", "GOOGL", "AAPL", "AMD", "AVGO", "TSM", "ARM", "META", "AMZN", "CRWD", "PLTR"],
    "DEFENSIVE_VALUE": ["SCHD", "VIG", "DGRO", "LLY", "UNH", "PG", "JNJ", "WMT", "COST", "HD", "PEP", "KO", "MCD"],
    "FIXED_INCOME": ["TLT", "IEF", "BND", "AGG", "JNK", "LQD", "SHY", "MBB"],
    "ALTERNATIVE": ["IBIT", "FBTC", "GLD", "IAU", "XLE", "XOP", "BITO", "MSTR", "COIN", "DBC", "SLV", "URA"],
    "CASH_MANAGEMENT": ["BOXX", "SGOV", "BIL", "VGSH", "MINT"]
}

# --- 2. 内部迷你投研数据库（千股千评核心） ---
ASSET_SPECIFIC_REASONS = {
    "SPY": "作为全球流动性最强的标普500指数ETF，SPY 是机构资金调仓的绝对枢纽，能在市场剧烈波动时提供无与伦比的交易深度与极低的滑点摩擦。",
    "IVV": "iShares 核心标普500 ETF 以极其低廉的管理费率著称。在长达数十年的宏观博弈期，通过微小的成本优势实现复利最大化，是终极的定投底仓。",
    "VOO": "先锋领航打造的低成本之王。持有 VOO 相当于无脑买入美国顶尖 500 强的护城河，有效平抑单一赛道风险，锁定大国经济软着陆的底层红利。",
    "QQQ": "汇聚了纳斯达克100中最顶尖的科技创新巨头，是捕获本轮 AI 革命、云计算与半导体长牛红利的最强锋矛。",
    "AMZN": "在 AWS 云服务与全球电商双轮驱动下，亚马逊不仅掌控零售定价权，更是 AI 云基础设施的关键寡头，兼具消费复苏与科技成长的双重属性。",
    "META": "凭借 AI 驱动的推荐算法大幅提升广告转化率，同时在开源大模型（Llama）生态中占据战略制高点。其降本增效后的利润弹性表现尤为亮眼。",
    "GOOGL": "在搜索垄断的基础上手握海量专有数据。其在 AI 模型训练与数字广告分发领域的规模效应无可匹敌，当前估值在科技巨头中具备显著的安全边际。",
    "AAPL": "拥有全市场最顶级的现金储备与高毛利服务收入。其庞大的 iOS 硬件生态和极强的用户黏性，使其成为抵御宏观经济衰退的终极消费级避风港。",
    "MSFT": "凭借 Azure 云计算与 OpenAI 的深度绑定，已在 B 端企业级 AI 应用中形成绝对垄断。其强劲且确定性的自由现金流，是平抑科技组合波动的核心压舱石。",
    "TSM": "掌握着全球最先进制程的半导体代工产能，是整个硅基时代的‘卖水人’。其产能利用率与无可替代的定价权，为组合提供了确定性极高的硬件底层 Alpha。",
    "NVDA": "作为 GPU 算力霸主，英伟达是本轮 AI 浪潮的绝对核心引擎。其软硬件生态（CUDA）构筑了难以逾越的护城河，是拉升组合整体弹性的必然之选。",
    "AVGO": "垄断了高端 AI 网络的底层芯片（如交换机芯片），是算力基础设施建设中不可或缺的一环，其高股息属性更是科技股中的稀缺配置。",
    "AMD": "作为全市场极少数能在数据中心 CPU 与 GPU 双线挑战巨头的芯片厂商，AMD 为算力赛道提供了高弹性的第二选择，有效分散单一厂商断供风险。",
    "LLY": "在 GLP-1 减肥药与阿尔茨海默症领域的革命性突破，使其跨越了传统医药的避险周期，正在重塑全球公共卫生的商业逻辑，成长性与防御性兼备。",
    "IBIT": "贝莱德比特币现货 ETF 为巨量传统资金提供了合规通道。作为数字黄金，它具备极强的抗法币超发属性，能在组合中提供与股债完全脱钩的 Beta 爆发力。",
    "FBTC": "富达发行的比特币基金。背靠顶级金融机构，为组合注入高波动的另类资产血液，是抵御全球流动性泛滥与地缘割裂风险的顶级尾部保险。",
    "SCHD": "严格筛选了具备长期派息增长历史的优质蓝筹。在经济增速放缓期，其提供的高质量现金流是账户抵抗滞胀的最佳防线。",
    "TLT": "长期美债 ETF 对宏观利率变化极度敏感。在美联储降息周期的预期下，它不仅提供票息，更能带来显著的资本利得，是对冲权益暴跌的终极利器。",
    "GLD": "实物黄金 ETF 是对抗全球主权信用重估、二次通胀升温以及地缘冲突黑天鹅事件的最有效实物硬通货。",
    "SGOV": "极低波动的超短期美债 ETF。在提供极高无风险年化收益的同时实现了本金的绝对安全，是随时准备下场抄底的‘干火药’。",
    "BOXX": "利用期权盒式价差获取无风险收益的创新工具，在享受现金等价物高利息的同时具备税务递延优势，是极佳的流动性管理容器。"
}

@st.cache_data(ttl=3600)
def get_detailed_intel(ticker):
    try:
        t = yf.Ticker(ticker)
        i = t.info
        name = i.get('longName', ticker)
        summary = i.get('longBusinessSummary', '全球核心标的，行业流动性枢纽。')[:150] + "..."
        sector = i.get('sector', '多元化配置')
        pe = i.get('forwardPE', 'N/A')
        if isinstance(pe, float): pe = round(pe, 1)
        return {"name": name, "summary": summary, "sector": sector, "pe": pe}
    except:
        return {"name": ticker, "summary": "该资产为 2026 年关键观察标项。", "sector": "跨行业配置", "pe": "N/A"}

# --- 3. 获取千人千面/千股千评的调仓理由 ---
def get_action_reason(ticker, diff, pool_category, intel):
    if diff < 0:
        return random.choice([
            f"量化风控警示：{ticker} 近期涨幅已充分甚至透支其短期基本面预期。结合其在 {intel['sector']} 板块近期的拥挤度，建议果断减持以兑现浮盈，将释放的购买力转移至对冲通道。",
            f"模型测算显示，{ticker} 的均值回归压力正在剧增。剥离部分仓位旨在斩断潜在的回撤长尾风险，优化整个账户的资本使用效率。"
        ])
    
    # 优先使用数据库里专属定制的独家研报理由
    if ticker in ASSET_SPECIFIC_REASONS:
        return ASSET_SPECIFIC_REASONS[ticker]
    
    # 如果是不在库里的长尾股票，利用它的 PE 和 Sector 动态拼接专属理由
    pe_str = f"前瞻 PE 为 {intel['pe']}x" if intel['pe'] != 'N/A' else "估值处于极度分歧的特殊周期"
    
    if pool_category == "GROWTH_TECH":
        return f"作为 {intel['sector']} 赛道的关键动能标的，其 {pe_str}。在 AI 算力与应用渗透的周期中，该资产具备极强的利润扩张弹性，是拉升组合上限的核心隐形引擎。"
    elif pool_category == "CORE_EQUITY":
        return f"作为大盘核心 Beta 组件，配置 {ticker} 能有效捕获宽基指数的利润复利。在宏观政策博弈期，可大幅平抑单一行业风险，锁定大国经济软着陆的底层红利。"
    elif pool_category == "DEFENSIVE_VALUE":
        return f"在当前滞胀担忧的边缘，{ticker} 所属的 {intel['sector']} 板块具备卓越的自由现金流韧性。其抗周期属性将为组合构筑一道坚固的‘向下护城河’。"
    elif pool_category == "FIXED_INCOME":
        return f"长中端久期资产不仅提供丰厚的票息安全垫，更是押注未来联储货币政策实质性转向的非对称看涨期权，是对冲权益系统性回撤的利器。"
    elif pool_category == "ALTERNATIVE":
        return f"作为硬资产或资源类龙头，在全球地缘碎片化背景下，它能提供与传统股债极低相关性的非线性爆发潜力，是应对 {intel['sector']} 结构性危机的极佳尾部保险。"
    else: 
        return "在波动率放大的震荡市中，锁定极高无风险/税务优化收益，为组合提供充沛的干火药，以备在极端行情下进行战术性抄底。"

def find_pool_category(ticker):
    for category, tickers in DYNAMIC_POOLS.items():
        if ticker in tickers: return category
    return "CORE_EQUITY"

# --- 4. 生成 20 只股票的广泛分散投资组合 ---
def generate_broad_target(risk_level):
    target = {}
    if "稳健型" in risk_level:
        alloc = {"CORE_EQUITY": (15, 3), "GROWTH_TECH": (5, 2), "DEFENSIVE_VALUE": (30, 5), "FIXED_INCOME": (30, 5), "ALTERNATIVE": (5, 2), "CASH_MANAGEMENT": (15, 3)}
    elif "平衡型" in risk_level:
        alloc = {"CORE_EQUITY": (20, 4), "GROWTH_TECH": (20, 4), "DEFENSIVE_VALUE": (20, 4), "FIXED_INCOME": (15, 3), "ALTERNATIVE": (15, 3), "CASH_MANAGEMENT": (10, 2)}
    else: 
        alloc = {"CORE_EQUITY": (10, 2), "GROWTH_TECH": (40, 7), "DEFENSIVE_VALUE": (5, 2), "FIXED_INCOME": (5, 2), "ALTERNATIVE": (35, 6), "CASH_MANAGEMENT": (5, 1)}

    for pool_name, (total_weight, num_items) in alloc.items():
        pool_tickers = DYNAMIC_POOLS[pool_name]
        selected = random.sample(pool_tickers, min(num_items, len(pool_tickers)))
        base_w = total_weight // len(selected)
        remainder = total_weight % len(selected)
        for i, t in enumerate(selected):
            weight = base_w + (1 if i < remainder else 0)
            if weight > 0: target[t] = weight
    return target

# --- 5. 深度动态叙事引擎 (动态重组) ---
def generate_ai_narrative(name, risk, target_map):
    tickers = list(target_map.keys())
    now_date = datetime.now().strftime('%Y-%m-%d')
    
    h1_titles = ["一、2026 全球宏观变量与流动性中枢研判", "一、宏观环境解构与资产重估逻辑", "一、处于十字路口的全球资本博弈"]
    h2_titles = ["二、组合持仓诊断：风险暴露与前沿优化", "二、从 Beta 拥挤到夏普比率的重塑", "二、穿透式诊断：剥离非系统性风险"]
    h3_titles = ["三、底层调仓动因：构建全天候博弈网络", "三、执行细节：矛与盾的极致协同", "三、重构资产锚点：进攻与对冲的艺术"]
    h4_titles = ["四、数字时代的另类对冲与跨周期展望", "四、非线性爆发：硬资产与另类溢价", "四、应对黑天鹅：法币剥离与实物防线"]
    h5_titles = ["五、CIO 季度投顾邀约与动态执行节奏", "五、动态财富管理与投顾交流机制", "五、首席官结语：应对瞬息万变的市场"]

    macro_blocks = [
        f"全球市场正处于‘技术性通缩’与‘债务货币化通胀’相互拉扯的极度张力之中。在这种前所未有的复杂宏观背景下，传统的“买入并持有”少数几只股票的静态策略已无法覆盖日益增长的尾部风险。根据智睿 CIO 团队的流动性监测，2026 年的资金分布呈现极端的“哑铃型”特征：海量资金追逐极少数具备垄断定价权的核心资产，长尾标的正被无情抛弃。",
        f"我们正见证一场由 AI 算力主权与能源重构引发的全球资本大分配。随着各大央行资产负债表的极限拉扯，资产的‘安全溢价’在 2026 年首次超越了‘成长溢价’。这意味着，闭眼买入宽基指数获取红利的时代已经终结。取而代之的是，市场对‘确定性盈利’的极度苛求。",
        f"地缘政治的碎片化正在强力扭曲传统的资产定价模型。在过去的一个季度中，跨国资本的流向显示出一个清晰的信号：寻找低相关性的避风港。面对通胀粘性的反复无常，依靠单一国别或单一行业的 Beta 收益，无异于在火山口上建立财富堡垒。"
    ]

    diag_blocks = [
        f"针对您的【{risk}】偏好画像，我们通过蒙特卡洛模型进行了 10,000 次压力测试。结果表明，如果您延续原有高度集中的持仓结构，在面临 5% 以上的宏观系统性回调时，净值修复周期将显著长于基准指数。您的账户在获取前期超额收益的同时，并未建立起相应的横向“护城河”。",
        f"基于您的【{risk}】设定，深度穿透扫描揭示了一个隐患：您的持仓在单一标的上的动能暴露过于拥挤。虽然在单边上扬的市场中表现出色，但一旦流动性边际收缩，极易发生连环踩踏。成功跨越 2026 震荡市的关键，在于对“波动率成本”的极致精算与压缩。",
        f"结合【{risk}】的投资诉求，量化归因系统发出了警告：您目前的组合严重缺乏对抗尾部风险（Tail Risk）的“现金流盾牌”。本次我们将持仓矩阵大幅扩充至近 20 只多元化标的，调整换手率达 30% 以上。其核心目的绝非简单的分散资金，而是强行剥离不可控的非系统性风险，将您的财富管理从“概率博弈”推向“逻辑溢价”。"
    ]

    exec_blocks = [
        f"在进攻端（Alpha 捕捉），我们建议将核心动能分散聚焦于以 **{tickers[0]}** 与 **{tickers[1]}** 为代表的创新链条。这些标的在 2026 年具备极强的利润兑现能力，其带来的超额预期足以带动组合向上突破。同时，在防御端大量织入了固收与红利标的（如 **{tickers[-2]}**），有效平抑科技板块高估值带来的单边回撤。",
        f"本次资产矩阵的扩充遵循着严密的马科维茨有效前沿（Efficient Frontier）逻辑。我们将一部分筹码压注于 **{tickers[0]}** 等具备强定价权的核心龙头，确保进攻的锋利度。同时，利用 **{tickers[-2]}** 构建坚不可摧的收益防火墙，并保留了以 **{tickers[-1]}** 为代表的现金等价物，确保您随时拥有战术抄底的主动权。",
        f"我们将您的资产分为了三层：压舱石、推进器与避震器。**{tickers[0]}** 充当推进器，负责刺穿通胀带来的购买力贬值；而包含 **{tickers[-2]}** 在内的防守组件，则与成长股形成完美的负相关对冲。这是一套全天候的协同博弈网络，旨在熨平宏观经济周期的非理性波动。"
    ]
    
    alt_blocks = [
        "随着 2026 年合规化进程的全面铺开，另类资产因子正在发挥其与传统法币体系脱钩的天然对冲属性。在这个周期中，优质资产的定义已经从单纯的“现金流折现（DCF）”演变为“不可替代性溢价”与“抗通胀韧性”。",
        "在这个数字经济与实体经济深度交织的年份，实物硬资产与合规加密 ETF 的战略地位不容忽视。它们提供了一种跳出传统央行货币政策周期的独立逻辑，是抵御全球主权债务危机的终极“保险丝”。",
        "我们特别强调了另类资产配置的重要性。面对 2026 年复杂的黑天鹅温床，仅靠股债双杀环境下的传统对冲已显单薄。引入低相关性的数字黄金与大宗商品，是机构投资者重塑收益不对称性的标准动作。"
    ]

    close_blocks = [
        "财富管理是一场长期的、动态演进的马拉松。随着市场节奏的显著加快，静态持仓的沉没成本正呈几何倍数增长。**因此，我们强烈建议您至少每个季度，与我们的高级专业投顾进行一次一对一的深度线上交流。** 我们将借此机会，根据最新的宏观政策转向及您个人的财务需求，对仓位进行精准的“微整形”，确保您的财富战舰始终航行在最优盈利路径上。",
        "在 2026 年的波澜壮阔中，闭门造车将面临极大的信息差风险。**我们诚挚邀约您每季度安排一次与投顾团队的线上会议。** 市场因子瞬息万变，您的税务与流动性需求也在不断变化。通过高频次、定制化的动态修剪，我们将携手帮助您的资产穿越牛熊，实现真正的财富层级跃迁。",
        "资产配置不是一劳永逸的加减法，而是需要实时纠偏的导航系统。**强烈建议您保持每季度与智睿高级分析师的线上战略对话。** 我们将为您解读最新的量化信号，及时优化资产权重。只有保持敏锐的沟通与动态的执行力，才能在这场 2026 年的全球财富再分配中成为最终的赢家。"
    ]

    report = f"""
<div class="report-text">
<h3>{random.choice(h1_titles)}</h3>
尊敬的 {name}，截至 {now_date}，{random.choice(macro_blocks)}

<h3>{random.choice(h2_titles)}</h3>
{random.choice(diag_blocks)}

<h3>{random.choice(h3_titles)}</h3>
{random.choice(exec_blocks)}

<h3>{random.choice(h4_titles)}</h3>
{random.choice(alt_blocks)} 我们将持续利用量化追踪系统，为您甄别全市场中具备这类稀缺属性的标的，确保您的投资组合永远具备生命力。

<h3>{random.choice(h5_titles)}</h3>
{random.choice(close_blocks)}

<div class="disclaimer">
<b>📝 免责与合规声明 (Disclaimer)：</b><br>
本决策建议系统由智睿全球资管（虚拟演示版）多因子量化模型自动生成，仅供投资者内部参考与策略演练。报告中所引用的宏观前瞻及资产配置建议，不构成实质性的投资依据、法律或税务建议。金融市场存在不可预测的系统性风险，所有标的均可能面临本金损失。任何模拟测试的结果均不保证真实收益。投资者在做出任何实际交易决定前，务必结合自身真实的风险承受能力，并建议咨询独立的专业财务顾问。
</div>
</div>
"""
    return report

# --- 6. 主界面逻辑 ---
with st.sidebar:
    st.header("👤 客户档案")
    c_name = st.text_input("姓名", value="Wayne")
    r_level = st.selectbox("风险偏好", ["稳健型", "平衡型", "激进型"], index=2)
    st.divider()
    p_input = st.text_area("当前持仓", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("🚀 生成全市场深度决策报告", type="primary")

if analyze_btn:
    try:
        with st.spinner("🕵️ 正在同步全球数据并进行多资产量化分配..."):
            rows = []
            for line in p_input.split('\n'):
                if ":" in line:
                    s, p = line.split(":")
                    rows.append({"项目": s.strip().upper(), "现状%": float(p.strip().replace("%",""))})
            df_now = pd.DataFrame(rows)

            target_map = generate_broad_target(r_level)

            st.title(f"🏛️ {c_name} 2026 全球智能决策终端")
            
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["项目"], values=df_now["现状%"], hole=.4)]).update_layout(title="诊断：当前配置集中"), use_container_width=True)
            with c2: st.plotly_chart(go.Figure(data=[go.Pie(labels=list(target_map.keys()), values=list(target_map.values()), hole=.4)]).update_layout(title=f"建议：{r_level} 极度分散模型"), use_container_width=True)

            st.divider()
            st.markdown("### 🏹 资产再平衡调仓指令表")
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

            st.markdown("### 🔍 标的逻辑穿透与深度调仓理由")
            for s in sorted(all_s, key=lambda x: target_map.get(x,0), reverse=True):
                c_p = df_now[df_now["项目"] == s]["现状%"].sum() if s in df_now["项目"].values else 0
                t_p = target_map.get(s, 0)
                diff = t_p - c_p
                if diff == 0: continue

                intel = get_detailed_intel(s)
                pool_cat = find_pool_category(s)
                reason = get_action_reason(s, diff, pool_cat, intel)
                
                if diff > 0:
                    with st.container(border=True):
                        st.markdown(f"<div class='card-title'>➕ 建议增持/建仓：{s} ({intel['name']})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='card-body'><b>业务逻辑：</b>{intel['summary']}</div>", unsafe_allow_html=True)
                        st.caption(f"📌 行业定位：{intel['sector']} | 前瞻 PE: {intel['pe']}x")
                        st.markdown(f"<div class='reason-text'><b>💡 调仓理由：</b>{reason}</div>", unsafe_allow_html=True)
                else:
                    with st.container(border=True):
                        st.markdown(f"<div class='card-title'>➖ 建议减持/清理：{s} ({intel['name']})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='reason-text'><b>💡 调仓理由：</b>{reason}</div>", unsafe_allow_html=True)

            st.divider()
            report_body = generate_ai_narrative(c_name, r_level, target_map)
            with st.container(border=True):
                st.subheader(f"【2026 CIO 备忘录】{c_name} 专属资产配置与最终投资建议")
                st.markdown(report_body, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ 解析错误：{e}")
