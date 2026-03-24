import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

st.set_page_config(page_title="アクチュアリー生保2次 過去問演習", layout="wide")

# =============================
# サイト設定（生保1サイト / 生保2サイトごとにここだけ変更）
# =============================
SITE_NAME = "アクチュアリー生保2次 過去問演習"
EXAM_DATE = date(2026, 12, 8)   # 生保1サイトなら date(2026, 12, 7)
QUESTION_FILE = "questions_normalized.csv"
JST = ZoneInfo("Asia/Tokyo")

# 教科書ページ設定
TEXTBOOK_LINKS = {
    "1": {"summary": "第1章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter1"},
    "2": {"summary": "第2章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter2"},
    "3": {"summary": "第3章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter3"},
    "4": {"summary": "第4章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter4"},
    "5": {"summary": "第5章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter5"},
    "6": {"summary": "第6章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter6"},
    "7": {"summary": "第7章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter7"},
    "8": {"summary": "第8章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter8"},
    "9": {"summary": "第9章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter9"},
    "10": {"summary": "第10章の簡易まとめをここに記載してください。", "download_url": "https://example.com/chapter10"},
}

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

def reset_answer_visibility():
    st.session_state["show_answer"] = False

def now_jst():
    return datetime.now(JST)

def today_group_info():
    now = now_jst()
    weekday_num = now.weekday()  # Mon=0 ... Sun=6
    group = str(weekday_num + 1)
    jp = ["月曜", "火曜", "水曜", "木曜", "金曜", "土曜", "日曜"][weekday_num]
    return group, jp, now

def days_to_exam():
    today_jst = now_jst().date()
    return (EXAM_DATE - today_jst).days

# -----------------------------
# 問題データ読み込み
# -----------------------------
df = load_questions()

required_cols = ["id", "章", "問題種別", "問題番号", "問題文", "解答"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"CSVに必要な列が足りません: {', '.join(missing)}")
    st.info("必要列: id, 章, 問題種別, 問題番号, 問題文, 解答")
    st.stop()

for col in ["id", "章", "問題種別", "年度", "問題番号", "問題文", "解答", "解説", "曜日グループ"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False

if "timer_running" not in st.session_state:
    st.session_state["timer_running"] = False

if "timer_start_ts" not in st.session_state:
    st.session_state["timer_start_ts"] = None

if "study_seconds_today" not in st.session_state:
    st.session_state["study_seconds_today"] = 0

if "study_date_jst" not in st.session_state:
    st.session_state["study_date_jst"] = now_jst().date().isoformat()

# JST日付が変わったらタイマー累計を日次でリセット
current_jst_date = now_jst().date().isoformat()
if st.session_state["study_date_jst"] != current_jst_date:
    st.session_state["study_date_jst"] = current_jst_date
    st.session_state["study_seconds_today"] = 0
    st.session_state["timer_running"] = False
    st.session_state["timer_start_ts"] = None

# -----------------------------
# ヘッダー
# -----------------------------
st.markdown(f"## {SITE_NAME}")

days_left = days_to_exam()
today_group, today_jp, now_tokyo = today_group_info()

if days_left >= 0:
    st.info(
        f"試験まであと **{days_left}日**（試験日: {EXAM_DATE.strftime('%Y-%m-%d')}）"
        f" / 現在時刻: {now_tokyo.strftime('%Y-%m-%d %H:%M')} JST"
    )
else:
    st.warning(
        f"試験日は {EXAM_DATE.strftime('%Y-%m-%d')} でした。"
        f" / 現在時刻: {now_tokyo.strftime('%Y-%m-%d %H:%M')} JST"
    )

has_weekday_group = "曜日グループ" in df.columns

# -----------------------------
# サイドバー
# -----------------------------
menu = st.sidebar.radio(
    "メニュー",
    ["今日の課題", "章ごとに学ぶ", "問題検索", "教科書で学ぶ"]
)

# -----------------------------
# 教科書で学ぶ
# -----------------------------
if menu == "教科書で学ぶ":
    chapter_options = sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    selected_chapter = st.sidebar.selectbox("章", chapter_options)

    st.subheader(f"第{selected_chapter}章 教科書で学ぶ")
    content = TEXTBOOK_LINKS.get(str(selected_chapter), {
        "summary": "この章の簡易まとめはまだ登録されていません。",
        "download_url": ""
    })

    st.markdown("### 簡易まとめ")
    st.write(content["summary"])

    st.markdown("### 教科書リンク")
    if content["download_url"]:
        st.link_button("アクチュアリー会の教科書ダウンロードページへ", content["download_url"])
    else:
        st.info("この章のダウンロードリンクはまだ設定されていません。app.py の TEXTBOOK_LINKS を更新してください。")
    st.stop()

# -----------------------------
# フィルタ
# -----------------------------
filtered = df.copy()
today_total_count = 0
today_remaining_count = 0

if menu == "今日の課題":
    if not has_weekday_group:
        st.warning("CSVに『曜日グループ』列がないため、今日の課題は使えません。")
        st.stop()

    st.info(f"今日は {today_jp} です。曜日グループ {today_group} の問題を出題します。")
    filtered = filtered[filtered["曜日グループ"] == today_group].copy()
    today_total_count = len(filtered)
    today_remaining_count = today_total_count

    chapter_options = ["すべて"] + sorted([x for x in filtered["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options)
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()

    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options)
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

elif menu == "章ごとに学ぶ":
    chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options)
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()

    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options)
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

    if "年度" in filtered.columns:
        valid_years = [y for y in filtered["年度"].unique().tolist() if y]
        year_options = ["すべて"] + sorted(valid_years)
        year = st.sidebar.selectbox("年度", year_options)
        if year != "すべて":
            filtered = filtered[filtered["年度"] == year].copy()

elif menu == "問題検索":
    keyword = st.sidebar.text_input("キーワード")
    chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options)
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()

    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options)
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

    if "年度" in filtered.columns:
        valid_years = [y for y in filtered["年度"].unique().tolist() if y]
        year_options = ["すべて"] + sorted(valid_years)
        year = st.sidebar.selectbox("年度", year_options)
        if year != "すべて":
            filtered = filtered[filtered["年度"] == year].copy()

    if keyword:
        question_mask = filtered["問題文"].str.contains(keyword, case=False, na=False)
        answer_mask = filtered["解答"].str.contains(keyword, case=False, na=False)
        number_mask = filtered["問題番号"].str.contains(keyword, case=False, na=False)
        filtered = filtered[question_mask | answer_mask | number_mask].copy()

# -----------------------------
# 並び替え
# -----------------------------
filtered["章_sort"] = filtered["章"].map(natural_sort_key)
filtered["問題種別_sort"] = filtered["問題種別"].map(question_type_sort_key)

sort_cols = ["章_sort", "問題種別_sort", "id_num", "id"]
if has_weekday_group and "曜日グループ" in filtered.columns:
    filtered["曜日グループ_sort"] = filtered["曜日グループ"].map(natural_sort_key)
    sort_cols = ["曜日グループ_sort"] + sort_cols

filtered = filtered.sort_values(by=sort_cols).reset_index(drop=True)

# -----------------------------
# 今日の課題表示
# -----------------------------
if menu == "今日の課題":
    t1, t2 = st.columns(2)
    with t1:
        st.metric("今日の課題総数", f"{today_total_count}問")
    with t2:
        st.metric("今日の残り課題", f"{today_remaining_count}問")
else:
    st.caption(f"問題数: {len(filtered)}")

# -----------------------------
# 勉強タイマー
# -----------------------------
st.markdown("### 今日の勉強時間")

running_elapsed_seconds = 0
if st.session_state["timer_running"] and st.session_state["timer_start_ts"] is not None:
    running_elapsed_seconds = int(now_tokyo.timestamp() - st.session_state["timer_start_ts"])

display_seconds = st.session_state["study_seconds_today"] + running_elapsed_seconds

timer_col1, timer_col2, timer_col3 = st.columns(3)
with timer_col1:
    hours = display_seconds // 3600
    minutes = (display_seconds % 3600) // 60
    seconds = display_seconds % 60
    st.metric("今日の累計勉強時間", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
with timer_col2:
    if not st.session_state["timer_running"]:
        if st.button("学習開始", use_container_width=True):
            st.session_state["timer_running"] = True
            st.session_state["timer_start_ts"] = now_tokyo.timestamp()
            st.rerun()
    else:
        if st.button("学習終了", use_container_width=True):
            elapsed = int(now_tokyo.timestamp() - st.session_state["timer_start_ts"])
            st.session_state["study_seconds_today"] += max(elapsed, 0)
            st.session_state["timer_running"] = False
            st.session_state["timer_start_ts"] = None
            st.rerun()
with timer_col3:
    st.success("計測中") if st.session_state["timer_running"] else st.info("停止中")

if filtered.empty:
    st.warning("条件に合う問題がありません。")
    st.stop()

valid_ids = filtered["id"].tolist()

if "current_id" not in st.session_state or st.session_state.current_id not in valid_ids:
    st.session_state.current_id = valid_ids[0]
    reset_answer_visibility()

def build_label(row):
    parts = [str(row["id"]), f"第{row['章']}章", str(row["問題種別"])]
    if str(row["問題番号"]).strip():
        parts.append(str(row["問題番号"]))
    return " | ".join(parts)

filtered["選択ラベル"] = filtered.apply(build_label, axis=1)

label_by_id = dict(zip(filtered["id"], filtered["選択ラベル"]))
id_by_label = dict(zip(filtered["選択ラベル"], filtered["id"]))
valid_labels = filtered["選択ラベル"].tolist()

current_label = label_by_id[st.session_state.current_id]
selected_label = st.selectbox("問題選択", valid_labels, index=valid_labels.index(current_label))
if st.button("表示"):
    new_id = id_by_label[selected_label]
    if new_id != st.session_state.current_id:
        st.session_state.current_id = new_id
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

title = f"第{row['章']}章 {row['問題種別']} {row['問題番号']}"
if has_weekday_group and row.get("曜日グループ", "") and menu == "今日の課題":
    title = f"[曜日グループ {row['曜日グループ']}] " + title
if "年度" in row and row["年度"]:
    title = f"{row['年度']}年 " + title
st.subheader(title)

st.markdown("### 問題")
st.write(row["問題文"])

show_answer = st.checkbox("解答を表示", key="show_answer")
if show_answer:
    st.markdown("### 解答")
    st.write(row["解答"])
    if "解説" in row and str(row["解説"]).strip():
        st.markdown("### 解説")
        st.write(row["解説"])

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

st.markdown("---")
st.markdown("### 進捗")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("現在位置", f"{current_index} / {total_count}")
with m2:
    st.metric("残り問題数", f"{remaining_count}題")
with m3:
    st.metric("進捗率", f"{progress_ratio * 100:.0f}%")
st.progress(progress_ratio)
