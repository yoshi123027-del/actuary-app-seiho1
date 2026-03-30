import html
import json
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

st.set_page_config(page_title="アクチュアリー2次試験 生保1過去問演習", layout="wide")

SITE_NAME = "アクチュアリー2次試験 生保1過去問演習"
EXAM_DATE = date(2026, 12, 8)
QUESTION_FILE = "questions_normalized.csv"
JST = ZoneInfo("Asia/Tokyo")
USER_STATE_FILE = Path(".streamlit_user_state.json")
MENU_OPTIONS = ["ホーム", "今日の課題", "章ごとに学ぶ", "問題検索", "教科書で学ぶ"]

TEXTBOOK_LINKS = {
    str(i): {
        "summary": f"第{i}章の簡易まとめはまだ登録されていません。",
        "download_url": "https://www.actuaries.jp/examin/textbook/",
    }
    for i in range(1, 11)
}
TEXTBOOK_LINKS["1"]["summary"] = "第1章の教科書まとめをGoogle Driveで閲覧できます。"
TEXTBOOK_LINKS["1"]["download_url"] = "https://drive.google.com/file/d/1nnzXQwZGs0cfJd543ttBmcx1PDDACubt/view?usp=sharing"


PRIMARY_EVAL_OPTIONS = ["理解", "要注意"]
PRIMARY_EVAL_LABEL = {
    "理解": "✅ 理解",
    "要注意": "🟡 要注意",
}
PRIMARY_EVAL_SCORE = {"理解": 2, "要注意": 0}
STATUS_LABEL = {
    "": "未評価",
    "理解": "理解",
    "要注意": "要注意",
}
REVIEW_FLAG_LABEL = "🚩 後で復習"


@st.cache_data(ttl=60)
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
    return {"ratings": {}, "history": {}, "favorites": {}, "review_flags": {}}


def migrate_legacy_user_state(base: dict) -> dict:
    ratings = base.get("ratings", {})
    review_flags = base.get("review_flags", {})

    migrated_ratings = {}
    for qid, rating in list(ratings.items()):
        if rating in ("理解", "要注意", ""):
            migrated_ratings[qid] = rating
        elif rating == "わかった":
            migrated_ratings[qid] = "理解"
        elif rating in ("あやしい",):
            migrated_ratings[qid] = "要注意"
        elif rating in ("わからない", "後で復習"):
            migrated_ratings[qid] = "要注意"
            review_flags[qid] = True
        else:
            migrated_ratings[qid] = ""

    base["ratings"] = migrated_ratings
    base["review_flags"] = {str(k): bool(v) for k, v in review_flags.items()}
    return base


def load_user_state():
    if USER_STATE_FILE.exists():
        try:
            data = json.loads(USER_STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                base = default_user_state()
                for key in base:
                    if isinstance(data.get(key), dict):
                        base[key] = data[key]
                return migrate_legacy_user_state(base)
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
        "main_menu": "ホーム",
        "current_id": None,
        "question_select_nonce": 0,
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


def get_primary_eval(question_id: str) -> str:
    return st.session_state["user_state"]["ratings"].get(question_id, "")


def is_review_flagged(question_id: str) -> bool:
    return bool(st.session_state["user_state"]["review_flags"].get(question_id, False))


def is_favorite(question_id: str) -> bool:
    return bool(st.session_state["user_state"]["favorites"].get(question_id, False))


def set_favorite(question_id: str, value: bool):
    st.session_state["user_state"]["favorites"][question_id] = bool(value)
    save_user_state()


def update_primary_eval(question_id: str, rating: str):
    user_state = st.session_state["user_state"]
    user_state["ratings"][question_id] = rating
    hist = user_state["history"].setdefault(
        question_id, {"count": 0, "last_rated_at": "", "score_total": 0}
    )
    hist["count"] += 1
    hist["last_rated_at"] = now_jst().isoformat(timespec="seconds")
    hist["score_total"] += PRIMARY_EVAL_SCORE.get(rating, 0)
    save_user_state()


def toggle_review_flag(question_id: str):
    current = is_review_flagged(question_id)
    st.session_state["user_state"]["review_flags"][question_id] = not current
    hist = st.session_state["user_state"]["history"].setdefault(
        question_id, {"count": 0, "last_rated_at": "", "score_total": 0}
    )
    hist["last_rated_at"] = now_jst().isoformat(timespec="seconds")
    save_user_state()


def compute_question_status(question_id: str) -> str:
    parts = []
    primary = get_primary_eval(question_id)
    if primary:
        parts.append(STATUS_LABEL.get(primary, primary))
    if is_review_flagged(question_id):
        parts.append(REVIEW_FLAG_LABEL)
    if not parts:
        return "未評価"
    return " / ".join(parts)


def render_multiline_text(text: str):
    safe_text = html.escape(str(text or ""))
    st.markdown(
        f'<div style="white-space: pre-wrap; line-height: 1.8;">{safe_text}</div>',
        unsafe_allow_html=True,
    )


def build_label(row) -> str:
    parts = [str(row["id"]), f"第{row['章']}章", str(row["問題種別"])]
    if str(row.get("年度", "")).strip():
        parts.append(f"{row['年度']}年")
    return " | ".join(parts)


def sort_questions(filtered: pd.DataFrame, has_weekday_group: bool) -> pd.DataFrame:
    filtered = filtered.copy()
    filtered["id"] = filtered["id"].astype(str)
    filtered["id_num"] = pd.to_numeric(filtered["id"], errors="coerce")
    filtered = filtered.sort_values(by=["id_num", "id"]).reset_index(drop=True)
    filtered["選択ラベル"] = filtered.apply(build_label, axis=1)
    filtered["ステータス"] = filtered["id"].map(compute_question_status)
    return filtered


def chapter_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    chapters = [x for x in df["章"].dropna().astype(str).unique().tolist() if str(x).strip()]
    total_all = 0
    understood_all = 0
    caution_all = 0
    review_all = 0

    for chapter in sorted(chapters, key=natural_sort_key):
        chapter_df = df[df["章"] == chapter]
        ids = chapter_df["id"].astype(str).tolist()
        total = len(ids)
        understood = sum(1 for qid in ids if get_primary_eval(qid) == "理解")
        caution = sum(1 for qid in ids if get_primary_eval(qid) == "要注意")
        review = sum(1 for qid in ids if is_review_flagged(qid))

        total_all += total
        understood_all += understood
        caution_all += caution
        review_all += review

        rows.append(
            {
                "章": chapter,
                "総数": total,
                "理解": understood,
                "要注意": caution,
                "後で復習": review,
                "理解度": f"{(understood / total * 100):.0f}%" if total else "0%",
            }
        )

    if total_all:
        rows.append(
            {
                "章": "合計",
                "総数": total_all,
                "理解": understood_all,
                "要注意": caution_all,
                "後で復習": review_all,
                "理解度": f"{(understood_all / total_all * 100):.0f}%" if total_all else "0%",
            }
        )

    return pd.DataFrame(rows)


def render_dashboard(df: pd.DataFrame):
    st.markdown("### 学習ダッシュボード")
    all_ids = df["id"].astype(str).tolist()
    total_count = len(all_ids)
    understood_count = sum(1 for qid in all_ids if get_primary_eval(qid) == "理解")
    caution_count = sum(1 for qid in all_ids if get_primary_eval(qid) == "要注意")
    review_count = sum(1 for qid in all_ids if is_review_flagged(qid))

    understanding_ratio = understood_count / total_count if total_count else 0.0
    st.progress(understanding_ratio)
    st.caption(f"全体理解度 {understanding_ratio * 100:.0f}%")

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
        if st.session_state["timer_running"]:
            st.button("学習終了", use_container_width=True, on_click=stop_timer)
        else:
            st.button("学習開始", use_container_width=True, on_click=start_timer)
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
            untouched = today_df[
                today_df["id"].astype(str).map(
                    lambda x: (get_primary_eval(x) == "") and (not is_review_flagged(x))
                )
            ]
            if not untouched.empty:
                return untouched.iloc[0], "今日の1問"
            return today_df.iloc[0], "今日の1問"

    flagged_df = df[df["id"].astype(str).map(is_review_flagged)].copy()
    if not flagged_df.empty:
        flagged_df = sort_questions(flagged_df, has_weekday_group)
        return flagged_df.iloc[0], "後で復習"

    caution_df = df[df["id"].astype(str).map(lambda x: get_primary_eval(x) == "要注意")].copy()
    if not caution_df.empty:
        caution_df = sort_questions(caution_df, has_weekday_group)
        return caution_df.iloc[0], "要注意"

    all_df = sort_questions(df.copy(), has_weekday_group)
    return all_df.iloc[0], "おすすめ"


def go_to_question(question_id: str, target_menu: str):
    st.session_state["main_menu"] = target_menu
    st.session_state["current_id"] = str(question_id)
    st.session_state["question_select_nonce"] += 1


def set_primary_eval_callback(question_id: str, rating: str):
    update_primary_eval(question_id, rating)


def toggle_review_flag_callback(question_id: str):
    toggle_review_flag(question_id)


def set_favorite_callback(question_id: str, widget_key: str):
    set_favorite(question_id, st.session_state[widget_key])


def go_prev_callback(valid_ids: list[str], current_index_zero: int):
    if current_index_zero > 0:
        st.session_state["current_id"] = valid_ids[current_index_zero - 1]
        st.session_state["question_select_nonce"] += 1


def go_next_callback(valid_ids: list[str], current_index_zero: int):
    if current_index_zero < len(valid_ids) - 1:
        st.session_state["current_id"] = valid_ids[current_index_zero + 1]
        st.session_state["question_select_nonce"] += 1




def sync_filter_state(target_key: str, source_key: str):
    st.session_state[target_key] = st.session_state[source_key]
    st.session_state["current_id"] = None
    st.session_state["question_select_nonce"] += 1


def render_main_filters(menu: str, df: pd.DataFrame):
    if menu not in ["章ごとに学ぶ", "問題検索"]:
        return

    key_prefix = "chapter" if menu == "章ごとに学ぶ" else "search"
    chapter_key = f"{key_prefix}_filter" if menu == "章ごとに学ぶ" else "search_chapter"
    type_key = f"{key_prefix}_type" if menu == "章ごとに学ぶ" else "search_type"
    year_key = f"{key_prefix}_year" if menu == "章ごとに学ぶ" else "search_year"

    chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    st.session_state.setdefault(chapter_key, "すべて")
    st.session_state.setdefault(type_key, "すべて")
    if "年度" in df.columns:
        years = [y for y in df["年度"].unique().tolist() if y]
        year_options = ["すべて"] + sorted(years)
        st.session_state.setdefault(year_key, "すべて")
    else:
        year_options = ["すべて"]

    st.markdown("### 絞り込み")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox(
            "章",
            chapter_options,
            index=chapter_options.index(st.session_state[chapter_key]) if st.session_state[chapter_key] in chapter_options else 0,
            key=f"main_{chapter_key}",
            on_change=sync_filter_state,
            args=(chapter_key, f"main_{chapter_key}"),
        )
    with c2:
        type_options = ["すべて"] + sorted([x for x in df["問題種別"].unique().tolist() if x], key=question_type_sort_key)
        st.selectbox(
            "小問 / 中問",
            type_options,
            index=type_options.index(st.session_state[type_key]) if st.session_state[type_key] in type_options else 0,
            key=f"main_{type_key}",
            on_change=sync_filter_state,
            args=(type_key, f"main_{type_key}"),
        )
    with c3:
        if "年度" in df.columns:
            st.selectbox(
                "年度",
                year_options,
                index=year_options.index(st.session_state[year_key]) if st.session_state[year_key] in year_options else 0,
                key=f"main_{year_key}",
                on_change=sync_filter_state,
                args=(year_key, f"main_{year_key}"),
            )
def filter_questions(df: pd.DataFrame, menu: str, has_weekday_group: bool):
    filtered = df.copy()
    today_total_count = 0
    today_remaining_count = 0
    today_group, today_jp, _ = today_group_info()

    st.sidebar.markdown("### 出題条件")
    only_review = st.sidebar.checkbox("🚩 後で復習だけ表示", key=f"review_only_{menu}")

    if menu == "今日の課題":
        if not has_weekday_group:
            st.warning("CSVに『曜日グループ』列がないため、今日の課題は使えません。")
            st.stop()
        st.info(f"今日は {today_jp} です。曜日グループ {today_group} の問題を出題します。")
        filtered = filtered[filtered["曜日グループ"] == today_group].copy()
        today_total_count = len(filtered)

    elif menu == "章ごとに学ぶ":
        chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
        st.session_state.setdefault("chapter_filter", "すべて")
        chapter = st.sidebar.selectbox("章", chapter_options, index=chapter_options.index(st.session_state["chapter_filter"]) if st.session_state["chapter_filter"] in chapter_options else 0, key="chapter_filter")
        if chapter != "すべて":
            filtered = filtered[filtered["章"] == chapter].copy()

        qt_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
        st.session_state.setdefault("chapter_type", "すべて")
        qt = st.sidebar.selectbox("小問 / 中問", qt_options, index=qt_options.index(st.session_state["chapter_type"]) if st.session_state["chapter_type"] in qt_options else 0, key="chapter_type")
        if qt != "すべて":
            filtered = filtered[filtered["問題種別"] == qt].copy()

        if "年度" in filtered.columns:
            years = [y for y in filtered["年度"].unique().tolist() if y]
            year_options = ["すべて"] + sorted(years)
            st.session_state.setdefault("chapter_year", "すべて")
            year = st.sidebar.selectbox("年度", year_options, index=year_options.index(st.session_state["chapter_year"]) if st.session_state["chapter_year"] in year_options else 0, key="chapter_year")
            if year != "すべて":
                filtered = filtered[filtered["年度"] == year].copy()

    elif menu == "問題検索":
        chapter_options = ["すべて"] + sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
        st.session_state.setdefault("search_chapter", "すべて")
        chapter = st.sidebar.selectbox("章", chapter_options, index=chapter_options.index(st.session_state["search_chapter"]) if st.session_state["search_chapter"] in chapter_options else 0, key="search_chapter")
        if chapter != "すべて":
            filtered = filtered[filtered["章"] == chapter].copy()

        qt_options = ["すべて"] + sorted([x for x in filtered["問題種別"].unique().tolist() if x], key=question_type_sort_key)
        st.session_state.setdefault("search_type", "すべて")
        qt = st.sidebar.selectbox("小問 / 中問", qt_options, index=qt_options.index(st.session_state["search_type"]) if st.session_state["search_type"] in qt_options else 0, key="search_type")
        if qt != "すべて":
            filtered = filtered[filtered["問題種別"] == qt].copy()

        if "年度" in filtered.columns:
            years = [y for y in filtered["年度"].unique().tolist() if y]
            year_options = ["すべて"] + sorted(years)
            st.session_state.setdefault("search_year", "すべて")
            year = st.sidebar.selectbox("年度", year_options, index=year_options.index(st.session_state["search_year"]) if st.session_state["search_year"] in year_options else 0, key="search_year")
            if year != "すべて":
                filtered = filtered[filtered["年度"] == year].copy()

        # キーワード検索は画面側で行う

    if only_review:
        filtered = filtered[filtered["id"].astype(str).map(is_review_flagged)].copy()

    if menu == "今日の課題":
        today_remaining_count = len(filtered)

    return filtered, today_total_count, today_remaining_count


def previous_action_text(question_id: str) -> str:
    primary = get_primary_eval(question_id)
    review = is_review_flagged(question_id)
    if not primary and not review:
        return "前回の記録はありません"
    parts = []
    if primary:
        parts.append(primary)
    if review:
        parts.append(REVIEW_FLAG_LABEL)
    return "前回の処理: " + " / ".join(parts)

def render_search_results(base_filtered: pd.DataFrame, has_weekday_group: bool):
    st.markdown("### 問題検索")
    keyword = st.text_input("キーワードを入力", key="search_keyword_main", placeholder="例：付加保険料")
    st.caption("問題文・解答・解説から検索します。問題文の一覧から気になるものを開く形式です。")

    if not keyword.strip():
        st.info("キーワードを入力すると、該当する問題を一覧表示します。")
        st.caption(f"検索対象: {len(base_filtered)}問")
        return

    keyword = keyword.strip()
    search_df = base_filtered.copy()
    question_mask = search_df["問題文"].str.contains(keyword, case=False, na=False)
    answer_mask = search_df["解答"].str.contains(keyword, case=False, na=False)
    explanation_mask = search_df["解説"].str.contains(keyword, case=False, na=False) if "解説" in search_df.columns else False
    matched = search_df[question_mask | answer_mask | explanation_mask].copy()
    matched = sort_questions(matched, has_weekday_group)

    st.caption(f"検索結果: {len(matched)}問")
    if matched.empty:
        st.warning("該当する問題はありません。")
        return

    def compact_question_text(value: str, limit: int = 120) -> str:
        one_line = re.sub(r"\s+", " ", str(value)).strip()
        if len(one_line) <= limit:
            return one_line
        return one_line[:limit].rstrip() + "…"

    for idx, (_, row) in enumerate(matched.iterrows(), start=1):
        qid = str(row["id"])
        summary = compact_question_text(row["問題文"])
        with st.expander(f"{idx}. {summary}", expanded=False):
            meta_parts = []
            if str(row.get("年度", "")).strip():
                meta_parts.append(f"{row['年度']}年")
            meta_parts.append(f"第{row['章']}章")
            meta_parts.append(str(row["問題種別"]))
            st.caption(" | ".join(meta_parts))
            st.caption(f"ステータス: {compute_question_status(qid)}")
            st.caption(previous_action_text(qid))
            st.markdown("**問題**")
            render_multiline_text(row["問題文"])
            st.markdown("**解答**")
            render_multiline_text(row["解答"])
            if str(row.get("解説", "")).strip():
                st.markdown("**解説**")
                render_multiline_text(row["解説"])


def render_problem_area(filtered: pd.DataFrame, menu: str, has_weekday_group: bool):
    if filtered.empty:
        st.warning("条件に合う問題がありません。")
        return

    valid_ids = filtered["id"].astype(str).tolist()
    if st.session_state["current_id"] not in valid_ids:
        st.session_state["current_id"] = valid_ids[0]
        st.session_state["question_select_nonce"] += 1

    current_id = st.session_state["current_id"]
    id_to_label = dict(zip(filtered["id"].astype(str), filtered["選択ラベル"]))
    label_to_id = {label: qid for qid, label in id_to_label.items()}
    valid_labels = [id_to_label[qid] for qid in valid_ids]
    current_label = id_to_label[current_id]

    widget_key = f"problem_select_{st.session_state['question_select_nonce']}"

    def on_problem_select():
        selected = st.session_state[widget_key]
        st.session_state["current_id"] = label_to_id[selected]

    st.selectbox(
        "問題選択",
        valid_labels,
        index=valid_labels.index(current_label),
        key=widget_key,
        on_change=on_problem_select,
    )

    row = filtered[filtered["id"].astype(str) == st.session_state["current_id"]].iloc[0]
    qid = str(row["id"])
    current_index_zero = valid_ids.index(qid)
    total_count = len(valid_ids)
    progress_ratio = (current_index_zero + 1) / total_count if total_count else 0.0

    title = f"第{row['章']}章 {row['問題種別']}"
    if has_weekday_group and str(row.get("曜日グループ", "")).strip() and menu == "今日の課題":
        title = f"[曜日グループ {row['曜日グループ']}] " + title
    if str(row.get("年度", "")).strip():
        title = f"{row['年度']}年 " + title

    st.subheader(title)
    st.caption(f"ステータス: {compute_question_status(qid)}")
    st.caption(previous_action_text(qid))

    st.markdown("### 問題")
    render_multiline_text(row["問題文"])

    with st.expander("解答を表示"):
        st.markdown("### 解答")
        render_multiline_text(row["解答"])
        if str(row.get("解説", "")).strip():
            st.markdown("### 解説")
            render_multiline_text(row["解説"])

        st.markdown("### 自己評価")
        current_eval = get_primary_eval(qid)
        review_flagged = is_review_flagged(qid)
        cols = st.columns(3)
        for idx, option in enumerate(PRIMARY_EVAL_OPTIONS):
            with cols[idx]:
                st.button(
                    PRIMARY_EVAL_LABEL[option],
                    key=f"eval_{qid}_{option}",
                    use_container_width=True,
                    type="primary" if current_eval == option else "secondary",
                    on_click=set_primary_eval_callback,
                    args=(qid, option),
                )
        with cols[2]:
            st.button(
                REVIEW_FLAG_LABEL,
                key=f"review_flag_{qid}",
                use_container_width=True,
                type="primary" if review_flagged else "secondary",
                on_click=toggle_review_flag_callback,
                args=(qid,),
            )
        st.caption(previous_action_text(qid))

    fav_key = f"favorite_{qid}"
    st.checkbox(
        "お気に入り",
        value=is_favorite(qid),
        key=fav_key,
        on_change=set_favorite_callback,
        args=(qid, fav_key),
    )

    nav1, nav2 = st.columns(2)
    with nav1:
        st.button(
            "← 前へ",
            key=f"prev_{qid}",
            use_container_width=True,
            disabled=current_index_zero == 0,
            on_click=go_prev_callback,
            args=(valid_ids, current_index_zero),
        )
    with nav2:
        st.button(
            "次へ →",
            key=f"next_{qid}",
            use_container_width=True,
            disabled=current_index_zero >= len(valid_ids) - 1,
            on_click=go_next_callback,
            args=(valid_ids, current_index_zero),
        )

    st.markdown("---")
    st.markdown("### 進捗")
    m1, m2, m3 = st.columns(3)
    m1.metric("現在位置", f"{current_index_zero + 1} / {total_count}")
    m2.metric("残り問題数", f"{total_count - current_index_zero - 1}題")
    m3.metric("進捗率", f"{progress_ratio * 100:.0f}%")
    st.progress(progress_ratio)


ensure_state()
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

st.markdown(f"## {SITE_NAME}")
left = days_to_exam()
today_group, today_jp, now_tokyo = today_group_info()
today_str = now_tokyo.strftime("%Y-%m-%d")
if left >= 0:
    st.info(f"今日: **{today_str}** / 試験まであと **{left}日**（試験日: {EXAM_DATE.strftime('%Y-%m-%d')}）")
else:
    st.warning(f"今日: **{today_str}** / 試験日は {EXAM_DATE.strftime('%Y-%m-%d')} でした。")

has_weekday_group = "曜日グループ" in df.columns
menu = st.sidebar.radio("メニュー", MENU_OPTIONS, key="main_menu")

if menu == "教科書で学ぶ":
    chapter_options = sorted([x for x in df["章"].unique().tolist() if x], key=natural_sort_key)
    selected_chapter = st.sidebar.selectbox("章", chapter_options, key="textbook_chapter")
    st.subheader(f"第{selected_chapter}章 教科書で学ぶ")
    content = TEXTBOOK_LINKS.get(
        str(selected_chapter),
        {"summary": "この章の簡易まとめはまだ登録されていません。", "download_url": "https://www.actuaries.jp/examin/textbook/"},
    )

    st.markdown("### 簡易まとめ")
    st.write(content["summary"])

    if str(selected_chapter) == "1" and content["download_url"]:
        st.link_button("第1章のまとめを開く", content["download_url"], use_container_width=True)

    st.markdown("### 教科書リンク")
    st.link_button(
        "アクチュアリー会の教科書ページへ",
        "https://www.actuaries.jp/examin/textbook/",
        use_container_width=True,
    )
    st.stop()

if menu == "ホーム":
    render_dashboard(df)

    reco, reco_kind = pick_home_recommendation(df)
    button_label = "今日の1問を開く" if reco_kind == "今日の1問" else "この問題を開く"
    target_menu = "今日の課題" if reco_kind == "今日の1問" else "章ごとに学ぶ"

    st.markdown("### すぐ始める")
    c1, c2, c3 = st.columns(3)
    c1.info("今日の1問にすぐ飛べます。")
    c2.info("左メニューで『🚩 後で復習だけ表示』に切り替えできます。")
    c3.info("章別進捗を見ながら弱点を潰せます。")

    st.button(
        button_label,
        use_container_width=True,
        on_click=go_to_question,
        args=(str(reco["id"]), target_menu),
    )

    render_timer(now_tokyo)

    reco_text = f"{reco_kind}: {reco.get('年度', '')}年 第{reco['章']}章 {reco['問題種別']}"
    if reco_kind == "後で復習":
        st.error(reco_text)
    elif reco_kind == "要注意":
        st.warning(reco_text)
    else:
        st.success(reco_text)
    st.stop()

render_main_filters(menu, df)

filtered, today_total_count, today_remaining_count = filter_questions(df, menu, has_weekday_group)

if menu == "問題検索":
    render_search_results(filtered, has_weekday_group)
    st.stop()

filtered = sort_questions(filtered, has_weekday_group)

if menu == "今日の課題":
    t1, t2 = st.columns(2)
    t1.metric("今日の課題総数", f"{today_total_count}問")
    t2.metric("表示中の課題数", f"{today_remaining_count}問")
else:
    st.caption(f"問題数: {len(filtered)}")

render_problem_area(filtered, menu, has_weekday_group)
st.markdown("---")
render_timer(now_tokyo)
