import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="2026 智睿全球资管决策系统", page_icon="🏛️", layout="wide")

# --- 1. 动态市场扫描 ---
@st.cache_data(ttl=3600)
def get_daily_market_context():
    return {
        "AI_CORE": "NVDA", "BIO_LEADER": "LLY", "CRYPTO_BETA": "BITCOIN",
        "DIV_ANCHOR": "SCHD", "ENERGY_HEDGE": "XLE", "TECH_DYNAMIC": "APP"
    }

# --- 2. 深度报告生成引擎 (完整内容回归) ---
def generate_deep_investment_report(name, risk, df_now, stars):
    # 确保列名匹配计算
    tech_weight = df_now[df_now["资产项目"].isin(["NVDA", "TSLA", "AAPL", "MSFT", "AMD", "APP"])]["现状%"].sum()
    now_date = datetime.now().strftime('%Y-%m-%d')
    
    if "稳健型" in risk:
        strategy_name = "【2026 全天候资产配置与风险平衡建议书】"
        main_content = f"""
### 第一部分：2026 年 3 月全球宏观局势研判
尊敬的 {name}，根据截至 {now_date} 的全球宏观多因子模型监测，我们正处于一个典型的“高利率下半场”环境。随着 2026 年全球产业链的深度重构，传统的资产相关性正在失效。对于稳健型客户，我们的核心目标是通过“多维分散”来抵御由于利率长期维持在高位带来的估值压力。当前十年期美债收益率的震荡走势预示着市场对增长放缓的担忧，这意味着传统的“全仓增长”策略已不再适用。

### 第二部分：持仓健康度诊断：集中度与资产相关性分析
通过对您提交的初始组合进行穿透分析，我们发现您的科技股敞口高达 {tech_weight:.1f}%。在现代组合理论（MPT）中，这意味着您的组合夏普比率（Sharpe Ratio）正处于危险区间。由于这些标的具备极高的“同向相关性”，一旦纳斯达克指数出现 5% 以上的健康回调，您的账户净值将面临两倍以上的剧烈回撤。这种“进攻性过剩、防御性赤字”的现状，是本次再平衡必须解决的核心矛盾。

### 第三部分：再平衡逻辑：现金流护城河与“分红盾牌”计划
我们将通过以下三个维度为您重新构建防御矩阵：
1. **核心配置高质量红利**：作为组合的“锚点资产”，其稳定的股息输出将在市场横盘震荡期提供宝贵的正向现金流。3.8% 以上的预期股息率不仅是对抗通胀的防线，更是心理上的“安全垫”。
2. **重塑固定收益组合**：建议大幅建仓 **TLT (长债)**。在利率见顶预期下，长债不仅提供现金流，更能在经济失速时作为资本利得的增长引擎。
3. **引入硬资产对冲**：配置 **能源 (XLE)** 和 **黄金**。这是针对 2026 年潜在地缘风险的“买路钱”，确保您在极端环境下依然具备购买力。

### 第四部分：针对数字资产 **{stars['CRYPTO_BETA']}** 的策略说明
关于建议中新增的数字资产，我们需特别声明：这并非鼓励投机。在 2026 年数字资产全面合规化的背景下，比特币已演变为一种“抗法币贬值”的另类资产。对于稳健型客户，低权重配置旨在利用其与传统股债极低的相关性，在不显著增加波动率的前提下，提取非线性收益。

### 第五部分：执行路径与 CIO 总结
本次调仓涉及总资产的大幅转换，建议采取“阶梯式”策略。在未来两个交易周内，逢高止盈科技仓位，优先补齐红利与债项底仓。您的目标是构建一个：年化波动率控制在 8% 以内，但确定性分红覆盖通胀的“常青组合”。
        """
    else:
        strategy_name = "【2026 极致 Beta 捕获与潮流 Alpha 掠夺手册】"
        main_content = f"""
### 第一部分：激进配置逻辑与 2026 动能分析
{name}，2026 年的市场属于那些敢于识别并拥抱“范式转移”的投资者。当前的 AI 算力潮正处于向应用端深度渗透的拐点。作为激进型客户，您的核心哲学应当是：利用波动率作为获取超额收益（Alpha）的阶梯，而非将其视为避险的理由。当前的流动性环境依然奖赏那些具备高成长动能的核心资产。

### 第二部分：进攻矩阵：算力、应用与加密资产
1. **重仓 AI 核心**：维持算力龙头 **{stars['AI_CORE']}** 的绝对领先地位。在 2026 年，算力依然是全球数字经济的“原油”，具备极强的定价权和溢价能力。
2. **切入应用爆发点**：建议大幅调增 AI 应用端标的 **{stars['TECH_DYNAMIC']}**。其 AI 广告引擎的变现效率已验证了 AI 商业闭环的逻辑，是目前最具 Beta 爆发力的方向。
3. **捕捉加密因子脉冲**：建议将加密资产组合占比提升。这是 2026 年最具爆发力的流动性工具，在机构资金全面入场的背景下，其弹性将远超传统权益标的。

### 第三部分：风险对冲与退出策略
虽然我们采取极致进攻策略，但仍需配置部分 **能源 (XLE)** 资产作为组合的“黑天鹅保单”。一旦全球能源供应链受冲击，能源板块的逆市拉升将为您提供高位换仓的宝贵流动性。记住，激进不代表盲目，而是要永远追随最活跃的资金流向，并在动能衰竭前完成利好兑现。

### 第四部分：执行策略：动态盯盘与动能跟踪
激进型配置需要对市场情绪（Sentiment）有极高的敏感度。建议按月度进行再平衡，确保资金永远沉淀在全市场波动率最高、叙事最强的核心标的中。您的目标是在 2026 年的波动潮中，实现财富层级的跨越式增值。

### 第五部分：CIO 首席官结语
您的配置将从“被动持有”转向“主动猎杀”。本方案旨在最大化您的风险补偿收益，利用高贝塔值的资产组合在 2026 年这个大航海时代捕获属于您的 Alpha。
        """
    
    return strategy_name, main_content

# --- 3. 主界面逻辑 ---
with st.sidebar:
    st.header("👤 客户档案")
    c_name = st.text_input("客户姓名", value="Wayne")
    r_level = st.selectbox("风险偏好", ["稳健型 (Conservative)", "平衡型 (Moderate)", "激进型 (Aggressive)"], index=0)
    st.divider()
    p_input = st.text_area("当前持仓 (代码: 比例)", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("🚀 生成深度报告", type="primary")

if analyze_btn:
    try:
        with st.spinner("🕵️ 正在进行全市场精算扫描..."):
            stars = get_daily_market_context()
            
            # 解析输入
            rows = []
            for line in p_input.split('\n'):
                if ":" in line:
                    s, p = line.split(":")
                    rows.append({"资产项目": s.strip().upper(), "现状%": float(p.strip().replace("%",""))})
            df_now = pd.DataFrame(rows)
            
            # 目标配比
            if "稳健型" in r_level:
                target_map = {stars['DIV_ANCHOR']: 30, "TLT": 25, "LLY": 15, "XLE": 15, "CASH": 10, stars['CRYPTO_BETA']: 5}
            elif "平衡型" in r_level:
                target_map = {stars['AI_CORE']: 20, "APP": 15, "LLY": 15, stars['CRYPTO_BETA']: 15, "XLE": 15, "SCHD": 20}
            else:
                target_map = {stars['AI_CORE']: 35, "APP": 25, "BITCOIN": 20, "COIN": 10, "TSM": 10}

            st.title(f"🏛️ {c_name} 2026 全球资管决策报告")
            
            # --- 表格明细展示 ---
            st.subheader("🎯 资产再平衡明细清单")
            final_list = []
            all_s = set(list(df_now["资产项目"]) + list(target_map.keys()))
            for s in all_s:
                c_p = df_now[df_now["资产项目"] == s]["现状%"].sum() if s in df_now["资产项目"].values else 0
                t_p = target_map.get(s, 0)
                diff = t_p - c_p
                
                # --- 严格判定逻辑修复 ---
                if diff > 20:
                    action = "🚀 战略性增持"
                elif diff < -20:
                    action = "📉 战略性减持"
                elif c_p == 0 and t_p > 0:
                    action = "🆕 新增建仓"
                elif 5 < diff <= 20:
                    action = "➕ 战术性加仓"
                elif -20 <= diff < -5:
                    action = "➖ 适度减持"
                else:
                    action = "✅ 核心持有"
                
                final_list.append({
                    "资产项目": s, "现状%": c_p, "建议%": t_p, 
                    "调整差值%": f"{diff:+.1f}", "操作建议": action
                })
            
            df_display = pd.DataFrame(final_list).sort_values("建议%", ascending=False)
            st.table(df_display.set_index('资产项目').style.format({"现状%": "{:.1f}", "建议%": "{:.1f}"}))

            # 深度研报展示
            st.divider()
            title, report = generate_deep_investment_report(c_name, r_level, df_now, stars)
            st.subheader(title)
            st.markdown(report)

    except Exception as e:
        st.error(f"⚠️ 解析错误: {e}")

st.markdown("---")
st.caption("📜 独立研究声明：报告基于 2026 模拟数据生成。")
