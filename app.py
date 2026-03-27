import json
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

st.set_page_config(page_title="アクチュアリー生保2次 過去問演習", layout="wide")

SITE_NAME = "アクチュアリー生保2次 過去問演習"
EXAM_DATE = date(2026, 12, 8)
QUESTION_FILE = "questions_normalized.csv"
JST = ZoneInfo("Asia/Tokyo")
USER_STATE_FILE = Path(".streamlit_user_state.json")
MENU_OPTIONS = ["ホーム", "今日の課題", "章ごとに学ぶ", "問題検索", "教科書で学ぶ"]

TEXTBOOK_LINKS = {
    str(i): {
        "summary": f"第{i}章の簡易まとめをここに記載してください。",
        "download_url": f"https://example.com/chapter{i}",
    }
    for i in range(1, 11)
}

SELF_EVAL_OPTIONS = ["わかった", "あやしい", "わからない", "後で復習"]
SELF_EVAL_SCORE = {"わかった": 2, "あやしい": 1, "わからない": -2, "後で復習": -1}
SELF_EVAL_LABEL = {
    "わかった": "✅ わかった",
    "あやしい": "🟡 あやしい",
    "わからない": "🔴 わからない",
    "後で復習": "📝 後で復習",
}
STATUS_LABEL = {
    "": "未評価",
    "わかった": "理解",
    "あやしい": "注意",
    "わからない": "苦手",
    "後で復習": "要復習",
}


@st.cache_data(ttl=1)
def load_questions() -> pd.DataFrame:
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


def now_jst() -> datetime:
    return datetime.now(JST)


def today_group_info():
    now = now_jst()
    weekday_num = now.weekday()
    weekday_name = ["月曜", "火曜", "水曜", "木曜", "金曜", "土曜", "日曜"][weekday_num]
    return str(weekday_num + 1), weekday_name, now


def days_to_exam() -> int:
    return (EXAM_DATE - now_jst().date()).days


def default_user_state():
    return {"ratings": {}, "history": {}, "favorites": {}}


def load_user_state():
    if USER_STATE_FILE.exists():
        try:
            data = json.loads(USER_STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                base = default_user_state()
                for key in base:
                    if isinstance(data.get(key), dict):
                        base[key] = data[key]
                return base
        except Exception:
            pass
    return default_user_state()


def save_user_state():
    USER_STATE_FILE.write_text(
        json.dumps(st.session_state["user_state"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ensure_state():
    defaults = {
        "timer_running": False,
        "timer_start_ts": None,
        "study_seconds_today": 0,
        "study_date_jst": now_jst().date().isoformat(),
        "user_state": load_user_state(),
        "app_menu": "ホーム",
        "main_menu_radio": "ホーム",
        "current_id": None,
        "selectbox_nonce": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    current_jst_date = now_jst().date().isoformat()
    if st.session_state["study_date_jst"] != current_jst_date:
        st.session_state["study_date_jst"] = current_jst_date
        st.session_state["study_seconds_today"] = 0
        st.session_state["timer_running"] = False
        st.session_state["timer_start_ts"] = None


def get_rating(question_id: str) -> str:
    return st.session_state["user_state"]["ratings"].get(question_id, "")


def is_favorite(question_id: str) -> bool:
    return bool(st.session_state["user_state"]["favorites"].get(question_id, False))


def set_favorite(question_id: str, value: bool):
    st.session_state["user_state"]["favorites"][question_id] = bool(value)
    save_user_state()


def update_self_eval(question_id: str, rating: str):
    user_state = st.session_state["user_state"]
    user_state["ratings"][question_id] = rating
    hist = user_state["history"].setdefault(
        question_id,
        {"count": 0, "last_rated_at": "", "score_total": 0},
    )
    hist["count"] += 1
    hist["last_rated_at"] = now_jst().isoformat(timespec="seconds")
    hist["score_total"] += SELF_EVAL_SCORE.get(rating, 0)
    save_user_state()


def compute_question_status(question_id: str) -> str:
    return STATUS_LABEL.get(get_rating(question_id), "未評価")


def build_label(row) -> str:
    parts = [str(row["id"]), f"第{row['章']}章", str(row["問題種別"])]
    if str(row.get("問題番号", "")).strip():
        parts.append(str(row["問題番号"]))
    if str(row.get("年度", "")).strip():
        parts.append(f"{row['年度']}年")
    return " | ".join(parts)


def sort_questions(filtered: pd.DataFrame, has_weekday_group: bool) -> pd.DataFrame:
    filtered = filtered.copy()
    filtered["id"] = filtered["id"].astype(str)
    filtered["id_num"] = pd.to_numeric(filtered["id"], errors="coerce")
    filtered["章_sort"] = filtered["章"].map(natural_sort_key)
    filtered["問題種別_sort"] = filtered["問題種別"].map(question_type_sort_key)
    sort_cols = ["章_sort", "問題種別_sort", "id_num", "id"]
    if has_weekday_group and "曜日グループ" in filtered.columns:
        filtered["曜日グループ_sort"] = filtered["曜日グループ"].map(natural_sort_key)
        sort_cols = ["曜日グループ_sort"] + sort_cols
    filtered = filtered.sort_values(by=sort_cols).reset_index(drop=True)
    filtered["選択ラベル"] = filtered.apply(build_label, axis=1)
    filtered["ステータス"] = filtered["id"].map(compute_question_status)
    return filtered


def chapter_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    chapters = [x for x in df["章"].dropna().astype(str).unique().tolist() if str(x).strip()]
    for chapter in sorted(chapters, key=natural_sort_key):
        chapter_df = df[df["章"] == chapter]
        ids = chapter_df["id"].astype(str).tolist()
        total = len(ids)
        rated = sum(1 for qid in ids if get_rating(qid))
        understood = sum(1 for qid in ids if get_rating(qid) == "わかった")
        weak = sum(1 for qid in ids if get_rating(qid) == "わからない")
        review = sum(1 for qid in ids if get_rating(qid) == "後で復習")
        rows.append(
            {
                "章": chapter,
                "総数": total,
                "評価済": rated,
                "理解": understood,
                "苦手": weak,
                "要復習": review,
                "進捗率": f"{(rated / total * 100):.0f}%" if total else "0%",
            }
        )
    return pd.DataFrame(rows)


def filter_questions(df: pd.DataFrame, menu: str, has_weekday_group: bool):
    filtered = df.copy()
    today_total_count = 0
    today_remaining_count = 0
    today_group, today_jp, _ = today_group_info()

    st.sidebar.markdown("### 出題条件")
    only_weak = st.sidebar.checkbox("苦手だけ出題")
    only_review = st.sidebar.checkbox("要復習だけ出題")

    if menu == "今日の課題":
        if not has_weekday_group:
            st.warning("CSVに『曜日グループ』列がないため、今日の課題は使えません。")
            st.stop()
        st.info(f"今日は {today_jp} です。曜日グループ {today_group} の問題を出題します。")
        filtered = filtered[filtered["曜日グループ"] == today_group].copy()
        today_total_count = len(filtered)

        chapter_options = ["すべて"] + sorted(
            [x for x in filtered["章"].unique().tolist() if x],
            key=natural_sort_key,
        )
        chapter = st.sidebar.selectbox("章", chapter_options, key="today_chapter")
        if chapter != "すべて":
            filtered = filtered[filtered["章"] == chapter].copy()

        qt_options = ["すべて"] + sorted(
            [x for x in filtered["問題種別"].unique().tolist() if x],
            key=question_type_sort_key,
        )
        qt = st.sidebar.selectbox("小問 / 中問", qt_options, key="today_type")
        if qt != "すべて":
            filtered = filtered[filtered["問題種別"] == qt].copy()

    elif menu == "章ごとに学ぶ":
        chapter_options = ["すべて"] + sorted(
            [x for x in df["章"].unique().tolist() if x],
            key=natural_sort_key,
        )
        chapter = st.sidebar.selectbox("章", chapter_options, key="chapter_filter")
        if chapter != "すべて":
            filtered = filtered[filtered["章"] == chapter].copy()

        qt_options = ["すべて"] + sorted(
            [x for x in filtered["問題種別"].unique().tolist() if x],
            key=question_type_sort_key,
        )
        qt = st.sidebar.selectbox("小問 / 中問", qt_options, key="chapter_type")
        if qt != "すべて":
            filtered = filtered[filtered["問題種別"] == qt].copy()

        if "年度" in filtered.columns:
            years = [y for y in filtered["年度"].unique().tolist() if y]
            year_options = ["すべて"] + sorted(years)
            year = st.sidebar.selectbox("年度", year_options, key="chapter_year")
            if year != "すべて":
                filtered = filtered[filtered["年度"] == year].copy()

    elif menu == "問題検索":
        keyword = st.sidebar.text_input("キーワード", key="search_keyword")
        chapter_options = ["すべて"] + sorted(
            [x for x in df["章"].unique().tolist() if x],
            key=natural_sort_key,
        )
        chapter = st.sidebar.selectbox("章", chapter_options, key="search_chapter")
        if chapter != "すべて":
            filtered = filtered[filtered["章"] == chapter].copy()

        qt_options = ["すべて"] + sorted(
            [x for x in filtered["問題種別"].unique().tolist() if x],
            key=question_type_sort_key,
        )
        qt = st.sidebar.selectbox("小問 / 中問", qt_options, key="search_type")
        if qt != "すべて":
            filtered = filtered[filtered["問題種別"] == qt].copy()

        if "年度" in filtered.columns:
            years = [y for y in filtered["年度"].unique().tolist() if y]
            year_options = ["すべて"] + sorted(years)
            year = st.sidebar.selectbox("年度", year_options, key="search_year")
            if year != "すべて":
                filtered = filtered[filtered["年度"] == year].copy()

        if keyword:
            question_mask = filtered["問題文"].str.contains(keyword, case=False, na=False)
            answer_mask = filtered["解答"].str.contains(keyword, case=False, na=False)
            number_mask = filtered["問題番号"].str.contains(keyword, case=False, na=False)
            filtered = filtered[question_mask | answer_mask | number_mask].copy()

    if only_weak:
        filtered = filtered[filtered["id"].astype(str).map(lambda x: get_rating(x) == "わからない")].copy()
    if only_review:
        filtered = filtered[filtered["id"].astype(str).map(lambda x: get_rating(x) == "後で復習")].copy()

    if menu == "今日の課題":
        today_remaining_count = len(filtered)

    return filtered, today_total_count, today_remaining_count


def render_dashboard(df: pd.DataFrame):
    st.markdown("### 学習ダッシュボード")
    all_ids = df["id"].astype(str).tolist()
    rated_count = sum(1 for qid in all_ids if get_rating(qid))
    weak_count = sum(1 for qid in all_ids if get_rating(qid) == "わからない")
    review_count = sum(1 for qid in all_ids if get_rating(qid) == "後で復習")
    understood_count = sum(1 for qid in all_ids if get_rating(qid) == "わかった")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("今日のおすすめ", "今日の1問")
    c2.metric("要復習", f"{review_count}問")
    c3.metric("苦手", f"{weak_count}問")
    c4.metric("理解済", f"{understood_count}問")

    progress_ratio = rated_count / len(all_ids) if all_ids else 0
    st.progress(progress_ratio, text=f"全体進捗 {progress_ratio * 100:.0f}%")

    chapter_df = chapter_summary(df)
    if not chapter_df.empty:
        st.dataframe(chapter_df, use_container_width=True, hide_index=True)


def start_timer():
    st.session_state["timer_running"] = True
    st.session_state["timer_start_ts"] = now_jst().timestamp()


def stop_timer():
    if st.session_state["timer_running"] and st.session_state["timer_start_ts"] is not None:
        elapsed = int(now_jst().timestamp() - st.session_state["timer_start_ts"])
        st.session_state["study_seconds_today"] += max(elapsed, 0)
    st.session_state["timer_running"] = False
    st.session_state["timer_start_ts"] = None


def render_timer(now_tokyo: datetime):
    st.markdown("### 今日の勉強時間")
    running_elapsed_seconds = 0
    if st.session_state["timer_running"] and st.session_state["timer_start_ts"] is not None:
        running_elapsed_seconds = int(now_tokyo.timestamp() - st.session_state["timer_start_ts"])

    display_seconds = st.session_state["study_seconds_today"] + running_elapsed_seconds
    c1, c2, c3 = st.columns(3)
    with c1:
        h = display_seconds // 3600
        m = (display_seconds % 3600) // 60
        s = display_seconds % 60
        st.metric("今日の累計勉強時間", f"{h:02d}:{m:02d}:{s:02d}")
    with c2:
        if not st.session_state["timer_running"]:
            st.button("学習開始", use_container_width=True, on_click=start_timer)
        else:
            st.button("学習終了", use_container_width=True, on_click=stop_timer)
    with c3:
        if st.session_state["timer_running"]:
            st.success("計測中")
        else:
            st.info("停止中")


def pick_home_recommendation(df: pd.DataFrame):
    has_weekday_group = "曜日グループ" in df.columns
    today_group, _, _ = today_group_info()
    if has_weekday_group:
        today_df = sort_questions(df[df["曜日グループ"].astype(str) == today_group].copy(), has_weekday_group)
        if not today_df.empty:
            return today_df.iloc[0], "今日の1問"
    review_df = df[df["id"].astype(str).map(lambda x: get_rating(x) == "後で復習")].copy()
    if not review_df.empty:
        review_df = sort_questions(review_df, has_weekday_group)
        return review_df.iloc[0], "要復習"
    weak_df = df[df["id"].astype(str).map(lambda x: get_rating(x) == "わからない")].copy()
    if not weak_df.empty:
        weak_df = sort_questions(weak_df, has_weekday_group)
        return weak_df.iloc[0], "苦手"
    sorted_df = sort_questions(df.copy(), has_weekday_group)
    return sorted_df.iloc[0], "おすすめ"


def on_menu_change():
    st.session_state["app_menu"] = st.session_state["main_menu_radio"]
    st.session_state["current_id"] = None
    st.session_state["selectbox_nonce"] += 1


def go_to_question(question_id: str, target_menu: str):
    st.session_state["app_menu"] = target_menu
    st.session_state["main_menu_radio"] = target_menu
    st.session_state["current_id"] = str(question_id)
    st.session_state["selectbox_nonce"] += 1


def set_problem_from_select(widget_key: str, label_to_id: dict[str, str]):
    st.session_state["current_id"] = label_to_id[st.session_state[widget_key]]


def go_prev(prev_target_id: str):
    st.session_state["current_id"] = prev_target_id
    st.session_state["selectbox_nonce"] += 1


def go_next(next_target_id: str):
    st.session_state["current_id"] = next_target_id
    st.session_state["selectbox_nonce"] += 1


def set_eval(question_id: str, rating: str):
    update_self_eval(question_id, rating)


def toggle_favorite(question_id: str, widget_key: str):
    set_favorite(question_id, st.session_state[widget_key])


def render_problem_area(filtered: pd.DataFrame, menu: str, has_weekday_group: bool):
    if filtered.empty:
        st.warning("条件に合う問題がありません。")
        return

    valid_ids = filtered["id"].astype(str).tolist()
    if st.session_state["current_id"] not in valid_ids:
        st.session_state["current_id"] = valid_ids[0]

    current_id = st.session_state["current_id"]
    current_index = valid_ids.index(current_id)

    id_to_label = dict(zip(filtered["id"].astype(str), filtered["選択ラベル"]))
    label_to_id = {label: qid for qid, label in id_to_label.items()}
    valid_labels = [id_to_label[qid] for qid in valid_ids]
    current_label = id_to_label[current_id]

    widget_key = f"problem_select_{menu}_{st.session_state['selectbox_nonce']}"
    st.selectbox(
        "問題選択",
        valid_labels,
        index=valid_labels.index(current_label),
        key=widget_key,
        on_change=set_problem_from_select,
        args=(widget_key, label_to_id),
    )

    row = filtered[filtered["id"].astype(str) == st.session_state["current_id"]].iloc[0]
    qid = str(row["id"])
    current_index = valid_ids.index(qid)
    total_count = len(valid_ids)
    progress_ratio = (current_index + 1) / total_count if total_count else 0

    title = f"第{row['章']}章 {row['問題種別']} {row['問題番号']}"
    if has_weekday_group and str(row.get("曜日グループ", "")).strip() and menu == "今日の課題":
        title = f"[曜日グループ {row['曜日グループ']}] " + title
    if str(row.get("年度", "")).strip():
        title = f"{row['年度']}年 " + title

    st.subheader(title)
    st.caption(f"ステータス: {compute_question_status(qid)}")

    st.markdown("### 問題")
    st.write(row["問題文"])

    fav_key = f"favorite_{qid}"
    st.checkbox(
        "お気に入り",
        value=is_favorite(qid),
        key=fav_key,
        on_change=toggle_favorite,
        args=(qid, fav_key),
    )

    with st.expander("解答を表示"):
        st.markdown("### 解答")
        st.write(row["解答"])
        if "解説" in row and str(row["解説"]).strip():
            st.markdown("### 解説")
            st.write(row["解説"])

        st.markdown("### 自己評価")
        current_eval = get_rating(qid)
        cols = st.columns(4)
        for idx, option in enumerate(SELF_EVAL_OPTIONS):
            with cols[idx]:
                st.button(
                    SELF_EVAL_LABEL[option],
                    key=f"eval_{qid}_{option}",
                    use_container_width=True,
                    type="primary" if current_eval == option else "secondary",
                    on_click=set_eval,
                    args=(qid, option),
                )
        if current_eval:
            st.caption(f"直近の自己評価: {current_eval}")

    nav1, nav2 = st.columns(2)
    with nav1:
        prev_disabled = current_index == 0
        prev_target_id = valid_ids[current_index - 1] if not prev_disabled else qid
        st.button(
            "← 前へ",
            use_container_width=True,
            disabled=prev_disabled,
            on_click=go_prev,
            args=(prev_target_id,),
        )
    with nav2:
        next_disabled = current_index >= len(valid_ids) - 1
        next_target_id = valid_ids[current_index + 1] if not next_disabled else qid
        st.button(
            "次へ →",
            use_container_width=True,
            disabled=next_disabled,
            on_click=go_next,
            args=(next_target_id,),
        )

    st.markdown("---")
    st.markdown("### 進捗")
    m1, m2, m3 = st.columns(3)
    m1.metric("現在位置", f"{current_index + 1} / {total_count}")
    m2.metric("残り問題数", f"{total_count - current_index - 1}題")
    m3.metric("進捗率", f"{progress_ratio * 100:.0f}%")
    st.progress(progress_ratio)


ensure_state()
df = load_questions()
required_cols = ["id", "章", "問題種別", "問題番号", "問題文", "解答"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"CSVに必要な列が足りません: {', '.join(missing)}")
    st.info("必要列: id, 章, 問題種別, 問題番号, 問題文, 解答")
    st.stop()

for col in ["id", "章", "問題種別", "年度", "問題番号", "問題文", "解答", "解説", "曜日グループ"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

st.markdown(f"## {SITE_NAME}")
left = days_to_exam()
today_group, today_jp, now_tokyo = today_group_info()
if left >= 0:
    st.info(
        f"試験まであと **{left}日**（試験日: {EXAM_DATE.strftime('%Y-%m-%d')}）"
        f" / 現在時刻: {now_tokyo.strftime('%Y-%m-%d %H:%M')} JST"
    )
else:
    st.warning(
        f"試験日は {EXAM_DATE.strftime('%Y-%m-%d')} でした。"
        f" / 現在時刻: {now_tokyo.strftime('%Y-%m-%d %H:%M')} JST"
    )

has_weekday_group = "曜日グループ" in df.columns
st.session_state["main_menu_radio"] = st.session_state["app_menu"]
menu = st.sidebar.radio(
    "メニュー",
    MENU_OPTIONS,
    index=MENU_OPTIONS.index(st.session_state["app_menu"]),
    key="main_menu_radio",
    on_change=on_menu_change,
)
menu = st.session_state["app_menu"]

if menu == "教科書で学ぶ":
    chapter_options = sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    selected_chapter = st.sidebar.selectbox("章", chapter_options)
    st.subheader(f"第{selected_chapter}章 教科書で学ぶ")
    content = TEXTBOOK_LINKS.get(
        str(selected_chapter),
        {"summary": "この章の簡易まとめはまだ登録されていません。", "download_url": ""},
    )
    st.markdown("### 簡易まとめ")
    st.write(content["summary"])
    st.markdown("### 教科書リンク")
    if content["download_url"]:
        st.link_button("アクチュアリー会の教科書ダウンロードページへ", content["download_url"])
    else:
        st.info("この章のダウンロードリンクはまだ設定されていません。app.py の TEXTBOOK_LINKS を更新してください。")
    st.stop()

render_dashboard(df)

if menu == "ホーム":
    st.markdown("### すぐ始める")
    c1, c2, c3 = st.columns(3)
    c1.info("今日の1問にすぐ飛べます。")
    c2.info("左メニューで『苦手だけ出題』『要復習だけ出題』に切り替えできます。")
    c3.info("章別進捗を見ながら弱点を潰せます。")
    render_timer(now_tokyo)

    reco, reco_kind = pick_home_recommendation(df)
    reco_text = f"{reco_kind}: {reco.get('年度', '')}年 第{reco['章']}章 {reco['問題種別']} {reco['問題番号']}"
    if reco_kind == "要復習":
        st.warning(reco_text)
    elif reco_kind == "苦手":
        st.error(reco_text)
    else:
        st.success(reco_text)

    button_label = "今日の1問を開く" if reco_kind == "今日の1問" else "この問題を開く"
    target_menu = "今日の課題" if reco_kind == "今日の1問" else "章ごとに学ぶ"
    st.button(
        button_label,
        use_container_width=True,
        on_click=go_to_question,
        args=(str(reco["id"]), target_menu),
    )
else:
    filtered, today_total_count, today_remaining_count = filter_questions(df, menu, has_weekday_group)
    filtered = sort_questions(filtered, has_weekday_group)

    if menu == "今日の課題" and today_total_count:
        st.caption(f"今日の課題: {today_remaining_count}問表示中 / 対象総数 {today_total_count}問")

    render_problem_area(filtered, menu, has_weekday_group)
