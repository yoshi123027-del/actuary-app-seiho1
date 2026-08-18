import styles from "./ShokenAnswerView.module.css";
import QuestionComment from "./QuestionComment";

const ORDER = ["目的", "商品設計", "基礎率設定", "収益性", "リスク対応"];

const SHORT_SECTIONS = {
  "1": ["① 解約返戻金額と死亡保険金額に起因する契約者間の公平性", "① 低・無解約返戻金型商品における契約者理解"],
  "2": ["① 保険料率の細分化における公平性"],
  "3": ["① 第三分野商品の予定発生率と予定死亡率の相違", "① 社会保険制度に連動する場合の論点"],
  "4": [],
  "5": ["①（ア）危険選択の目的", "①（イ）医的査定と環境査定"],
  "6": ["① 商品毎収益検証の目的", "① 商品毎収益検証を実施する三つの手順"],
  "7": ["① 自社データを用いる場合のメリット・デメリット", "① 公共データを用いる場合のメリット・デメリット"],
  "8": ["① 個人年金保険の代表的な年金支払種類"],
  "9": ["（ア）事後モニタリングと改善アクションの目的・必要性"],
  "10": ["（ア）米ドル建一時払終身保険の標準利率"],
  "11": ["（ア）予定利率設定の一般的な留意点", "（イ）市中金利上昇・物価上昇が収益性に与える影響"],
  "12": ["（ア）一商品に複数給付を持たせる利点"],
  "13": ["（ア）予定事業費の十分性・普遍性・公平性", "（イ）件数比例・責任準備金比例と費用主義・効用主義"],
  "14": ["（ア）商品設計・契約群団・商品ポートフォリオ・事後管理"],
  "15": ["（ア）年金開始前・開始後にトンチン性を持たせる給付例", "（イ）トンチン性商品の長寿リスク"],
  "16": ["（ア）第三分野の予定発生率設定が困難な理由"],
};

const FALLBACK_GROUPS = {
  "1": ["1．死亡者の持ち分を生存者に移す商品設計上の工夫", "2．予定死亡率の設定方法", "3．解約益と将来利益の関係", "4．その他の留意点"],
  "2": ["1．商品設計上の留意点", "2．価格設定上の留意点", "3．その他の留意点"],
  "3": ["1．予定発生率の設定", "2．保険収支の不確実性を制御する商品設計・方策", "3．その他の留意点"],
  "4": ["① 国内金利の上昇", "② 死亡率の低下", "③ 顧客による余命推定技術の普及", "④ 未婚率（晩婚化・非婚化を含む）の上昇"],
  "5": ["1．商品設計上の留意点", "2．価格設定上の留意点", "3．その他の留意点"],
  "6": ["A．本商品の特性および解約率の特性", "B．解約率シナリオと他シナリオの連動性", "C．感応度分析・ストレステスト", "D．検証結果の活用"],
  "7": ["1．商品設計上の留意点", "2．計算基礎率の設定", "3．リスク管理上の留意点"],
  "8": ["1．安定的な商品供給", "2．将来の金利上昇に対する機動的な対応", "3．長寿リスクに対する顧客ニーズ", "4．競合他社に対する優位性と商品設計", "5．その他の留意点"],
  "9": ["A．一件当たり収益性の観点", "B．販売件数の観点", "C．総合判断・再モニタリング"],
  "10": ["1．予定利率の設定", "2．商品設計と競合後発商品への対応", "3．BBB格事業債を含む資産運用上のリスク", "4．収益検証・事後管理"],
  "11": ["1．十分性", "2．公平性", "3．収益性", "4．商品設計・計算基礎率・事後管理"],
  "12": ["1．販売政策", "2．各商品の給付設計", "3．各商品の基礎率設定・危険選択", "4．収益性・事後モニタリング"],
  "13": ["1．開発目的・商品設計", "2．販売政策", "3．実際事業費と予定事業費体系", "4．収益性・事後管理"],
  "14": ["1．環境変化が商品に及ぼす影響", "2．事後モニタリングの内容と目的", "3．商品・料率・販売政策その他の対応策"],
  "15": ["1．商品設計・契約取扱い", "2．計算基礎率の設定", "3．販売方針", "4．収益の性質・事後モニタリング・改善"],
  "16": ["1．商品A・Bの収益性の特徴", "2．競争環境の変化が与える影響", "3．収益性検証の目的・実施手順", "4．検証結果の活用・事後管理"],
};

const DOMAIN_TERMS = [
  "契約者保護", "契約者間の公平性", "公平性", "十分性", "収益性", "健全性", "商品設計",
  "予定死亡率", "予定発生率", "予定利率", "予定解約率", "予定事業費", "計算基礎率",
  "解約率", "解約益", "将来利益", "長寿リスク", "逆選択", "モラルリスク", "危険選択",
  "収益検証", "感応度分析", "ストレステスト", "事後モニタリング", "再保険", "ALM",
  "販売方針", "販売政策", "リスク管理", "内部留保", "資産運用", "契約者理解",
];

function clean(value) {
  return String(value || "").replace(/\r/g, "").replace(/[ \t]+/g, " ").trim();
}

function paragraphUnits(text) {
  return clean(text).split(/\n\s*\n/u).map((part) => part.trim()).filter(Boolean);
}

function sentenceUnits(text) {
  const source = clean(text);
  const matches = source.match(/[^。！？\n]+[。！？]?/gu) || [];
  return matches.map((part) => part.trim()).filter((part) => part.length >= 6);
}

function expandUnits(units, minimumCount) {
  const result = [...units];
  let guard = 0;
  while (result.length < minimumCount && guard < 50) {
    guard += 1;
    let targetIndex = -1;
    let targetSentences = [];
    result.forEach((unit, index) => {
      const pieces = sentenceUnits(unit);
      if (pieces.length >= 2 && pieces.length > targetSentences.length) {
        targetIndex = index;
        targetSentences = pieces;
      }
    });
    if (targetIndex < 0) break;
    const midpoint = Math.ceil(targetSentences.length / 2);
    result.splice(
      targetIndex,
      1,
      targetSentences.slice(0, midpoint).join(""),
      targetSentences.slice(midpoint).join(""),
    );
  }
  return result;
}

function frameworkEntries(text) {
  const source = String(text || "").replace(/\r/g, "");
  const blocks = source.split(/\n\s*\n/u).map((part) => part.trim()).filter(Boolean);
  return ORDER.map((key, index) => {
    const block = blocks[index] || "";
    const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
    const body = lines.length > 1 ? lines.slice(1).join(" ") : lines.join(" ");
    const compact = body.replace(/[。！？]+$/u, "").split(/[、，]/u).map((part) => part.trim()).filter(Boolean).slice(0, 3).join("・");
    return { key, text: compact || "問題文から主要論点を確認" };
  });
}

function extractMajorItems(problem, fallback) {
  const lines = String(problem || "").replace(/\r/g, "").split("\n").map((line) => line.trim()).filter(Boolean);
  const letterGroups = [];
  const requestGroups = [];
  let letters = [];
  let requested = [];
  let collectingRequested = false;

  const flushLetters = () => {
    if (letters.length) letterGroups.push(letters);
    letters = [];
  };
  const flushRequested = () => {
    if (requested.length) requestGroups.push(requested);
    requested = [];
  };

  lines.forEach((line) => {
    if (/^(①|②|③|④|（[ア-オ]）|\([ア-オ]\))/u.test(line)) {
      flushLetters();
      if (collectingRequested) flushRequested();
      collectingRequested = false;
    }

    const letter = line.match(/^([Ａ-ＦA-F][．.])\s*(.+)$/u);
    if (letter) {
      letters.push(`${letter[1]} ${letter[2].replace(/。.*$/u, "").trim()}`);
      return;
    }

    if (/以下の(点|論点)|次の(点|観点)|解答にあたっては/u.test(line)) {
      flushRequested();
      collectingRequested = true;
      return;
    }

    if (collectingRequested && /^[・\-]/u.test(line)) {
      requested.push(line.replace(/^[・\-]\s*/u, "").replace(/。.*$/u, "").trim());
      return;
    }

    if (collectingRequested && /^(※|なお、|ただし、)/u.test(line)) {
      flushRequested();
      collectingRequested = false;
    }
  });

  flushLetters();
  flushRequested();

  const lastLetters = letterGroups.length ? letterGroups[letterGroups.length - 1] : [];
  const lastRequested = requestGroups.length ? requestGroups[requestGroups.length - 1] : [];
  const selected = lastLetters.length ? lastLetters : lastRequested;
  const unique = [...new Set(selected)].filter((item) => item.length >= 4).slice(0, 8);

  if (!unique.length) return fallback;

  const other = fallback.find((item) => item.includes("その他"));
  if (!lastLetters.length && other && !unique.some((item) => item.includes("その他"))) {
    return [...unique, other];
  }
  return unique;
}

function allocateInOrder(items, count) {
  if (count <= 0) return [];
  const remaining = [...items];
  return Array.from({ length: count }, (_, index) => {
    if (index === count - 1) return remaining.splice(0);
    const groupsLeft = count - index;
    const minimumForRest = groupsLeft - 1;
    const take = Math.max(1, Math.floor(remaining.length / groupsLeft));
    return remaining.splice(0, Math.min(take, Math.max(1, remaining.length - minimumForRest)));
  });
}

function bulletsFrom(parts) {
  const bullets = [];
  parts.forEach((part) => {
    sentenceUnits(part).forEach((sentence) => {
      const pieces = sentence.length > 120
        ? sentence.split(/(?=また、)|(?=なお、)|(?=一方、)|(?=ただし、)|(?=このため、)|(?=したがって、)/u)
        : [sentence];
      pieces.forEach((piece) => {
        const item = clean(piece).replace(/^[-・]\s*/u, "");
        if (item && !bullets.includes(item)) bullets.push(item);
      });
    });
  });
  return bullets;
}

function emphasisTerms(entries) {
  const source = entries.map((entry) => entry.text).join(" ");
  const terms = DOMAIN_TERMS.filter((term) => source.includes(term));
  source.split(/[、。，・／/（）()「」『』：:\n]/u)
    .map((part) => part.trim())
    .filter((part) => part.length >= 3 && part.length <= 18)
    .forEach((part) => terms.push(part));
  return [...new Set(terms)].sort((a, b) => b.length - a.length);
}

function EmphasizedText({ text, terms }) {
  const nodes = [];
  let cursor = 0;
  let key = 0;

  while (cursor < text.length) {
    let bestIndex = -1;
    let bestTerm = "";
    terms.forEach((term) => {
      const index = text.indexOf(term, cursor);
      if (index < 0) return;
      if (bestIndex < 0 || index < bestIndex || (index === bestIndex && term.length > bestTerm.length)) {
        bestIndex = index;
        bestTerm = term;
      }
    });

    if (bestIndex < 0) {
      nodes.push(text.slice(cursor));
      break;
    }
    if (bestIndex > cursor) nodes.push(text.slice(cursor, bestIndex));
    nodes.push(<strong key={`strong-${key}`}>{bestTerm}</strong>);
    key += 1;
    cursor = bestIndex + bestTerm.length;
  }

  return nodes.length ? nodes : text;
}

function prepare(row) {
  const safeRow = row || {};
  const id = String(safeRow.id || "");
  const structuredShortAnswers = Array.isArray(safeRow.短答) ? safeRow.短答 : null;
  const structuredGroups = Array.isArray(safeRow.論文式答案) ? safeRow.論文式答案 : null;
  const shortTitles = SHORT_SECTIONS[id] || [];
  const fallback = FALLBACK_GROUPS[id] || ["問題文で指定された論点"];
  const titles = extractMajorItems(safeRow.問題文, fallback);
  const rawUnits = paragraphUnits(safeRow.合格レベル答案);
  const units = expandUnits(rawUnits, shortTitles.length + titles.length * 2);
  const shortUnits = units.slice(0, Math.min(shortTitles.length, units.length));
  const essayUnits = units.slice(shortUnits.length);
  const framework = frameworkEntries(safeRow.フレームワークを用いた論点整理);
  const terms = emphasisTerms(framework);
  const allocations = allocateInOrder(essayUnits, titles.length);

  return {
    shortAnswers: structuredShortAnswers || shortTitles.map((title, index) => ({ title, text: shortUnits[index] || "" })),
    framework,
    terms,
    groups: structuredGroups || titles.map((title, index) => ({
      title,
      bullets: bulletsFrom(allocations[index] || []),
    })),
  };
}

function Framework({ entries }) {
  return (
    <div className={styles.frameworkBox}>
      <h3>論文式の思考フレーム</h3>
      <p className={styles.frameworkFlow}><strong>{ORDER.join(" → ")}</strong></p>
      {entries.map((entry) => <p key={entry.key}><strong>{entry.key}：</strong>{entry.text}</p>)}
      <p className={styles.frameworkNote}>1分程度で答案の骨格と加点論点を整理するメモ。</p>
    </div>
  );
}

export default function ShokenAnswerView({ row = {} }) {
  const prepared = prepare(row);

  return (
    <div className={styles.answerView}>
      <section className={styles.section}>
        <div className={styles.answerHeading}><h2>合格レベル答案</h2></div>

        {prepared.shortAnswers.map((answer) => answer.text && (
          <div className={styles.shortAnswer} key={answer.title}>
            <h3>{answer.title}</h3>
            <div className={styles.text}><p>{answer.text}</p></div>
          </div>
        ))}

        <Framework entries={prepared.framework} />

        <div className={styles.essayHeading}><h3>論文式答案</h3></div>
        <div className={styles.text}>
          {prepared.groups.map((group) => (
            <section className={styles.majorGroup} key={group.title}>
              <h3 className={styles.majorTitle}>{group.title}</h3>
              {Array.isArray(group.subgroups) && group.subgroups.length ? group.subgroups.map((subgroup) => (
                <div className={styles.middleGroup} key={`${group.title}-${subgroup.title}`}>
                  <h4 className={styles.middleTitle}>{subgroup.title}</h4>
                  {subgroup.bullets.map((bullet, index) => (
                    <p className={styles.bullet} key={`${group.title}-${subgroup.title}-${index}`}>
                      <EmphasizedText text={bullet} terms={prepared.terms} />
                    </p>
                  ))}
                </div>
              )) : group.bullets.map((bullet, index) => (
                <p className={styles.bullet} key={`${group.title}-${index}`}>
                  <EmphasizedText text={bullet} terms={prepared.terms} />
                </p>
              ))}
            </section>
          ))}
        </div>
        <QuestionComment row={row} />
      </section>
    </div>
  );
}
