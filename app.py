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
    return (0, value) if value=="小問" else (1, value) if value=="中問" else (2, value)

def now_jst():
    return datetime.now(JST)

def today_group_info():
    now = now_jst()
    weekday_num = now.weekday()
    return str(weekday_num+1), ["月","火","水","木","金","土","日"][weekday_num], now

def days_to_exam():
    return (EXAM_DATE - now_jst().date()).days

# --- compact UI ---
st.markdown("""
<style>
.block-container {padding-top:0.6rem;padding-bottom:0.6rem;max-width:760px;}
h2{font-size:1.2rem;margin:0.2rem 0;}
.metric-small{font-size:1.1rem;font-weight:700;}
.card{border:1px solid #eee;border-radius:12px;padding:8px 10px;margin-bottom:6px;}
button{min-height:40px;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

df = load_questions()

for col in ["id","章","問題種別","問題番号","問題文","解答","年度","曜日グループ","解説"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)

df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

if "show_answer" not in st.session_state:
    st.session_state.show_answer=False
if "current_id" not in st.session_state:
    st.session_state.current_id=None

# header
days_left = days_to_exam()
today_group, today_jp, now_tokyo = today_group_info()

st.markdown(f"## {SITE_NAME}")

c1,c2,c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="card">残り<br><span class="metric-small">{max(days_left,0)}日</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="card">曜日<br><span class="metric-small">{today_jp}</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="card">時刻<br><span class="metric-small">{now_tokyo.strftime("%H:%M")}</span></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("モード",["今日の課題","章別","検索"])

filtered = df.copy()

if menu=="今日の課題" and "曜日グループ" in df.columns:
    filtered = filtered[filtered["曜日グループ"]==today_group]

chapter = st.sidebar.selectbox("章",["すべて"]+sorted(df["章"].unique(), key=natural_sort_key))
if chapter!="すべて":
    filtered = filtered[filtered["章"]==chapter]

qtype = st.sidebar.selectbox("種別",["すべて"]+sorted(df["問題種別"].unique(), key=question_type_sort_key))
if qtype!="すべて":
    filtered = filtered[filtered["問題種別"]==qtype]

filtered = filtered.sort_values(["章","問題種別","id_num"]).reset_index(drop=True)

if filtered.empty:
    st.warning("問題なし")
    st.stop()

if st.session_state.current_id not in filtered["id"].tolist():
    st.session_state.current_id = filtered.iloc[0]["id"]

labels = [f"問{r.id} 第{r.章}章 {r.問題種別}" for _,r in filtered.iterrows()]
id_map = dict(zip(labels, filtered["id"]))

selected = st.selectbox("問題", labels, index=labels.index(next(l for l in labels if id_map[l]==st.session_state.current_id)))

if st.button("開く", use_container_width=True):
    st.session_state.current_id = id_map[selected]
    st.session_state.show_answer=False
    st.rerun()

row = filtered[filtered["id"]==st.session_state.current_id].iloc[0]

st.markdown('<div class="card">', unsafe_allow_html=True)
st.write(row["問題文"])

if st.checkbox("解答表示"):
    st.write("----")
    st.write(row["解答"])
st.markdown('</div>', unsafe_allow_html=True)

idx = filtered.index[filtered["id"]==st.session_state.current_id][0]

c1,c2 = st.columns(2)
with c1:
    if st.button("←", use_container_width=True) and idx>0:
        st.session_state.current_id = filtered.iloc[idx-1]["id"]
        st.session_state.show_answer=False
        st.rerun()
with c2:
    if st.button("→", use_container_width=True) and idx<len(filtered)-1:
        st.session_state.current_id = filtered.iloc[idx+1]["id"]
        st.session_state.show_answer=False
        st.rerun()
