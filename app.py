import re
from datetime import datetime, date
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="アクチュアリー生保2次 過去問演習", layout="wide")

SITE_NAME = "アクチュアリー生保2次 過去問演習"
EXAM_DATE = date(2026, 12, 8)
FLAGS_FILE = "study_flags.csv"
STUDY_LOG_FILE = "study_time_log.csv"
QUESTION_FILE = "questions_normalized.csv"

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

def today_group_info():
    weekday_num = datetime.now().weekday()
    group = str(weekday_num + 1)
    jp = ["月曜", "火曜", "水曜", "木曜", "金曜", "土曜", "日曜"][weekday_num]
    return group, jp

def days_to_exam():
    return (EXAM_DATE - date.today()).days

def load_flags():
    path = Path(FLAGS_FILE)
    if not path.exists():
        return pd.DataFrame(columns=["user_name", "id", "status", "updated_at"])
    try:
        flags = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=["user_name", "id", "status", "updated_at"])
    for col in ["user_name", "id", "status", "updated_at"]:
        if col not in flags.columns:
            flags[col] = ""
    flags["user_name"] = flags["user_name"].fillna("").astype(str).str.strip()
    flags["id"] = flags["id"].fillna("").astype(str).str.strip()
    flags["status"] = flags["status"].fillna("未解答").astype(str).str.strip()
    flags["updated_at"] = flags["updated_at"].fillna("").astype(str).str.strip()
    return flags[["user_name", "id", "status", "updated_at"]]

def save_flags(flags_df):
    flags_df.to_csv(FLAGS_FILE, index=False, encoding="utf-8-sig")

def get_user_flag_map(flags_df, user_name):
    user_df = flags_df[flags_df["user_name"] == user_name].copy()
    if user_df.empty:
        return {}
    return dict(zip(user_df["id"], user_df["status"]))

def update_flag(user_name, question_id, status):
    flags = load_flags()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question_id = str(question_id)
    mask = (flags["user_name"] == user_name) & (flags["id"] == question_id)
    if mask.any():
        flags.loc[mask, "status"] = status
        flags.loc[mask, "updated_at"] = now_str
    else:
        flags = pd.concat([flags, pd.DataFrame([{
            "user_name": user_name,
            "id": question_id,
            "status": status,
            "updated_at": now_str
        }])], ignore_index=True)
    save_flags(flags)

def load_study_log():
    path = Path(STUDY_LOG_FILE)
    if not path.exists():
        return pd.DataFrame(columns=["user_name", "study_date", "seconds"])
    try:
        log_df = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=["user_name", "study_date", "seconds"])
    for col in ["user_name", "study_date", "seconds"]:
        if col not in log_df.columns:
            log_df[col] = ""
    log_df["user_name"] = log_df["user_name"].fillna("").astype(str).str.strip()
    log_df["study_date"] = log_df["study_date"].fillna("").astype(str).str.strip()
    log_df["seconds"] = pd.to_numeric(log_df["seconds"], errors="coerce").fillna(0).astype(int)
    return log_df[["user_name", "study_date", "seconds"]]

def save_study_log(log_df):
    log_df.to_csv(STUDY_LOG_FILE, index=False, encoding="utf-8-sig")

def add_study_seconds(user_name, seconds_to_add):
    if seconds_to_add <= 0:
        return
    log_df = load_study_log()
    today_str = date.today().isoformat()
    mask = (log_df["user_name"] == user_name) & (log_df["study_date"] == today_str)
    if mask.any():
        log_df.loc[mask, "seconds"] = log_df.loc[mask, "seconds"] + int(seconds_to_add)
    else:
        log_df = pd.concat([log_df, pd.DataFrame([{
            "user_name": user_name,
            "study_date": today_str,
            "seconds": int(seconds_to_add)
        }])], ignore_index=True)
    save_study_log(log_df)

def get_today_study_seconds(user_name):
    log_df = load_study_log()
    today_str = date.today().isoformat()
    mask = (log_df["user_name"] == user_name) & (log_df["study_date"] == today_str)
    if not mask.any():
        return 0
    return int(log_df.loc[mask, "seconds"].sum())

def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}時間{minutes}分"
    if minutes > 0:
        return f"{minutes}分{secs}秒"
    return f"{secs}秒"

df = load_questions()
required_cols = ["id", "章", "問題種別", "問題番号", "問題文", "解答"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"CSVに必要な列が足りません: {', '.join(missing)}")
    st.stop()

for col in ["id", "章", "問題種別", "年度", "問題番号", "問題文", "解答", "解説", "曜日グループ"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()
df["id"] = df["id"].astype(str).str.strip()
df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

if "timer_running" not in st.session_state:
    st.session_state["timer_running"] = False
if "timer_start_ts" not in st.session_state:
    st.session_state["timer_start_ts"] = None

st.markdown(f"## {SITE_NAME}")
d = days_to_exam()
if d >= 0:
    st.info(f"試験まであと **{d}日**（試験日: {EXAM_DATE.strftime('%Y-%m-%d')}）")

has_weekday_group = "曜日グループ" in df.columns
today_group, today_jp = today_group_info()

st.sidebar.markdown("### ユーザー")
user_name = st.sidebar.text_input("ユーザー名", value="guest").strip() or "guest"

flags_df = load_flags()
user_flag_map = get_user_flag_map(flags_df, user_name)
df["学習状況"] = df["id"].map(lambda x: user_flag_map.get(str(x), "未解答"))

menu = st.sidebar.radio("メニュー", ["今日の課題", "章ごとに学ぶ", "問題検索", "苦手だけ解く", "教科書で学ぶ"])

if menu == "教科書で学ぶ":
    chapter_options = sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    selected_chapter = st.sidebar.selectbox("章", chapter_options)
    st.subheader(f"第{selected_chapter}章 教科書で学ぶ")
    content = TEXTBOOK_LINKS.get(str(selected_chapter), {"summary": "この章の簡易まとめはまだ登録されていません。", "download_url": ""})
    st.markdown("### 簡易まとめ")
    st.write(content["summary"])
    st.markdown("### 教科書リンク")
    if content["download_url"]:
        st.link_button("アクチュアリー会の教科書ダウンロードページへ", content["download_url"])
    st.stop()

filtered = df.copy()
today_total_count = 0
today_done_count = 0
today_remaining_count = 0

if menu == "今日の課題":
    if not has_weekday_group:
        st.warning("CSVに『曜日グループ』列がないため、今日の課題は使えません。")
        st.stop()
    st.info(f"今日は {today_jp} です。曜日グループ {today_group} の問題を出題します。")
    filtered = filtered[filtered["曜日グループ"] == today_group].copy()
    today_total_count = len(filtered)
    today_done_count = int((filtered["学習状況"] == "マスター").sum())
    today_remaining_count = today_total_count - today_done_count
    chapter_options = ["すべて"] + sorted([x for x in filtered["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options, key="today_chapter")
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()
    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options, key="today_type")
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

elif menu == "章ごとに学ぶ":
    chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options, key="chapter_mode")
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()
    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options, key="chapter_type")
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

elif menu == "問題検索":
    keyword = st.sidebar.text_input("キーワード", key="search_keyword")
    chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options, key="search_chapter")
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()
    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options, key="search_type")
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()
    if keyword:
        q = filtered["問題文"].str.contains(keyword, case=False, na=False)
        a = filtered["解答"].str.contains(keyword, case=False, na=False)
        n = filtered["問題番号"].str.contains(keyword, case=False, na=False)
        filtered = filtered[q | a | n].copy()

elif menu == "苦手だけ解く":
    filtered = filtered[filtered["学習状況"] == "苦手"].copy()
    chapter_options = ["すべて"] + sorted([x for x in filtered["章"].unique().tolist() if x], key=natural_sort_key)
    chapter = st.sidebar.selectbox("章", chapter_options, key="weak_chapter")
    if chapter != "すべて":
        filtered = filtered[filtered["章"] == chapter].copy()
    question_type_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
    question_type = st.sidebar.selectbox("小問 / 中問", question_type_options, key="weak_type")
    if question_type != "すべて":
        filtered = filtered[filtered["問題種別"] == question_type].copy()

filtered["章_sort"] = filtered["章"].map(natural_sort_key)
filtered["問題種別_sort"] = filtered["問題種別"].map(question_type_sort_key)
sort_cols = ["章_sort", "問題種別_sort", "id_num", "id"]
if has_weekday_group and "曜日グループ" in filtered.columns:
    filtered["曜日グループ_sort"] = filtered["曜日グループ"].map(natural_sort_key)
    sort_cols = ["曜日グループ_sort"] + sort_cols
filtered = filtered.sort_values(by=sort_cols).reset_index(drop=True)

master_count = int((df["学習状況"] == "マスター").sum())
weak_count = int((df["学習状況"] == "苦手").sum())
unanswered_count = int((df["学習状況"] == "未解答").sum())

s1, s2, s3 = st.columns(3)
with s1:
    st.metric("マスター", f"{master_count}問")
with s2:
    st.metric("未解答", f"{unanswered_count}問")
with s3:
    st.metric("苦手", f"{weak_count}問")

if menu == "今日の課題":
    t1, t2, t3 = st.columns(3)
    with t1:
        st.metric("今日の課題総数", f"{today_total_count}問")
    with t2:
        st.metric("今日の完了", f"{today_done_count}問")
    with t3:
        st.metric("今日の残り課題", f"{today_remaining_count}問")
    if today_total_count > 0:
        st.progress(today_done_count / today_total_count)
else:
    st.caption(f"問題数: {len(filtered)}")

st.markdown("### 今日の勉強時間")
today_study_seconds = get_today_study_seconds(user_name)
running_elapsed_seconds = 0
if st.session_state["timer_running"] and st.session_state["timer_start_ts"] is not None:
    running_elapsed_seconds = int(datetime.now().timestamp() - st.session_state["timer_start_ts"])
display_seconds = today_study_seconds + running_elapsed_seconds

tc1, tc2, tc3 = st.columns(3)
with tc1:
    st.metric("今日の累計勉強時間", format_seconds(display_seconds))
with tc2:
    if not st.session_state["timer_running"]:
        if st.button("学習開始", use_container_width=True):
            st.session_state["timer_running"] = True
            st.session_state["timer_start_ts"] = datetime.now().timestamp()
            st.rerun()
    else:
        if st.button("学習終了", use_container_width=True):
            elapsed = int(datetime.now().timestamp() - st.session_state["timer_start_ts"])
            add_study_seconds(user_name, elapsed)
            st.session_state["timer_running"] = False
            st.session_state["timer_start_ts"] = None
            st.rerun()
with tc3:
    st.success("計測中" if st.session_state["timer_running"] else "停止中")

if filtered.empty:
    st.warning("条件に合う問題がありません。")
    st.stop()

valid_ids = [str(x) for x in filtered["id"].tolist()]
if st.session_state.get("current_id") not in valid_ids:
    st.session_state["current_id"] = valid_ids[0]

filtered["選択ラベル"] = filtered.apply(
    lambda row: " | ".join(
        [str(row["id"]), f"第{row['章']}章", str(row["問題種別"])]
        + ([str(row["問題番号"])] if str(row["問題番号"]).strip() else [])
        + ([f"【{row['学習状況']}】"] if str(row["学習状況"]).strip() else [])
    ),
    axis=1
)

label_by_id = dict(zip(filtered["id"], filtered["選択ラベル"]))
id_by_label = dict(zip(filtered["選択ラベル"], filtered["id"]))
valid_labels = filtered["選択ラベル"].tolist()

top1, top2 = st.columns([1, 4])
with top1:
    if st.button("ランダム出題"):
        st.session_state["current_id"] = str(filtered.sample(1).iloc[0]["id"])
        st.rerun()

with top2:
    current_label = label_by_id[st.session_state["current_id"]]
    selected_label = st.selectbox("問題選択", valid_labels, index=valid_labels.index(current_label), key="question_select")
    if st.button("表示"):
        st.session_state["current_id"] = str(id_by_label[selected_label])
        st.rerun()

current_rows = filtered[filtered["id"] == st.session_state["current_id"]]
if current_rows.empty:
    st.session_state["current_id"] = valid_ids[0]
    current_rows = filtered[filtered["id"] == st.session_state["current_id"]]

row = current_rows.iloc[0]

st.markdown("### 学習フラグ")
current_status = user_flag_map.get(str(row["id"]), "未解答")
fc1, fc2 = st.columns([3, 1])
with fc1:
    selected_status = st.radio("この問題の状態", ["未解答", "苦手", "マスター"], index=["未解答", "苦手", "マスター"].index(current_status), horizontal=True, key=f"flag_{row['id']}")
with fc2:
    st.write("")
    st.write("")
    if st.button("フラグ保存", use_container_width=True):
        update_flag(user_name, row["id"], selected_status)
        st.rerun()

current_index = valid_ids.index(st.session_state["current_id"]) + 1
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

show_answer = st.checkbox("解答を表示", key=f"show_answer_{row['id']}")
if show_answer:
    st.markdown("### 解答")
    st.write(row["解答"])
    if "解説" in row and str(row["解説"]).strip():
        st.markdown("### 解説")
        st.write(row["解説"])

nav1, nav2 = st.columns(2)
with nav1:
    if st.button("← 前へ", use_container_width=True):
        if current_index > 1:
            st.session_state["current_id"] = valid_ids[current_index - 2]
            st.rerun()
with nav2:
    if st.button("次へ →", use_container_width=True):
        if current_index < len(valid_ids):
            st.session_state["current_id"] = valid_ids[current_index]
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
