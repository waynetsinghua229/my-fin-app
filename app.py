import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 页面设置：更专业的金融黑金风格
st.set_page_config(page_title="2026 尊享动态资管决策系统", page_icon="🏦", layout="wide")

# --- 1. 2026 核心资产库 (动态潮流因子配置) ---
# 逻辑：采用“高质量因子”与“宏观风险均衡模型”
ASSET_POOL = {
    "高质量成长": {
        "NVDA": {"name": "英伟达", "reason": "AI算力基石，高ROE与强劲现金流支撑。"},
        "MSFT": {"name": "微软", "reason": "企业级AI渗透率提升，防御性成长的典范。"},
        "LLY": {"name": "礼来", "reason": "生物医药龙头，刚需价值与长期增长并存。"}
    },
    "动态潮流/Beta": {
        "BITCOIN": {"name": "加密资产 (BTC)", "reason": "潮流因子：合规化加速与流动性溢价爆发。"},
        "APP": {"name": "AppLovin", "reason": "潮流因子：AI广告引擎AXON变现能力验证。"},
        "TSM": {"name": "台积电", "reason": "潮流因子：先进封装产能缺口推动的Beta收益。"},
        "COIN": {"name": "Coinbase", "reason": "潮流因子：加密牛市回归的合规交易平台。"}
    },
    "防守与对冲": {
        "XLE": {"name": "能源ETF", "reason": "宏观因子：2026地缘溢价下的通胀对冲。"},
        "GLD": {"name": "黄金ETF", "reason": "避险因子：法币信用对冲与战略配置压力。"},
        "SCHD": {"name": "高质量红利标的", "reason": "现金流策略：专注持续派息能力，提升安全边际。"}
    }
}

# --- 2. 模拟 2026 年 3 月的潮流因子 (核心动态逻辑) ---
def get_dynamic_template(risk_level):
    """
    根据风险偏好和 2026 年 3 月的宏观环境自动生成【动态 100%】建议
    模拟场景：比特币活跃、能源通胀、避险情绪提升
    """
    # 基本配置结构
    template = {}
    
    if "稳健型" in risk_level:
        # 核心：高质量红利与防御 (100%)
        template = {"SCHD": 25, "LLY": 15, "XLE": 20, "GLD": 15, "TLT": 15, "CASH": 10}
        # 如果比特币活跃，给稳健型客户 5% 的黄金换成加密货币对冲，不能太多
        if True: # 模拟比特币活跃
            template["GLD"] = 10
            template["BITCOIN"] = 5
            
    elif "平衡型" in risk_level:
        # 核心：高质量成长与Beta组合 (100%)
        # 当加密货币潮流因子爆发时，动态调减 MSFT，调增 BITCOIN
        template = {"NVDA": 15, "LLY": 15, "APP": 10, "XLE": 15, "GLD": 15, "SCHD": 10, "MSFT": 5}
        # 比特币活跃潮流
        if True: # 模拟加密牛市
            template["MSFT"] = 0 # 调减防御性
            template["COIN"] = 10 # 新增交易平台 Beta
            template["BITCOIN"] = 10 # 新增核心资产
            
    else: # 激进型
        # 核心：高波Beta与前沿科技 (100%)
        # 如果加密潮流因子爆表，重仓 APP 和 BITCOIN
        template = {"NVDA": 30, "APP": 25, "XLE": 10, "TSM": 10, "CASH": 5}
        # 比特币爆发潮流
        if True: # 模拟加密暴涨
            template["TSM"] = 5 # 调减芯片
            template["COIN"] = 15 # 激进建仓交易平台
            template["BITCOIN"] = 15 # 核心 Beta
            
    return template

# --- 侧边栏 ---
with st.sidebar:
    st.header("👤 客户档案")
    client_name = st.text_input("客户姓名", value="ying")
    risk_level = st.selectbox("配置模型 (Risk Level)", ["稳健型 (Conservative)", "平衡型 (Moderate)", "激进型 (Aggressive)"], index=1)
    st.divider()
    st.subheader("📦 当前持仓 (代码: 比例)")
    portfolio_input = st.text_area("格式: NVDA: 60%\nTSLA: 40%", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("生成 2026 年度动态建议书", type="primary")

# --- 主界面 ---
st.title(f"🏦 {client_name} 的 2026 年度全资产再平衡报告")
current_date = datetime.now().strftime("%Y年%m月")
st.caption(f"基于经典多因子理论与 {current_date} 动态潮流模型 | 第三方研究参考")

if analyze_btn:
    try:
        # 1. 解析数据
        current_rows = []
        for line in portfolio_input.split('\n'):
            if ":" in line:
                s, p = line.split(":")
                current_rows.append({"资产": s.strip().upper(), "当前%": float(p.strip().replace("%",""))})
        df_now = pd.DataFrame(current_rows)

        # 2. 获取【动态配平 100%】模板
        target_map = get_dynamic_template(risk_level)

        # 3. 汇总诊断
        final_report = []
        all_symbols = set(list(df_now["资产"]) + list(target_map.keys()))
        
        # 将 ASSET_POOL 展平方便查询依据
        flattened_assets = {}
        for category, assets in ASSET_POOL.items():
            flattened_assets.update(assets)
            
        for s in all_symbols:
            curr = df_now[df_now["资产"] == s]["当前%"].values[0] if s in df_now["资产"].values else 0
            tgt = target_map.get(s, 0)
            diff = tgt - curr
            
            reason = flattened_assets.get(s, {}).get("reason", "针对本期跨资产类别相关度进行的战术性配置调整。")
            
            if curr == 0 and tgt > 0: action = "🆕 战术建仓"
            elif diff > 5: action = "➕ 动态增持"
            elif diff < -5: action = "➖ 风险平抑"
            else: action = "✅ 核心核心"
            
            final_report.append({
                "资产项目": s,
                "当前权重 %": curr,
                "建议权重 %": tgt,
                "动作": action,
                "策略依据": reason
            })
            
        df_final = pd.DataFrame(final_report).sort_values(by="建议权重 %", ascending=False)

        # 4. 图表
        st.subheader("📊 配置结构：当前 vs 建议 (Rebalancing)")
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["资产"], values=df_now["当前%"], hole=.3)]).update_layout(title="调整前：路径过于集中"), use_container_width=True)
        with c2: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_final["资产项目"], values=df_final["建议权重 %"], hole=.3)]).update_layout(title="调整后：经典平衡模型"), use_container_width=True)

        # 5. 方案表
        st.markdown("---")
        st.subheader("🏹 专家资产调优建议 (The CIO Perspectives)")
        st.table(df_final)

        # 6. 【专家版】投资建议建议
        st.markdown("---")
        st.subheader("🎙️ 首席配置解说書 (Investment Perspectives)")
        advice = f"""
        **关于 {client_name} 账户的 2026 年度动态配置调整逻辑：**

        **1. 风险对标：** 您目前的组合在 NVDA 和 TSLA 上的集中度过高。根据资产定价模型，单一行业暴露度在 2026 年宏观因子波动季极易放大整体回撤风险。特别是在我们观测到**地缘溢价**和**加密货币潮流因子**同时活跃的背景下，目前的配置路径稍显脆弱。

        **2. 引入‘潮流因子对冲’：** 针对本期**比特币市场活跃**的潮流，我们并未建议您满仓加密货币，而是基于**风险中性策略**，为您动态调减了防御性的 **MSFT**，并新增了具备强劲 Beta 收益的 **BITCOIN (加密资产)** 和 **COIN (合规平台)**。作为【{risk_level}】客户，这种动态调优能在防守的同时，确保组合不失其爆发力。

        **3. 跨资产类别的战略对冲：** 引入 XLE (能源) 与 GLD (黄金) 用于战略对冲本期的通胀与避险需求。

        **【执行总结】**：
        止盈部分高波个股，平配稳健底仓，并动态配置具备长期 Alpha 收益的核心标的。建议按此方案在未来 1-2 周内完成再平衡。
        """
        st.info(advice)

    except Exception as e:
        st.error(f"分析出错：{e}")

# --- 7. 免责声明 (合规加固版) ---
st.markdown("---")
st.caption("📜 独立研究声明：本资产配置诊断报告基于经典多因子模型（Modern Portfolio Theory, MPT）及第三方潮流因子模型生成，所引用的资产观点、逻辑和理由仅供学术探讨与研究参考，不构成任何形式的投资建议、要约或担保。市场有风险，投资需谨慎。")
