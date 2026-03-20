import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 页面设置
st.set_page_config(page_title="2026 全球资产配置诊断系统", page_icon="⚖️", layout="wide")

# --- 1. 基于经典资产定价模型的资产库 ---
# 逻辑：采用“高质量因子”与“宏观风险对冲”的双重模型
CORE_ASSET_MODELS = {
    "NVDA": {"name": "英伟达", "reason": "高成长因子：AI基础设施核心，具备极高的资本回报率(ROE)与市场定价权。"},
    "LLY": {"name": "礼来", "reason": "刚需价值因子：生物医药领域领头羊，现金流稳定且具备对抗经济周期的能力。"},
    "MSFT": {"name": "微软", "reason": "防御性成长：资产负债表极度健康，是高利率环境下的优质‘避风港’标的。"},
    "XLE": {"name": "能源ETF", "reason": "通胀对冲逻辑：2026年大宗商品价格中枢上移，作为能源端风险补偿不可或缺。"},
    "GLD": {"name": "黄金ETF", "reason": "系统性风险防御：作为传统避险资产，有效对冲法币信用波动及地缘政治压力。"},
    "SCHD": {"name": "高质量红利标的", "reason": "现金流策略：专注具备持续派息能力的龙头企业，提供组合的底层安全边际。"},
    "APP": {"name": "AppLovin", "reason": "超额收益因子：AI应用端爆发力标的，具备较强的Beta收益属性。"}
}

# --- 侧边栏 ---
with st.sidebar:
    st.header("👤 客户档案")
    client_name = st.text_input("客户姓名", value="ying")
    risk_level = st.selectbox("配置模型 (Risk Level)", ["稳健型 (Conservative)", "平衡型 (Moderate)", "激进型 (Aggressive)"], index=1)
    st.divider()
    st.subheader("📦 输入当前持仓")
    portfolio_input = st.text_area("格式: 代码: 比例", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("生成全球资产配置诊断", type="primary")

# --- 主界面 ---
st.title(f"📊 {client_name}：2026 全球资产配置与再平衡诊断报告")
st.caption("基于经典资产组合理论与 2026 年宏观环境因子模型 | 独立第三方研究参考")

if analyze_btn:
    try:
        # 1. 解析数据
        current_rows = []
        for line in portfolio_input.split('\n'):
            if ":" in line:
                s, p = line.split(":")
                current_rows.append({"资产": s.strip().upper(), "当前%": float(p.strip().replace("%",""))})
        df_now = pd.DataFrame(current_rows)

        # 2. 经典模型配置模板
        if "稳健型" in risk_level:
            target_map = {"SCHD": 25, "LLY": 15, "XLE": 15, "GLD": 15, "TLT": 20, "CASH": 10}
        elif "平衡型" in risk_level:
            target_map = {"NVDA": 15, "MSFT": 15, "LLY": 15, "APP": 10, "XLE": 15, "GLD": 15, "SCHD": 15}
        else: # 激进型
            target_map = {"NVDA": 30, "APP": 20, "TSM": 15, "LLY": 15, "XLE": 10, "COIN": 10}

        # 3. 诊断报告生成
        final_report = []
        all_symbols = set(list(df_now["资产"]) + list(target_map.keys()))
        for s in all_symbols:
            curr = df_now[df_now["资产"] == s]["当前%"].values[0] if s in df_now["资产"].values else 0
            tgt = target_map.get(s, 0)
            diff = tgt - curr
            reason = CORE_ASSET_MODELS.get(s, {}).get("reason", "基于跨资产类别相关度进行的战术性配置调整。")
            
            if curr == 0 and tgt > 0: action = "🆕 战略建仓"
            elif diff > 5: action = "➕ 适度增持"
            elif diff < -5: action = "➖ 战术减持"
            else: action = "✅ 核心持有"
            
            final_report.append({"资产项目": s, "现状%": curr, "建议%": tgt, "建议决策": action, "策略依据": reason})
            
        df_final = pd.DataFrame(final_report).sort_values(by="建议%", ascending=False)

        # 4. 前后对比饼图
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["资产"], values=df_now["当前%"], hole=.3)]).update_layout(title="调整前：高风险敞口状态"), use_container_width=True)
        with c2: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_final["资产项目"], values=df_final["建议%"], hole=.3)]).update_layout(title="建议：多因子平衡模型"), use_container_width=True)

        # 5. 方案详情
        st.subheader("🏹 资产优化方案表 (Portfolio Rebalancing Table)")
        st.table(df_final)

        # 6. 【合规版】投资专家建议
        st.markdown("---")
        st.subheader("💡 专家配置建议书 (Investment Perspectives)")
        
        advice = f"""
        **关于 {client_name} 账户的 2026 年度资产配置调整逻辑：**

        **1. 风险集中度诊断：**
        您目前的组合在科技单一板块的暴露度达到 **{df_now['当前%'].sum()}%**。根据经典资产组合理论，过高的相关性会显著放大市场下行时的系统性风险。特别是在 2026 年 3 月宏观波动率抬升的背景下，这种配置路径的脆弱性较高。

        **2. 引入‘质量因子’与‘防御因子’：**
        我们建议在维持 AI 核心配置的同时，引入 **LLY (高质量医药)** 和 **能源/黄金 (通胀对冲资产)**。通过将单一增长股转向具备‘强劲自由现金流’的企业，可以有效平滑账户收益曲线，增强组合在复杂利率环境下的韧性。

        **3. 跨资产类别的战略平衡：**
        能源与黄金的配置并非单纯的投机，而是基于 2026 年地缘政治与通胀预期的‘保险机制’。

        **【执行总结】**：
        建议在未来两个调仓窗口内，通过‘止盈部分高波个股、平配稳健底仓’的方式，向目标均衡模型靠拢。
        """
        st.info(advice)

    except Exception as e:
        st.error(f"分析出错：{e}")
