import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

st.set_page_config(page_title="アクチュアリー2次試験 生保1過去問演習", layout="wide")

SITE_NAME = "アクチュアリー2次試験 生保1過去問演習"
EXAM_DATE = date(2026, 12, 7)
QUESTION_FILE = "questions_normalized.csv"
JST = ZoneInfo("Asia/Tokyo")

@st.cache_data(ttl=1)
def load_questions():
    return pd.read_csv(QUESTION_FILE, encoding="utf-8-sig")

def natural_sort_key(value):
    s = str(value).strip()
    m = re.search(r"\d+", s)
    return (0, int(m.group()), s) if m else (1, s)

def question_type_sort_key(value):
    s = str(value).strip()
    if s == "小問":
        return (0, s)
    if s == "中問":
        return (1, s)
    return (2, s)

def now_jst():
    return datetime.now(JST)

def today_group_info():
    now = now_jst()
    weekday_num = now.weekday()
    return str(weekday_num + 1), ["月", "火", "水", "木", "金", "土", "日"][weekday_num], now

def days_to_exam():
    return (EXAM_DATE - now_jst().date()).days

def reset_answer():
    st.session_state["show_answer"] = False

st.markdown("""
<style>
.block-container {padding-top:0.5rem;padding-bottom:0.6rem;max-width:760px;}
h2{font-size:1.05rem !important;line-height:1.25 !important;margin:0.1rem 0 0.4rem 0 !important;}
.card{border:1px solid #2f3441;border-radius:12px;padding:8px 10px;margin-bottom:8px;}
.metric-small{font-size:1.05rem;font-weight:700;}
div[data-testid="stButton"] > button {min-height:40px;border-radius:10px;font-weight:600;}
div[data-testid="stSelectbox"] label, div[data-testid="stRadio"] label {font-size:0.92rem;}
</style>
""", unsafe_allow_html=True)

df = load_questions()

required = ["id", "章", "問題種別", "問題番号", "問題文", "解答"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"CSVに必要な列が足りません: {', '.join(missing)}")
    st.stop()

for col in ["id", "章", "問題種別", "問題番号", "問題文", "解答", "年度", "曜日グループ", "解説"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

days_left = days_to_exam()
today_group, today_jp, now_tokyo = today_group_info()

st.markdown(f"## {SITE_NAME}")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="card">残り<br><span class="metric-small">{max(days_left,0)}日</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="card">曜日<br><span class="metric-small">{today_jp}</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="card">時刻<br><span class="metric-small">{now_tokyo.strftime("%H:%M")}</span></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("モード", ["今日の課題", "章別", "検索"])

filtered = df.copy()

if menu == "今日の課題" and "曜日グループ" in filtered.columns:
    filtered = filtered[filtered["曜日グループ"] == today_group].copy()

chapter_options = ["すべて"] + sorted([x for x in filtered["章"].unique().tolist() if x], key=natural_sort_key)
chapter = st.sidebar.selectbox("章", chapter_options)
if chapter != "すべて":
    filtered = filtered[filtered["章"] == chapter].copy()

type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
qtype = st.sidebar.selectbox("種別", type_options)
if qtype != "すべて":
    filtered = filtered[filtered["問題種別"] == qtype].copy()

if menu == "検索":
    keyword = st.sidebar.text_input("キーワード")
    if keyword:
        mask = (
            filtered["問題文"].str.contains(keyword, case=False, na=False)
            | filtered["解答"].str.contains(keyword, case=False, na=False)
            | filtered["問題番号"].str.contains(keyword, case=False, na=False)
        )
        filtered = filtered[mask].copy()

filtered["章_sort"] = filtered["章"].map(natural_sort_key)
filtered["種別_sort"] = filtered["問題種別"].map(question_type_sort_key)
sort_cols = ["章_sort", "種別_sort", "id_num", "id"]
if "曜日グループ" in filtered.columns:
    filtered["曜日_sort"] = filtered["曜日グループ"].map(natural_sort_key)
    sort_cols = ["曜日_sort"] + sort_cols
filtered = filtered.sort_values(sort_cols).reset_index(drop=True)

if filtered.empty:
    st.warning("条件に合う問題がありません。")
    st.stop()

valid_ids = filtered["id"].tolist()

if st.session_state.current_id not in valid_ids:
    st.session_state.current_id = valid_ids[0]
    reset_answer()

labels = []
id_by_label = {}
for _, r in filtered.iterrows():
    label = f"問{r['id']} 第{r['章']}章 {r['問題種別']}"
    if str(r["問題番号"]).strip():
        label += f" {r['問題番号']}"
    labels.append(label)
    id_by_label[label] = r["id"]

current_label = next((label for label in labels if id_by_label[label] == st.session_state.current_id), labels[0])

selected = st.selectbox("問題", labels, index=labels.index(current_label), key="question_select")
if st.button("開く", use_container_width=True):
    st.session_state.current_id = id_by_label[selected]
    reset_answer()
    st.rerun()

current_idx = valid_ids.index(st.session_state.current_id)
row = filtered.iloc[current_idx]

st.markdown('<div class="card">', unsafe_allow_html=True)
st.write(row["問題文"])

show_answer = st.checkbox("解答表示", key="show_answer")
if show_answer:
    st.write("---")
    st.write(row["解答"])
    if "解説" in row and str(row["解説"]).strip():
        st.write(row["解説"])
st.markdown('</div>', unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("←", use_container_width=True, key="prev_btn"):
        if current_idx > 0:
            st.session_state.current_id = valid_ids[current_idx - 1]
            reset_answer()
            st.rerun()
with col_next:
    if st.button("→", use_container_width=True, key="next_btn"):
        if current_idx < len(valid_ids) - 1:
            st.session_state.current_id = valid_ids[current_idx + 1]
            reset_answer()
            st.rerun()
