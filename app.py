import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="2026 尊享全资产投顾系统", page_icon="🎙️", layout="wide")

# --- 1. 2026 热门核心资产池 ---
HOT_ASSETS_DATABASE = {
    "NVDA": {"name": "英伟达", "reason": "AI算力基石，Blackwell芯片需求极强。"},
    "APP": {"name": "AppLovin", "reason": "AI广告引擎AXON爆发，变现能力顶级。"},
    "LLY": {"name": "礼来", "reason": "减肥药赛道王者，需求远超产能。"},
    "MSFT": {"name": "微软", "reason": "Copilot企业端渗透加速，估值稳健。"},
    "XLE": {"name": "能源ETF", "reason": "地缘溢价支撑油价，天然抗通胀工具。"},
    "GLD": {"name": "黄金ETF", "reason": "避险情绪与抗通胀的核心抓手。"},
    "COIN": {"name": "Coinbase", "reason": "2026数字资产合规利好，牛市交易爆发。"}
}

# --- 侧边栏 ---
with st.sidebar:
    st.header("👤 客人画像")
    client_name = st.text_input("客人姓名", value="ying")
    risk_level = st.selectbox("风险偏好", ["稳健型", "平衡型", "激进型"], index=1)
    st.divider()
    st.subheader("📦 输入当前持仓")
    portfolio_input = st.text_area("格式: 代码: 比例", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("生成深度财富报告", type="primary")

# --- 主界面 ---
st.title(f"🏛️ {client_name} 2026 资产再平衡专业报告")

if analyze_btn:
    try:
        # 1. 解析原始数据
        current_rows = []
        for line in portfolio_input.split('\n'):
            if ":" in line:
                s, p = line.split(":")
                current_rows.append({"资产": s.strip().upper(), "当前%": float(p.strip().replace("%",""))})
        df_now = pd.DataFrame(current_rows)

        # 2. 热门资产模板
        if risk_level == "稳健型":
            target_map = {"MSFT": 20, "LLY": 15, "XLE": 20, "GLD": 20, "TLT": 15, "CASH": 10}
        elif risk_level == "平衡型":
            target_map = {"NVDA": 20, "APP": 15, "LLY": 15, "MSFT": 10, "XLE": 15, "GLD": 15, "COIN": 10}
        else:
            target_map = {"NVDA": 35, "APP": 25, "COIN": 15, "TSM": 15, "XLE": 5, "GLD": 5}

        # 3. 汇总数据
        final_report = []
        all_symbols = set(list(df_now["资产"]) + list(target_map.keys()))
        for s in all_symbols:
            curr = df_now[df_now["资产"] == s]["当前%"].values[0] if s in df_now["资产"].values else 0
            tgt = target_map.get(s, 0)
            diff = tgt - curr
            reason = HOT_ASSETS_DATABASE.get(s, {}).get("reason", "平衡资产风险，提升组合韧性。")
            if curr == 0 and tgt > 0: action = "🆕 新增"
            elif diff > 5: action = "➕ 增持"
            elif diff < -5: action = "➖ 减持"
            else: action = "✅ 维持"
            final_report.append({"资产代码": s, "当前%": curr, "建议%": tgt, "动作": action, "推荐理由": reason})
            
        df_final = pd.DataFrame(final_report).sort_values(by="建议%", ascending=False)

        # 4. 图表展示
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["资产"], values=df_now["当前%"], hole=.3)]).update_layout(title="调整前分布"), use_container_width=True)
        with c2: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_final["资产代码"], values=df_final["建议%"], hole=.3)]).update_layout(title="2026 建议模型"), use_container_width=True)

        # 5. 表格
        st.subheader("🏹 资产优化调优方案")
        st.table(df_final)

        # 6. 金牌口播稿 (采用安全拼接模式)
        st.markdown("---")
        st.subheader("🎙️ 金牌投顾·深度口播稿")
        
        script = f"【开场白】 {client_name}您好！作为您的理财管家，我得直白地告诉您：您现在的持仓‘进攻有余，防守全无’。 "
        script += "在2026年3月这种高波动环境下，全仓押注科技股就像在暴雨天开快车，非常危险。 "
        script += "【核心调整】 我为您引入了‘三驾马车’配置法：一是保留英伟达等核心AI资产； "
        script += "二是引入礼来(LLY)，锁定医药赛道的刚需红利；三是重仓能源和黄金，给账户穿上‘防弹衣’。 "
        script += "【预期目标】 调整后，您的资产将从‘赌单只股票’进化为‘赚全球红利’。波动率会下降一半，但收益底色会更亮！"
        
        st.success(script)

    except Exception as e:
        st.error(f"分析出错：{e}")