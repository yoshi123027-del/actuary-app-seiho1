import re
import streamlit as st
import pandas as pd

st.set_page_config(page_title="アクチュアリー生保2次 過去問演習", layout="wide")

@st.cache_data(ttl=1)
def load_data():
    return pd.read_csv("questions_normalized.csv", encoding="utf-8-sig")

def natural_sort_key(value):
    s = str(value).strip()
    m = re.search(r"\d+", s)
    if m:
        return (0, int(m.group()), s)
    return (1, s)

def question_type_sort_key(value):
    s = str(value).strip()
    if s == "小問":
        return (0, s)
    if s == "中問":
        return (1, s)
    return (2, s)

def reset_answer_visibility():
    st.session_state["show_answer"] = False

df = load_data()

required_cols = ["id", "科目", "章", "問題種別", "問題番号", "問題文", "解答"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"CSVに必要な列が足りません: {', '.join(missing)}")
    st.info("必要列: id, 科目, 章, 問題種別, 問題番号, 問題文, 解答")
    st.stop()

for col in ["id", "科目", "章", "問題種別", "年度", "問題番号", "問題文", "解答", "解説"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False

st.title("アクチュアリー生保2次 過去問演習")

# --- サイドバー ---
subject_options = sorted([x for x in df["科目"].unique().tolist() if x])
subject = st.sidebar.selectbox("科目", subject_options)

subject_df = df[df["科目"] == subject].copy()

chapter_options = ["すべて"] + sorted(
    [x for x in subject_df["章"].unique().tolist() if x],
    key=natural_sort_key
)
chapter = st.sidebar.selectbox("章", chapter_options)

chapter_df = subject_df.copy()
if chapter != "すべて":
    chapter_df = chapter_df[chapter_df["章"] == chapter].copy()

question_type_options = ["すべて"] + sorted(
    [x for x in chapter_df["問題種別"].unique().tolist() if x],
    key=question_type_sort_key
)
question_type = st.sidebar.selectbox("小問 / 中問", question_type_options)

filtered = chapter_df.copy()
if question_type != "すべて":
    filtered = filtered[filtered["問題種別"] == question_type].copy()

if "年度" in filtered.columns:
    valid_years = [y for y in filtered["年度"].unique().tolist() if y]
    year_options = ["すべて"] + sorted(valid_years)
    year = st.sidebar.selectbox("年度", year_options)
    if year != "すべて":
        filtered = filtered[filtered["年度"] == year].copy()

filtered["章_sort"] = filtered["章"].map(natural_sort_key)
filtered["問題種別_sort"] = filtered["問題種別"].map(question_type_sort_key)

filtered = filtered.sort_values(
    by=["章_sort", "問題種別_sort", "id_num", "id"]
).reset_index(drop=True)

st.write(f"問題数: {len(filtered)}")

if filtered.empty:
    st.warning("条件に合う問題がありません。CSVの科目・章・問題種別・年度を確認してください。")
    st.stop()

valid_ids = filtered["id"].tolist()

if "current_id" not in st.session_state or st.session_state.current_id not in valid_ids:
    st.session_state.current_id = valid_ids[0]
    reset_answer_visibility()

# 問題選択ラベル作成
filtered["選択ラベル"] = filtered.apply(
    lambda row: f"{row['id']} | 第{row['章']}章 {row['問題種別']} {row['問題番号']}",
    axis=1
)

label_by_id = dict(zip(filtered["id"], filtered["選択ラベル"]))
id_by_label = dict(zip(filtered["選択ラベル"], filtered["id"]))
valid_labels = filtered["選択ラベル"].tolist()

col1, col2 = st.columns([1, 4])

with col1:
    if st.button("ランダム出題"):
        st.session_state.current_id = filtered.sample(1).iloc[0]["id"]
        reset_answer_visibility()
        st.rerun()

with col2:
    current_label = label_by_id[st.session_state.current_id]
    selected_label = st.selectbox(
        "問題選択",
        valid_labels,
        index=valid_labels.index(current_label)
    )
    if st.button("表示"):
        new_id = id_by_label[selected_label]
        if new_id != st.session_state.current_id:
            st.session_state.current_id = new_id
            reset_answer_visibility()
        st.rerun()

current_index_for_nav = valid_ids.index(st.session_state.current_id)
nav1, nav2 = st.columns(2)

with nav1:
    if st.button("← 前へ", use_container_width=True):
        if current_index_for_nav > 0:
            st.session_state.current_id = valid_ids[current_index_for_nav - 1]
            reset_answer_visibility()
            st.rerun()

with nav2:
    if st.button("次へ →", use_container_width=True):
        if current_index_for_nav < len(valid_ids) - 1:
            st.session_state.current_id = valid_ids[current_index_for_nav + 1]
            reset_answer_visibility()
            st.rerun()

current_rows = filtered[filtered["id"] == st.session_state.current_id]

if current_rows.empty:
    st.session_state.current_id = valid_ids[0]
    reset_answer_visibility()
    current_rows = filtered[filtered["id"] == st.session_state.current_id]

row = current_rows.iloc[0]

current_index = valid_ids.index(st.session_state.current_id) + 1
total_count = len(valid_ids)
remaining_count = total_count - current_index
progress_ratio = current_index / total_count if total_count else 0

st.markdown("### 進捗")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("現在位置", f"{current_index} / {total_count}")
with m2:
    st.metric("残り問題数", f"{remaining_count}題")
with m3:
    st.metric("進捗率", f"{progress_ratio * 100:.0f}%")
st.progress(progress_ratio)

title = f"{row['科目']} 第{row['章']}章 {row['問題種別']} {row['問題番号']}"
if "年度" in row and row["年度"]:
    title = f"{row['年度']}年 " + title
st.subheader(title)

st.markdown("## 問題")
st.write(row["問題文"])

show_answer = st.checkbox("解答を表示", key="show_answer")

if show_answer:
    st.markdown("## 解答")
    st.write(row["解答"])

    if "解説" in row and str(row["解説"]).strip():
        st.markdown("## 解説")
        st.write(row["解説"])
