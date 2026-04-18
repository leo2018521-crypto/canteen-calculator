import streamlit as st
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="🍽️ 食堂采购计算器",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .total-amount {
        font-size: 1.5rem;
        color: #d62728;
        font-weight: bold;
    }
    .meal-header {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# 默认菜品价格库（元/斤）
DEFAULT_PRICES = {
    "猪肉": 12, "鸡肉": 15, "牛肉": 35, "鸡蛋": 6,
    "土豆": 2.5, "青椒": 4, "茄子": 3.5, "豆腐": 5,
    "面条": 4, "大米": 3, "白菜": 2, "萝卜": 1.5,
    "西红柿": 4.5, "黄瓜": 3, "豆芽": 2, "南瓜": 2,
    "冬瓜": 1.8, "胡萝卜": 2.5, "洋葱": 3, "芹菜": 4,
    "菠菜": 5, "油菜": 3.5, "香菇": 12, "木耳": 25,
    "腐竹": 15, "海带": 8, "鱼丸": 18, "香肠": 20,
    "培根": 22, "火腿": 16,
}

# 初始化session state
if 'prices' not in st.session_state:
    st.session_state.prices = DEFAULT_PRICES.copy()

# 主标题
st.markdown('<div class="main-header">🍽️ 食堂采购计算器</div>', unsafe_allow_html=True)

# 侧边栏 - 价格管理
with st.sidebar:
    st.header("⚙️ 菜品价格管理")
    st.info("在这里添加或修改菜品单价（元/斤）")
    
    # 新增菜品
    st.subheader("添加新菜品")
    col1, col2 = st.columns(2)
    with col1:
        new_dish = st.text_input("菜品名称", key="new_dish_name")
    with col2:
        new_price = st.number_input("单价(元/斤)", min_value=0.1, value=10.0, step=0.5, key="new_dish_price")
    
    if st.button("➕ 添加菜品", use_container_width=True):
        if new_dish:
            st.session_state.prices[new_dish] = new_price
            st.success(f"✅ 已添加：{new_dish} {new_price}元/斤")
        else:
            st.warning("⚠️ 请输入菜品名称")
    
    # 修改现有价格
    st.subheader("修改价格")
    dish_to_edit = st.selectbox("选择菜品", list(st.session_state.prices.keys()), key="edit_dish")
    if dish_to_edit:
        new_price_val = st.number_input(f"修改 {dish_to_edit} 单价", min_value=0.1, value=float(st.session_state.prices[dish_to_edit]), step=0.5, key="edit_price")
        if st.button("💾 保存修改", use_container_width=True):
            st.session_state.prices[dish_to_edit] = new_price_val
            st.success(f"✅ 已更新：{dish_to_edit} {new_price_val}元/斤")
    
    # 显示当前价格表
    st.subheader("📋 当前价格表")
    price_df = pd.DataFrame(list(st.session_state.prices.items()), columns=["菜品", "单价(元/斤)"])
    st.dataframe(price_df, use_container_width=True, hide_index=True)

# 主界面
st.markdown("---")
people_count = st.number_input("👥 用餐人数", min_value=1, value=150, step=10)
st.markdown("---")

# 三餐输入
meals = ["早餐", "中餐", "晚餐"]
meal_emojis = {"早餐": "🌅", "中餐": "☀️", "晚餐": "🌙"}
meal_data = {}

for meal in meals:
    st.markdown(f'<div class="meal-header">{meal_emojis[meal]} {meal}</div>', unsafe_allow_html=True)
    dishes_for_meal = []
    cols = st.columns(3)
    for i in range(6):
        with cols[i % 3]:
            dish_name = st.selectbox(f"菜品{i+1}", [""] + list(st.session_state.prices.keys()), key=f"{meal}_dish_{i}")
            if dish_name:
                grams = st.number_input(f"克数", min_value=0, value=0, step=100, key=f"{meal}_grams_{i}")
                if grams > 0:
                    price_per_jin = st.session_state.prices[dish_name]
                    amount = people_count * grams * price_per_jin / 500
                    dishes_for_meal.append({"菜品": dish_name, "克数": grams, "单价": price_per_jin, "金额": amount})
    meal_data[meal] = dishes_for_meal
    st.markdown("---")

# 计算结果
st.markdown("## 💰 采购金额汇总")
if st.button("🧮 计算采购金额", type="primary", use_container_width=True):
    total_all = 0
    for meal in meals:
        dishes = meal_data[meal]
        if dishes:
            st.markdown(f"### {meal_emojis[meal]} {meal}")
            df = pd.DataFrame(dishes)
            df["单价"] = df["单价"].apply(lambda x: f"{x}元/斤")
            df["克数"] = df["克数"].apply(lambda x: f"{x}g")
            df["金额"] = df["金额"].apply(lambda x: f"¥{x:,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            meal_total = sum(d["金额"] for d in dishes)
            total_all += meal_total
            st.markdown(f"**{meal}合计：¥{meal_total:,.0f}**")
            st.markdown("---")
    
    if total_all > 0:
        st.markdown(f'<div class="result-box"><div class="total-amount">📊 今日采购总金额：¥{total_all:,.0f}</div><div style="color: #666; margin-top: 10px;">用餐人数：{people_count}人 | 人均成本：¥{total_all/people_count:.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ 请先输入菜品和克数，再点击计算")

st.markdown("---")
st.caption("💡 提示：在左侧边栏可以管理菜品价格 | 克数单位：克(g) | 计算方式：人数×克数×单价÷500")
