import styles from "./ShokenAnswerView.module.css";

const ORDER = ["目的", "商品設計", "基礎率設定", "収益性", "リスク対応"];
const KEYS = {"目的":["目的","意義","ニーズ","契約者","公平","理解","保障"],"商品設計":["商品","設計","給付","保障","保険期間","払込","返戻","年金","販売","チャネル","査定"],"基礎率設定":["基礎率","予定","死亡率","発生率","解約率","利率","事業費","データ","安全割増","標準利率"],"収益性":["収益","利益","損益","収支","検証","キャッシュフロー","責任準備金","資本","費差","利差","価格"],"リスク対応":["リスク","管理","ストレス","感応度","モニタリング","改善","再保険","ヘッジ","ALM","販売上限","流動性"]};
const FALLBACK = {"目的":["顧客ニーズ、契約者保護、公平性を開発目的として明確にする。","中問の制度・原則を、なぜ本商品で重要かという形で所見へ接続する。","既契約者・他商品・会社全体への影響も踏まえて目的を定める。"],"商品設計":["給付、期間、払込、解約返戻金、販売方法を組み合わせて収支変動を制御する。","選択肢拡大の効果と逆選択・複雑性・説明負担を併せて検討する。","既存商品、チャネル、危険選択、契約取扱いまで一体で設計する。"],"基礎率設定":["自社・業界・公的データの同質性、十分性、最新性、将来トレンドを確認する。","死亡・発生率、予定利率、解約率、事業費率を相互整合的に設定する。","不確実性に応じた安全割増と複数シナリオを置き、実績で更新する。"],"収益性":["ベース、感応度、複合ストレス、販売量変動で将来収支を検証する。","一件利益、販売件数、必要資本、流動性、利益発生時期を分けて評価する。","短期利益だけでなく残存契約の将来利益と後年度損失を確認する。"],"リスク対応":["商品設計、料率、販売上限、危険選択、再保険、ALMを重層的に組み合わせる。","実績差を一過性と構造要因に分け、改善・停止・再開のトリガーを定める。","対応策の効果だけでなく契約者への不利益、副作用、実行可能性を確認する。"]};

const sentences = (text) => String(text || "").replace(/\r/g, "")
  .split(/(?<=[。！？])|\n+/).map((x) => x.trim()).filter((x) => x.length >= 10);
const short = (text, n = 112) => {
  const value = String(text || "").replace(/\s+/g, " ").trim();
  return value.length <= n ? value : `${value.slice(0, n).replace(/[、。\s]+$/, "")}…`;
};

function frameworkPoints(row) {
  const source = sentences(`${row.問題文 || ""}\n${row.合格レベル答案 || ""}`);
  return Object.fromEntries(ORDER.map((name) => {
    const ranked = source.map((text, index) => ({ text, index,
      score: (KEYS[name] || []).reduce((s, key) => s + (text.includes(key) ? 2 : 0), 0),
    })).filter((x) => x.score > 0).sort((a, b) => b.score - a.score || a.index - b.index);
    const result = [];
    for (const item of ranked) {
      const value = short(item.text);
      if (!result.includes(value)) result.push(value);
      if (result.length === 3) break;
    }
    for (const value of FALLBACK[name] || []) {
      if (result.length === 3) break;
      if (!result.includes(value)) result.push(value);
    }
    return [name, result.slice(0, 3)];
  }));
}

function problemSections(problem) {
  const lines = String(problem || "").replace(/\r/g, "").split("\n").map((x) => x.trim()).filter(Boolean);
  const result = [];
  let required = false;
  lines.forEach((line, index) => {
    if (/[＜【].*(論点|観点).*[＞】]/u.test(line) || /以下の(点|論点).*触れる/u.test(line)) { required = true; return; }
    if (/[＜【].*(前提|特徴|状況|環境変化).*[＞】]/u.test(line) || /^※/u.test(line)) required = false;
    let match = line.match(/^(（[ア-オ]）|\([ア-オ]\)|[①-⑩])\s*(.*)$/u);
    if (!match) match = line.match(/^([Ａ-ＦA-F][．.])\s*(.*)$/u);
    if (match) {
      let body = match[2].trim();
      if (!body || /^(次の|以下|あなた|このような|上記)/.test(body)) body = `${body} ${lines[index + 1] || ""}`.trim();
      body = body.replace(/。.*$/u, "").replace(/\s+/g, " ").trim();
      result.push(`${match[1]} ${short(body || "問題文で指定された論点", 64)}`);
    } else if (required && /^[-・]/u.test(line)) {
      result.push(`指定論点 ${short(line.replace(/^[-・]\s*/u, ""), 60)}`);
    }
  });
  return [...new Set(result)].slice(0, 12).length ? [...new Set(result)].slice(0, 12) : ["問題文に沿った答案"];
}

function categories(title) {
  const ranked = ORDER.map((name) => ({ name,
    score: (KEYS[name] || []).reduce((s, key) => s + (title.includes(key) ? 2 : 0), title.includes(name) ? 4 : 0),
  })).sort((a, b) => b.score - a.score);
  const result = ranked.filter((x) => x.score > 0).slice(0, 3).map((x) => x.name);
  for (const name of ORDER) { if (result.length >= 3) break; if (!result.includes(name)) result.push(name); }
  return result;
}

function answerParts(text, minimum) {
  const parts = String(text || "").split(/\n\s*\n/).map((x) => x.trim()).filter(Boolean);
  while (parts.length < minimum) {
    const index = parts.reduce((best, x, i) => best < 0 || x.length > parts[best].length ? i : best, -1);
    const list = sentences(parts[index]);
    if (index < 0 || list.length < 2) break;
    const half = Math.ceil(list.length / 2);
    parts.splice(index, 1, list.slice(0, half).join(""), list.slice(half).join(""));
  }
  return parts;
}

function distribute(parts, count) {
  const rest = [...parts];
  return Array.from({ length: count }, (_, i) => {
    if (i === count - 1) return rest.splice(0);
    return rest.splice(0, Math.max(1, Math.floor(rest.length / (count - i))));
  });
}

function threePoints(parts) {
  const result = [];
  for (const text of sentences(parts.join("\n"))) {
    const value = short(text, 104);
    if (!result.includes(value)) result.push(value);
    if (result.length === 3) break;
  }
  const extra = [
    "中問で確認した定義・意義を、所見の判断根拠として使う。",
    "問題文固有の前提を一般論へ当てはめ、影響の方向を示す。",
    "施策の効果に加え、限界・副作用・事後検証まで記述する。",
  ];
  for (const value of extra) { if (result.length === 3) break; if (!result.includes(value)) result.push(value); }
  return result.slice(0, 3);
}

function Framework({ row }) {
  const points = frameworkPoints(row);
  return <div className={styles.text}>
    <p><strong>{ORDER.join(" → ")}</strong></p>
    {ORDER.map((name) => <div key={name}>
      <h3>{name}</h3>
      {points[name].map((point, i) => <p className={styles.bullet} key={`${name}-${i}`}><strong>論点{i + 1}</strong>　{point}</p>)}
    </div>)}
  </div>;
}

function Answer({ row }) {
  const sections = problemSections(row.問題文);
  const groups = distribute(answerParts(row.合格レベル答案, sections.length), sections.length);
  return <div className={styles.text}>{sections.map((title, i) => {
    const frame = categories(title);
    const body = groups[i] || [];
    return <div key={`${row.id}-${title}`}>
      <h3>{title}</h3>
      <p><strong>【フレームワーク：{frame.join("・")}】</strong></p>
      <p><strong>中問知識の使い方：</strong>この区分の知識を、後続の所見では「{frame.join("・")}」の判断根拠として使う。</p>
      {threePoints(body).map((point, j) => <p className={styles.bullet} key={`${row.id}-${i}-${j}`}><strong>加点論点{j + 1}</strong>　{point}</p>)}
      {body.map((paragraph, j) => <p key={`${row.id}-${i}-body-${j}`}>{paragraph}</p>)}
    </div>;
  })}</div>;
}

export default function ShokenAnswerViewEnhanced({ row }) {
  return <div className={styles.answerView}>
    <section className={styles.section}>
      <h2>① フレームワークを用いた論点整理</h2>
      <Framework row={row} />
    </section>
    <section className={styles.section}>
      <div className={styles.answerHeading}>
        <h2>② 合格レベル答案</h2>
        <span>問題文の指定構成を土台に、各区分で最低3論点を展開</span>
      </div>
      <Answer row={row} />
    </section>
  </div>;
}
