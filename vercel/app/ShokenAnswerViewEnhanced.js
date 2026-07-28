import styles from "./ShokenAnswerView.module.css";

const ORDER = ["目的","商品設計","基礎率設定","収益性","リスク対応"];
const SHORT_SECTIONS = {"1":["① 解約返戻金額と死亡保険金額に起因する契約者間の公平性","① 低・無解約返戻金型商品における契約者理解"],"2":["① 保険料率の細分化における公平性"],"3":["① 第三分野商品の予定発生率と予定死亡率の相違","① 社会保険制度に連動する場合の論点"],"4":[],"5":["①（ア）危険選択の目的","①（イ）医的査定と環境査定"],"6":["① 商品毎収益検証の目的","① 商品毎収益検証を実施する三つの手順"],"7":["① 自社データを用いる場合のメリット・デメリット","① 公共データを用いる場合のメリット・デメリット"],"8":["① 個人年金保険の代表的な年金支払種類"],"9":["（ア）事後モニタリングと改善アクションの目的・必要性"],"10":["（ア）米ドル建一時払終身保険の標準利率"],"11":["（ア）予定利率設定の一般的な留意点","（イ）市中金利上昇・物価上昇が収益性に与える影響"],"12":["（ア）一商品に複数給付を持たせる利点"],"13":["（ア）予定事業費の十分性・普遍性・公平性","（イ）件数比例・責任準備金比例と費用主義・効用主義"],"14":["（ア）商品設計・契約群団・商品ポートフォリオ・事後管理"],"15":["（ア）年金開始前・開始後にトンチン性を持たせる給付例","（イ）トンチン性商品の長寿リスク"],"16":["（ア）第三分野の予定発生率設定が困難な理由"]};
const FALLBACK_GROUPS = {"1":["1．死亡者の持ち分を生存者に移す商品設計上の工夫","2．予定死亡率の設定方法","3．解約益と将来利益の関係","4．その他の留意点"],"2":["1．商品設計上の留意点","2．価格設定上の留意点","3．その他の留意点"],"3":["1．予定発生率の設定","2．保険収支の不確実性を制御する商品設計・方策","3．その他の留意点"],"4":["1．国内金利の上昇","2．死亡率の低下","3．顧客による余命推定技術の普及"],"5":["1．商品設計上の留意点","2．価格設定上の留意点","3．その他の留意点"],"6":["A．本商品の特性および解約率の特性","B．解約率シナリオと他シナリオの連動性","C．感応度分析・ストレステスト","D．検証結果の活用"],"7":["1．商品設計上の留意点","2．計算基礎率の設定","3．リスク管理上の留意点"],"8":["1．安定的な商品供給","2．将来の金利上昇に対する機動的な対応","3．長寿リスクに対する顧客ニーズ","4．競合他社に対する優位性と商品設計","5．その他の留意点"],"9":["A．一件当たり収益性の観点","B．販売件数の観点","C．総合判断・再モニタリング"],"10":["1．予定利率の設定","2．商品設計と競合後発商品への対応","3．BBB格事業債を含む資産運用上のリスク","4．収益検証・事後管理"],"11":["1．十分性","2．公平性","3．収益性","4．商品設計・計算基礎率・事後管理"],"12":["1．販売政策","2．各商品の給付設計","3．各商品の基礎率設定・危険選択","4．収益性・事後モニタリング"],"13":["1．開発目的・商品設計","2．販売政策","3．実際事業費と予定事業費体系","4．収益性・事後管理"],"14":["1．環境変化が商品に及ぼす影響","2．事後モニタリングの内容と目的","3．商品・料率・販売政策その他の対応策"],"15":["1．商品設計・契約取扱い","2．計算基礎率の設定","3．販売方針","4．収益の性質・事後モニタリング・改善"],"16":["1．商品A・Bの収益性の特徴","2．競争環境の変化が与える影響","3．収益性検証の目的・実施手順","4．検証結果の活用・事後管理"]};

const HEADING_MAP = {
  "【①何を実現・保護するか】": "目的",
  "【①何を守るのか】": "目的",
  "【目的】": "目的",
  "【②問題文から読み取る変化・制約】": "変化",
  "【②何が変化したのか】": "変化",
  "【変化】": "変化",
  "【③収支・契約者・リスクへの影響】": "影響",
  "【③何に影響するのか】": "影響",
  "【影響】": "影響",
  "【④確認・計測する方法】": "計測",
  "【④どう測るのか】": "計測",
  "【計測】": "計測",
  "【⑤商品・料率・販売・リスク管理への反映】": "経営対応",
  "【⑤どう対応するのか】": "経営対応",
  "【経営対応】": "経営対応",
};

function normalize(text) {
  return String(text || "").replace(/\r/g, "").replace(/[ \t]+/g, " ").trim();
}

function sentences(text) {
  return normalize(text)
    .split(/(?<=[。！？])|\n+/u)
    .map((part) => part.trim())
    .filter((part) => part.length >= 8);
}

function answerUnits(text, minimumCount) {
  const units = normalize(text).split(/\n\s*\n/u).map((part) => part.trim()).filter(Boolean);
  while (units.length < minimumCount) {
    let target = -1;
    let pieces = null;
    units.forEach((unit, index) => {
      const list = sentences(unit);
      if (list.length < 2) return;
      if (target < 0 || unit.length > units[target].length) {
        target = index;
        const half = Math.ceil(list.length / 2);
        pieces = [list.slice(0, half).join(""), list.slice(half).join("")];
      }
    });
    if (target < 0) break;
    units.splice(target, 1, ...pieces);
  }
  return units;
}

function compactFramework(text) {
  const buckets = Object.fromEntries(ORDER.map((key) => [key, []]));
  let current = null;
  normalize(text).split("\n").forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) return;
    if (HEADING_MAP[line]) {
      current = HEADING_MAP[line];
      return;
    }
    if (current) buckets[current].push(line);
  });
  return ORDER.map((key) => {
    const clauses = buckets[key].join(" ")
      .replace(/[。！？]/gu, "")
      .split(/[、，]/u)
      .map((part) => part.trim())
      .filter(Boolean)
      .slice(0, 3);
    return { key, text: clauses.join("・") || "問題文から主要論点を確認" };
  });
}

function extractMajorItems(problem, fallback) {
  const lines = normalize(problem).split("\n").map((line) => line.trim()).filter(Boolean);
  const letterBlocks = [];
  const requestBlocks = [];
  let letters = [];
  let requested = [];
  let inRequestedBlock = false;

  const flushLetters = () => {
    if (letters.length) letterBlocks.push(letters);
    letters = [];
  };
  const flushRequested = () => {
    if (requested.length) requestBlocks.push(requested);
    requested = [];
  };

  lines.forEach((line) => {
    if (/^(①|②|③|④|（[ア-オ]）|\([ア-オ]\))/u.test(line)) {
      flushLetters();
      if (inRequestedBlock) flushRequested();
      inRequestedBlock = false;
    }
    const letter = line.match(/^([Ａ-ＦA-F][．.])\s*(.+)$/u);
    if (letter) {
      letters.push(`${letter[1]} ${letter[2].replace(/。.*$/u, "").trim()}`);
      return;
    }
    if (/以下の(点|論点)|次の(点|観点)|解答にあたっては/u.test(line)) {
      flushRequested();
      inRequestedBlock = true;
      return;
    }
    if (inRequestedBlock && /^[・\-]/u.test(line)) {
      requested.push(line.replace(/^[・\-]\s*/u, "").replace(/。.*$/u, "").trim());
      return;
    }
    if (inRequestedBlock && /^(※|なお、|ただし、)/u.test(line)) {
      flushRequested();
      inRequestedBlock = false;
    }
  });
  flushLetters();
  flushRequested();

  const result = letterBlocks.at(-1) || requestBlocks.at(-1) || [];
  const unique = [...new Set(result)].filter((item) => item.length >= 4).slice(0, 8);
  return unique.length ? unique : fallback;
}

function allocate(items, count) {
  const remaining = [...items];
  return Array.from({ length: count }, (_, index) => {
    if (index === count - 1) return remaining.splice(0);
    const after = count - index - 1;
    const take = Math.max(1, Math.floor(remaining.length / (count - index)));
    return remaining.splice(0, Math.min(take, Math.max(1, remaining.length - after)));
  });
}

function makeBullets(parts) {
  const result = [];
  parts.forEach((part) => {
    sentences(part).forEach((sentence) => {
      const values = sentence.length > 125
        ? sentence.split(/(?=また、)|(?=なお、)|(?=一方、)|(?=ただし、)/u)
        : [sentence];
      values.forEach((value) => {
        const item = normalize(value).replace(/^[-・]\s*/u, "");
        if (item && !result.includes(item)) result.push(item);
      });
    });
  });
  return result;
}

function ensureThree(bullets, title) {
  const result = [...bullets];
  [
    `${title}について、問題文の前提と基本的な考え方を確認する。`,
    "契約者間の公平性、収益性および健全性への影響を確認する。",
    "実施後は計画と実績を比較し、必要に応じて見直す。",
  ].forEach((item) => {
    if (result.length < 3 && !result.includes(item)) result.push(item);
  });
  return result;
}

function frameworkTerms(entries) {
  return entries.flatMap((entry) => entry.text
    .replace(/[【】「」『』（）()・／,:：。！？]/gu, " ")
    .split(/\s+/u))
    .filter((term) => term.length >= 3 && term.length <= 14);
}

function capGroups(groups, limit = 3500) {
  const copied = groups.map((group) => ({ ...group, bullets: [...group.bullets] }));
  const count = () => copied.reduce(
    (sum, group) => sum + group.bullets.reduce((inner, bullet) => inner + bullet.length, 0),
    0,
  );
  while (count() > limit) {
    const target = [...copied].reverse().find((group) => group.bullets.length > 3);
    if (!target) break;
    target.bullets.pop();
  }
  return { groups: copied, characters: count() };
}

function prepare(row) {
  const id = String(row.id);
  const shortTitles = SHORT_SECTIONS[id] || [];
  const fallback = FALLBACK_GROUPS[id] || ["問題文で指定された論点"];
  const units = answerUnits(row.合格レベル答案, shortTitles.length + fallback.length * 2);
  const shortUnits = units.splice(0, Math.min(shortTitles.length, units.length));
  const shortAnswers = shortTitles.map((title, index) => ({
    title,
    paragraphs: shortUnits[index] ? [shortUnits[index]] : [],
  }));

  const titles = extractMajorItems(row.問題文, fallback);
  const allocations = allocate(units, titles.length);
  const framework = compactFramework(row.フレームワークを用いた論点整理);
  const terms = frameworkTerms(framework);
  const groups = titles.map((title, index) => ({
    title,
    bullets: ensureThree(makeBullets(allocations[index] || []), title),
  }));
  return { shortAnswers, framework, terms, ...capGroups(groups) };
}

function Framework({ entries }) {
  return <div className={styles.frameworkBox}>
    <h3>論文式の思考フレーム</h3>
    <p className={styles.frameworkFlow}><strong>{ORDER.join(" → ")}</strong></p>
    {entries.map((entry) => (
      <p key={entry.key}><strong>{entry.key}：</strong>{entry.text}</p>
    ))}
    <p className={styles.frameworkNote}>1分程度で答案の骨格と加点論点を整理するメモ。本文の章立ては問題文と公式解答例の順序を優先する。</p>
  </div>;
}

export default function ShokenAnswerViewEnhanced({ row }) {
  const prepared = prepare(row);
  return <div className={styles.answerView}>
    <section className={styles.section}>
      <div className={styles.answerHeading}>
        <h2>合格レベル答案</h2>
        <span>公式解答例を土台に、問題文の指定構成で整理</span>
      </div>

      {prepared.shortAnswers.map((answer) => (
        <div className={styles.shortAnswer} key={answer.title}>
          <h3>{answer.title}</h3>
          <div className={styles.text}>
            {answer.paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
          </div>
        </div>
      ))}

      <Framework entries={prepared.framework} />

      <div className={styles.essayHeading}>
        <h3>論文式答案</h3>
        <span>約{prepared.characters.toLocaleString("ja-JP")}字／3,500字以内</span>
      </div>

      <div className={styles.text}>
        {prepared.groups.map((group) => (
          <section className={styles.majorGroup} key={group.title}>
            <h3 className={styles.majorTitle}>{group.title}</h3>
            {group.bullets.map((bullet, index) => {
              const emphasized = prepared.terms.some((term) => bullet.includes(term));
              return <p className={styles.bullet} key={index}>
                {emphasized ? <strong>{bullet}</strong> : bullet}
              </p>;
            })}
          </section>
        ))}
      </div>
    </section>
  </div>;
}
