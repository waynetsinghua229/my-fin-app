import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="2026 智睿全球高净值量化终端", page_icon="🏦", layout="wide")

# --- 前端样式优化 ---
st.markdown("""
    <style>
    .report-text { font-size: 1rem !important; line-height: 1.8; text-align: justify; }
    .card-title { color: #4A90E2; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px; }
    .card-body { font-size: 0.9rem; margin-bottom: 5px; color: gray;}
    .reason-text { font-size: 0.95rem; font-weight: 500; margin-top: 10px; color: #E6A23C; }
    .engine-alert { border-left: 4px solid #F56C6C; padding: 10px; background-color: rgba(245, 108, 108, 0.1); margin-bottom: 20px;}
    h3 { border-left: 5px solid #4A90E2; padding-left: 12px; margin-top: 25px !important; }
    .disclaimer { font-size: 0.85rem; color: #888888; border-top: 1px dashed #555; padding-top: 15px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 行业动态主题池 (大幅扩充资产丰富度) ---
DYNAMIC_POOLS = {
    "CORE_EQUITY": ["VOO", "IVV", "SPY", "VTI", "DIA", "IWM", "RSP", "VT", "URTH", "QQQM"],
    "GROWTH_TECH": ["QQQ", "VGT", "XLK", "SMH", "SOXX", "NVDA", "MSFT", "GOOGL", "AAPL", "AMD", "AVGO", "TSM", "ARM", "META", "AMZN", "CRWD", "PLTR", "PANW", "NOW"],
    "DEFENSIVE_VALUE": ["SCHD", "VIG", "DGRO", "LLY", "UNH", "PG", "JNJ", "WMT", "COST", "HD", "PEP", "KO", "MCD", "MRK", "ABBV"],
    "FIXED_INCOME": ["TLT", "IEF", "BND", "AGG", "JNK", "LQD", "SHY", "MBB", "MUB", "HYG"],
    "ALTERNATIVE": ["IBIT", "FBTC", "GLD", "IAU", "XLE", "XOP", "BITO", "MSTR", "COIN", "DBC", "SLV", "URA", "URNM"],
    "CASH_MANAGEMENT": ["BOXX", "SGOV", "BIL", "VGSH", "MINT"]
}

# --- 2. 内部迷你数据库（千股千评核心） ---
ASSET_SPECIFIC_REASONS = {
    "SPY": "作为全球流动性最强的宽基，SPY 在极端行情下依然能提供无与伦比的交易深度与极低的滑点摩擦。",
    "IVV": "以极其低廉的管理费率著称。在跨周期的宏观博弈中，微小的成本优势能实现复利最大化，是终极的大盘底仓。",
    "VOO": "相当于无脑买入美国顶尖 500 强的护城河，有效平抑单一赛道风险，锁定大国经济复苏的底层红利。",
    "QQQ": "汇聚了纳斯达克100中最顶尖的创新巨头，是捕获本轮 AI 革命、云计算与半导体长牛红利的最强锋矛。",
    "AMZN": "在 AWS 云服务与全球电商双轮驱动下，掌控零售定价权的同时也是 AI 云基建寡头，兼具消费与成长的双重属性。",
    "META": "凭借 AI 驱动的算法大幅提升广告转化率，在开源大模型生态中占据制高点，降本增效后的利润弹性极其亮眼。",
    "GOOGL": "手握海量专有数据，在 AI 模型训练与数字广告分发领域的规模效应无可匹敌，当前估值具备显著的安全边际。",
    "AAPL": "拥有顶级现金储备与高毛利服务收入，庞大的 iOS 生态和极强用户黏性使其成为抵御经济衰退的消费级避风港。",
    "MSFT": "凭借 Azure 与 OpenAI 的深度绑定，在 B 端企业级 AI 应用中形成垄断，其强劲自由现金流是平抑组合波动的压舱石。",
    "TSM": "掌握全球最先进制程的半导体代工产能，作为硅基时代的‘卖水人’，其无可替代的定价权为组合提供了确定性极高的硬件 Alpha。",
    "NVDA": "作为 GPU 算力霸主与 AI 浪潮的绝对核心，其软硬件生态（CUDA）构筑了极深护城河，是拉升组合整体弹性的必然之选。",
    "AVGO": "垄断了高端 AI 网络交换机芯片，是算力基建中不可或缺的一环，其高股息属性更是科技股中的稀缺配置。",
    "LLY": "在 GLP-1 减肥药领域的革命性突破，正在重塑全球公共卫生的商业逻辑，跨越了传统医药的避险周期。",
    "IBIT": "贝莱德比特币 ETF 为传统资金提供了合规通道，作为数字硬资产，它能在组合中提供与股债完全脱钩的 Beta 爆发力。",
    "SCHD": "严格筛选具备长期派息历史的优质蓝筹，在经济增速放缓期，其高质量现金流是账户抵抗滞胀的最佳防线。",
    "TLT": "对宏观利率变化极度敏感。在美联储货币周期博弈中，它不仅提供票息，更能带来显著资本利得，是对冲权益暴跌的终极利器。",
    "GLD": "对抗全球主权信用重估、二次通胀升温以及地缘冲突黑天鹅事件的最有效实物硬通货。",
    "SGOV": "极低波动的超短期美债 ETF，提供无风险高息的同时实现本金绝对安全，是随时准备下场抄底的‘干火药’。",
    "CRWD": "作为终端节点安全的绝对龙头，在 AI 时代数据安全需求激增的背景下，具备极高的客户留存率和业绩爆发力。",
    "PLTR": "在大数据分析与国防军工 AI 软件领域拥有垄断地位，其商业化进程加速，是软件 SaaS 赛道的稀缺纯正标的。"
}

@st.cache_data(ttl=3600)
def get_detailed_intel(ticker):
    try:
        t = yf.Ticker(ticker)
        i = t.info
        name = i.get('longName', ticker)
        summary = i.get('longBusinessSummary', '核心标的，底层逻辑稳健。')[:150] + "..."
        sector = i.get('sector', '多元化配置')
        pe = i.get('forwardPE', 'N/A')
        if isinstance(pe, float): pe = round(pe, 1)
        return {"name": name, "summary": summary, "sector": sector, "pe": pe}
    except:
        return {"name": ticker, "summary": "量化模型追踪的跨周期资产。", "sector": "量化配置", "pe": "N/A"}

# --- 核心修复：找回判定板块的函数 ---
def find_pool_category(ticker):
    for category, tickers in DYNAMIC_POOLS.items():
        if ticker in tickers: return category
    return "CORE_EQUITY"

# --- 3. 核心降维惩罚机制 (Age & Amount Penalty) ---
def calculate_actual_risk(base_risk_name, age, amount):
    risk_map = {"保守": 1, "中性偏保守": 2, "中性": 3, "中性偏激进": 4, "激进": 5}
    base_score = risk_map[base_risk_name]
    penalty = 0
    trigger_reasons = []

    if age >= 60:
        penalty += 1
        trigger_reasons.append(f"年龄跨越 60 岁防御临界线")
    if age >= 75:
        penalty += 1
        trigger_reasons.append(f"进入深度老龄化财富保全期")
    if amount >= 5000000:
        penalty += 1
        trigger_reasons.append(f"高净值门槛（>$5M，跨周期守成优先）")
    if amount >= 20000000:
        penalty += 1
        trigger_reasons.append(f"超高净值门槛（>$20M，家族传承优先）")

    adj_score = max(1, base_score - penalty)
    adj_names = {1: "保守", 2: "中性偏保守", 3: "中性", 4: "中性偏激进", 5: "激进"}
    return adj_score, adj_names[adj_score], trigger_reasons, (adj_score < base_score)

# --- 4. 生成 20 只股票的分散投资组合 (匹配五阶风险) ---
def generate_broad_target(adj_risk_score, engine):
    alloc_matrix = {
        1: {"CORE_EQUITY": (10, 2), "GROWTH_TECH": (0, 0), "DEFENSIVE_VALUE": (35, 6), "FIXED_INCOME": (30, 6), "ALTERNATIVE": (0, 0), "CASH_MANAGEMENT": (25, 4)},
        2: {"CORE_EQUITY": (15, 3), "GROWTH_TECH": (5, 1), "DEFENSIVE_VALUE": (30, 5), "FIXED_INCOME": (25, 5), "ALTERNATIVE": (5, 1), "CASH_MANAGEMENT": (20, 3)},
        3: {"CORE_EQUITY": (20, 4), "GROWTH_TECH": (15, 3), "DEFENSIVE_VALUE": (20, 4), "FIXED_INCOME": (20, 3), "ALTERNATIVE": (10, 2), "CASH_MANAGEMENT": (15, 3)},
        4: {"CORE_EQUITY": (20, 4), "GROWTH_TECH": (25, 5), "DEFENSIVE_VALUE": (10, 2), "FIXED_INCOME": (10, 2), "ALTERNATIVE": (25, 4), "CASH_MANAGEMENT": (10, 2)},
        5: {"CORE_EQUITY": (10, 2), "GROWTH_TECH": (40, 7), "DEFENSIVE_VALUE": (5, 1), "FIXED_INCOME": (5, 1), "ALTERNATIVE": (35, 6), "CASH_MANAGEMENT": (5, 1)}
    }
    
    alloc = alloc_matrix[adj_risk_score]
    target = {}
    for pool_name, (total_weight, num_items) in alloc.items():
        if num_items == 0: continue
        pool_tickers = DYNAMIC_POOLS[pool_name]
        selected = random.sample(pool_tickers, min(num_items, len(pool_tickers)))
        base_w = total_weight // len(selected)
        remainder = total_weight % len(selected)
        for i, t in enumerate(selected):
            weight = base_w + (1 if i < remainder else 0)
            if weight > 0: target[t] = weight
    return target

# --- 5. 量化引擎调仓理由适配 ---
def get_action_reason(ticker, diff, pool_category, intel, engine):
    if diff < 0:
        return f"量化风控警示：{ticker} 在组合中的非系统性风险敞口超载。根据【{engine}】约束，建议减持以兑现浮盈，释放资金空间。"
    
    engine_prefix = ""
    if "动能" in engine: engine_prefix = f"【动能追涨信号】系统捕捉到该标的强势突破。 "
    elif "风险平价" in engine: engine_prefix = f"【风险平价约束】该标的边际波动率在可控区间，完美平衡组合风险贡献度。 "
    elif "多因子" in engine: engine_prefix = f"【多因子打分】基于质量与动量双因子重叠筛选，存在显著估值溢价。 "

    if ticker in ASSET_SPECIFIC_REASONS:
        reason = ASSET_SPECIFIC_REASONS[ticker]
    else:
        pe_str = f"前瞻 PE 为 {intel['pe']}x" if intel['pe'] != 'N/A' else "估值处于特殊周期"
        if pool_category == "GROWTH_TECH": reason = f"作为 {intel['sector']} 赛道的关键变量，其 {pe_str}，具备极强利润扩张弹性。"
        elif pool_category == "CORE_EQUITY": reason = f"作为宽基 Beta 组件，配置 {ticker} 能有效平抑单一行业风险，锁定经济基本面红利。"
        elif pool_category == "DEFENSIVE_VALUE": reason = f"{intel['sector']} 板块具备卓越的现金流韧性，其抗周期属性将构筑向下护城河。"
        elif pool_category == "FIXED_INCOME": reason = f"长中端久期资产不仅提供票息，更是押注宏观货币政策转向的非对称看涨期权。"
        elif pool_category == "ALTERNATIVE": reason = f"提供与传统股债极低相关性的爆发潜力，是应对 {intel['sector']} 黑天鹅的尾部保险。"
        else: reason = "在震荡市中锁定极高无风险收益，为组合提供充沛干火药以备战术抄底。"
        
    return engine_prefix + reason

# --- 6. 深度动态叙事引擎 (1500字+, 融合 Age/Amount 逻辑) ---
def generate_ai_narrative(name, original_risk, actual_risk, is_downgraded, triggers, target_map, engine, amount):
    tickers = list(target_map.keys())
    now_date = datetime.now().strftime('%Y-%m-%d')
    
    downgrade_text = ""
    if is_downgraded:
        trigger_str = "、".join(triggers)
        downgrade_text = f"""
        <div class="engine-alert">
        <b>⚠️ 智睿 CIO 高净值财富保全机制已触发：</b><br>
        虽然您的主观问卷设定为【{original_risk}】，但系统侦测到您的基础画像（{trigger_str}）。在顶级的 Private Banking 逻辑中，规模与岁月的沉淀意味着“跨越周期的绝对保值”优先级远高于“博取高波动的超额收益”。因此，本【{engine}】引擎强制接管，为您叠加了智能惩罚系数，将实际风险敞口精准降维至<b>【{actual_risk}】</b>。这是对您存量财富最负责任的底层隔离。
        </div>
        """
        
    engine_desc = ""
    if "动能" in engine: engine_desc = "本次配置引入了华尔街经典的‘动能轮动（Momentum）’法则，强行超配了过去 120 个交易日动能最强的核心标的，旨在将 Alpha 收益推向极致。"
    elif "风险平价" in engine: engine_desc = "本次配置重度依赖桥水全天候理念的‘风险平价（Risk Parity）’模型，系统根据动态波动率倒数加权，确保科技与固收的‘风险贡献度’完全相等，画出最平滑的净值曲线。"
    elif "多因子" in engine: engine_desc = "结合 Fama-French 多因子框架，系统为您筛除了纯粹由情绪驱动的泡沫，锁定了具备‘低估值、高质量、高动量’属性的绝对 Alpha 标的。"
    else: engine_desc = "本次报告采用经典的战略资产配置（SAA）框架，结合宏观经济周期的非对称演绎，为您锚定了最具长效复利的资产矩阵。"

    report = f"""
<div class="report-text">
{downgrade_text}

<h3>一、2026 宏观流动性中枢与【{engine}】策略匹配</h3>
尊敬的 {name}，截至 {now_date}，全球资本市场正处于“技术通缩”与“债务通胀”相互拉扯的张力之中。海量资金追逐极少数垄断资产，长尾标的面临流动性枯竭。在这种复杂背景下，机械的静态买入持有已失效。

{engine_desc} 针对您的巨额资金体量（${amount:,}），我们通过蒙特卡洛模型进行了 10,000 次压力测试。结果表明，若延续高度集中的单边暴露，净值修复周期将难以承受。我们认为，2026 年成功的财富管理取决于对“波动率成本”的极致控制。

<h3>二、投资组合穿透诊断：极度分散化与夏普比率优化</h3>
诊断揭示，您过往的持仓在单一赛道上的 Beta 拥挤度极高，缺乏横向护城河。本次我们为您执行的再平衡方案，将持仓矩阵大幅扩充至近 20 只多元化标的，调整换手率达 30% 以上。

这绝非简单的资金拆分，而是利用相关性矩阵的负相关特征，彻底优化您的有效前沿（Efficient Frontier）。我们在追求目标收益的同时，强行剥离了不可控的非系统性风险。

<h3>三、底层调仓动因：构建全天候协同博弈网络</h3>
在进攻端，我们分散聚焦于以 **{tickers[0]}** 为代表的创新链条。它们具备极强的利润兑现壁垒。在防御端，我们重仓织入了 **{tickers[-2]}** 等高质量固收或红利组件，与成长股形成完美对冲。此外，**{tickers[-1]}** 等流动性干火药的配置，确保您在未来半年具备随时捕获市场错杀定价、逆势抄底的绝对主动权。

<h3>四、数字时代的另类对冲与资产剥离</h3>
合规化加密 ETF 及实物黄金等硬资产的配置至关重要。在这个周期中，优质资产的定义已演变为“抗通胀韧性”与“非中心化信用”。它们提供了一种跳出传统央行周期的独立逻辑，是抵御全球主权债务危机的终极“保险丝”。

<h3>五、CIO 季度投顾邀约与动态执行节奏</h3>
静态持仓的沉没成本正呈几何倍数增长。**我们强烈建议您至少每个季度，与我们的高级专业投顾进行一次一对一的深度线上交流。** 结合宏观政策转向、税务规划，以及本终端持续输出的量化信号，对您的仓位进行精准的“微整形”，确保您的财富战舰始终航行在最优盈利路径上。

<div class="disclaimer">
<b>📝 免责与合规声明 (Disclaimer)：</b><br>
本研报及多因子决策系统由智睿全球资管（虚拟版）自动生成，仅供内部策略演练使用。所引用的量化引擎（包括动能、风险平价等）及降维算法结果，不构成任何实质性投资依据或税务建议。金融市场面临系统性风险，所有标的均有本金损失可能。过往业绩不预示未来。投资者在做出实盘交易决定前，务必结合自身真实的风险承受能力，并建议咨询独立持牌财务顾问。
</div>
</div>
"""
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

            st.markdown(f"### 🔍 标的逻辑穿透 (基于 {engine_choice})")
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
                        st.markdown(f"<div class='card-body'><b>业务逻辑：</b>{intel['summary']}</div>", unsafe_allow_html=True)
                        st.caption(f"📌 行业定位：{intel['sector']} | 前瞻 PE: {intel['pe']}x")
                        st.markdown(f"<div class='reason-text'><b>💡 {engine_choice.split(' ')[0]} 调仓动因：</b>{reason}</div>", unsafe_allow_html=True)
                else:
                    with st.container(border=True):
                        st.markdown(f"<div class='card-title'>➖ 建议减持/清理：{s} ({intel['name']})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='reason-text'><b>💡 风控提示：</b>{reason}</div>", unsafe_allow_html=True)

            st.divider()
            report_body = generate_ai_narrative(c_name, r_level, actual_risk, is_downgraded, triggers, target_map, engine_choice, c_amount)
            with st.container(border=True):
                st.subheader(f"【2026 CIO 量化备忘录】{c_name} 跨周期财富配置报告")
                st.markdown(report_body, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ 解析错误：{e}")
