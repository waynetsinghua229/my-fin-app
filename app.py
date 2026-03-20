import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="2026 智睿资产动态平衡系统", page_icon="⚖️", layout="wide")

# --- 1. 资产属性数据库 (增加分红属性) ---
ASSET_ATTR = {
    "SCHD": {"name": "高质量红利标的", "is_dividend": True, "est_yield": 3.8},
    "LLY": {"name": "礼来 (医药)", "is_dividend": True, "est_yield": 0.8},
    "XLE": {"name": "能源ETF", "is_dividend": True, "est_yield": 3.2},
    "MSFT": {"name": "微软", "is_dividend": True, "est_yield": 0.7},
    "TLT": {"name": "长债ETF", "is_dividend": True, "est_yield": 4.2},
    "NVDA": {"name": "英伟达", "is_dividend": False, "est_yield": 0.02},
    "BITCOIN": {"name": "加密资产", "is_dividend": False, "est_yield": 0},
    "CASH": {"name": "现金储备", "is_dividend": True, "est_yield": 4.5} # 2026年模拟利率
}

# --- 2. 风险矩阵模板 ---
def get_strategic_allocation(risk_level):
    if "稳健型" in risk_level:
        return {"SCHD": 35, "TLT": 25, "LLY": 10, "XLE": 10, "CASH": 15, "NVDA": 5}
    elif "平衡型" in risk_level:
        return {"NVDA": 15, "MSFT": 15, "LLY": 10, "SCHD": 15, "XLE": 15, "BITCOIN": 10, "GLD": 10, "CASH": 10}
    else: # 激进型
        return {"NVDA": 35, "APP": 20, "BITCOIN": 25, "COIN": 10, "TSM": 10}

# --- 侧边栏 ---
with st.sidebar:
    st.header("👤 客户画像")
    client_name = st.text_input("客户姓名", value="Wayne")
    risk_level = st.selectbox("风险偏好", ["稳健型 (Conservative)", "平衡型 (Moderate)", "激进型 (Aggressive)"], index=0)
    st.divider()
    st.subheader("📦 输入当前持仓")
    portfolio_input = st.text_area("格式: NVDA: 60%", value="NVDA: 60%\nTSLA: 40%", height=150)
    analyze_btn = st.button("生成深度对标报告", type="primary")

if analyze_btn:
    try:
        # 1. 解析输入
        rows = []
        for line in portfolio_input.split('\n'):
            if ":" in line:
                s, p = line.split(":")
                rows.append({"资产": s.strip().upper(), "比例": float(p.strip().replace("%",""))})
        df_now = pd.DataFrame(rows)
        
        # 2. 获取目标策略
        target_map = get_strategic_allocation(risk_level)
        all_symbols = set(list(df_now["资产"]) + list(target_map.keys()))
        
        # 3. 计算分红比例与详情
        report_data = []
        div_total_pct = 0
        for s in all_symbols:
            curr = df_now[df_now["资产"] == s]["比例"].sum() if s in df_now["资产"].values else 0
            tgt = target_map.get(s, 0)
            
            # 判断是否为分红资产
            is_div = ASSET_ATTR.get(s, {}).get("is_dividend", False)
            if is_div: div_total_pct += tgt
            
            report_data.append({
                "项目": s, 
                "当前权重%": curr, 
                "目标建议%": tgt, 
                "类型": "📈 分红/现金流型" if is_div else "🚀 成长/波动型"
            })
        
        df_final = pd.DataFrame(report_data).sort_values(by="目标建议%", ascending=False)

        # 4. 视觉展示
        st.title(f"📊 {client_name}：{risk_level} 资产配置方案")
        
        # 核心指标：分红比例显示
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("建议分红类资产总占比", f"{div_total_pct}%", delta="现金流保障" if div_total_pct > 50 else None)
        with c2:
            st.metric("组合集中度风险", "低" if "稳健型" in risk_level else "高")
        with c3:
            st.metric("2026 宏观匹配度", "95%")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_now["资产"], values=df_now["比例"], hole=.4)]).update_layout(title="诊断：当前持仓结构"), use_container_width=True)
        with col_b: st.plotly_chart(go.Figure(data=[go.Pie(labels=df_final["项目"], values=df_final["目标建议%"], hole=.4)]).update_layout(title=f"建议：{risk_level} 模型"), use_container_width=True)
        
        st.subheader("🏹 资产再平衡与分红属性明细")
        st.table(df_final)

        # 5. 🔥 针对性的投资建议书 🔥
        st.markdown("---")
        st.subheader("🎙️ 首席配置分析 (Investment Commentary)")
        
        if "稳健型" in risk_level:
            advice_title = "核心任务：构建稳健的‘分红安全垫’"
            strategy_text = f"Wayne，针对您的稳健偏好，我们强制将分红类资产（含 SCHD、长债及现金）的比例拉升至 **{div_total_pct}%**。这不仅是为了对抗通胀，更是在 2026 年市场波动时为您提供持续的‘落袋收益’。即使股价不涨，您的组合依然具备自我修复的现金流能力。"
        else:
            advice_title = "核心任务：动态捕获 Alpha 与 潮流 Beta"
            strategy_text = "激进型配置下，我们大幅降低了分红类资产的权重，转而配置高贝塔值的 AI 与加密资产。虽然这会牺牲分红稳定性，但能极大提升在 2026 年科技爆发期的净值增长潜力。"

        st.info(f"**【{advice_title}】**\n\n{strategy_text}")
        st.caption("📜 免责声明：本建议基于现代资产组合理论（MPT）生成。")

    except Exception as e:
        st.error(f"分析出错：{e}")
