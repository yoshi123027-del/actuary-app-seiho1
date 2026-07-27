import styles from "./ShokenAnswerView.module.css";

const FRAMEWORK_ORDER = ["目的", "変化", "影響", "計測", "経営対応"];

const HEADING_ALIASES = {
  "【目的】": { key: "目的" },
  "【①何を実現・保護するか】": { key: "目的" },
  "【①何を守るのか】": { key: "目的" },
  "【変化】": { key: "変化" },
  "【②問題文から読み取る変化・制約】": { key: "変化" },
  "【②何が変化したのか】": { key: "変化" },
  "【影響】": { key: "影響" },
  "【③収支・契約者・リスクへの影響】": { key: "影響" },
  "【③何に影響するのか】": { key: "影響" },
  "【計測】": { key: "計測" },
  "【④確認・計測する方法】": { key: "計測" },
  "【④どう測るのか】": { key: "計測" },
  "【二つを併用する視点】": { key: "計測", prefix: "併用の視点：" },
  "【経営対応】": { key: "経営対応" },
  "【⑤商品・料率・販売・リスク管理への反映】": { key: "経営対応" },
  "【⑤どう対応するのか】": { key: "経営対応" },
};

const ANSWER_STRUCTURES = {
  "1": [
    ["① 解約返戻金額と死亡保険金額に起因する契約者間の公平性", ["目的", "影響"], 1],
    ["① 低・無解約返戻金型商品における契約者理解", ["目的", "経営対応"], 1],
    ["② 死亡者持分を生存者へ移転する商品設計", ["変化", "経営対応"], 2],
    ["② 予定死亡率その他の計算基礎率", ["影響", "計測"], 2],
    ["② 解約益と将来利益の関係・収益検証", ["影響", "計測"], 2],
    ["② 販売方針と事後モニタリング", ["計測", "経営対応"], 1]
  ],
  "2": [
    ["① 保険料率の細分化における公平性", ["目的", "影響"], 1],
    ["② ライフスタイル指標を料率区分に用いる要件", ["変化", "計測"], 2],
    ["② 商品設計上の留意点", ["変化", "経営対応"], 1],
    ["② 価格設定と危険選択", ["影響", "計測"], 2],
    ["② 契約者説明・プライバシー・社会的容認性", ["目的", "経営対応"], 1],
    ["② 収益検証と販売後モニタリング", ["計測", "経営対応"], 1]
  ],
  "3": [
    ["① 第三分野の予定発生率と死亡保険の予定死亡率の相違", ["変化", "影響"], 1],
    ["① 社会保険制度に連動する場合の困難性", ["変化", "影響"], 1],
    ["② 介護終身年金の商品設計", ["目的", "経営対応"], 2],
    ["② 予定発生率の設定", ["影響", "計測"], 2],
    ["② その他の計算基礎率と収益検証", ["影響", "計測"], 1],
    ["② 保険収支の不確実性を制御する方策", ["計測", "経営対応"], 2],
    ["② 販売後のモニタリングと改善", ["計測", "経営対応"], 1]
  ],
  "4": [
    ["選択① 国内金利の上昇", ["変化", "影響", "計測", "経営対応"], 2],
    ["選択② 死亡率の低下", ["変化", "影響", "計測", "経営対応"], 2],
    ["選択③ 顧客による余命推定技術の普及", ["変化", "影響", "計測", "経営対応"], 2]
  ],
  "5": [
    ["①（ア）危険選択の目的", ["目的"], 1],
    ["①（イ）医的査定と環境査定", ["計測"], 1],
    ["② インターネットチャネルにおける危険選択の特徴", ["変化", "影響"], 2],
    ["② 商品設計上の留意点", ["経営対応"], 1],
    ["② 価格設定上の留意点", ["影響", "計測"], 1],
    ["② 営業職員チャネル・他社商品との関係", ["変化", "影響"], 1],
    ["② リスク管理と事後モニタリング", ["計測", "経営対応"], 1]
  ],
  "6": [
    ["① 商品毎収益検証の目的", ["目的"], 1],
    ["① 商品毎収益検証を実施する三つの手順", ["計測"], 1],
    ["② A．商品特性および解約率の特性", ["変化", "影響"], 2],
    ["② B．解約率シナリオと他シナリオの連動性", ["変化", "計測"], 2],
    ["② C．感応度分析・ストレステスト", ["計測"], 1],
    ["② D．検証結果の経営への活用", ["経営対応"], 2]
  ],
  "7": [
    ["① 自社データを用いる場合のメリット・デメリット", ["計測"], 1],
    ["① 公共データを用いる場合のメリット・デメリット", ["計測"], 1],
    ["② 認知症保険の商品設計", ["目的", "変化", "経営対応"], 2],
    ["② 計算基礎率の設定", ["影響", "計測"], 2],
    ["② 商品導入に伴うリスク", ["変化", "影響"], 1],
    ["② リスク管理・事後モニタリング", ["計測", "経営対応"], 2]
  ],
  "8": [
    ["① 個人年金保険の代表的な四つの年金支払種類", ["目的"], 1],
    ["② 安定的な商品供給", ["目的", "経営対応"], 1],
    ["② 将来の金利上昇に対する機動的な対応", ["変化", "影響", "計測", "経営対応"], 2],
    ["② 長寿リスクに対する顧客ニーズ", ["目的", "変化", "経営対応"], 1],
    ["② 競合他社に対する優位性と商品設計上の工夫", ["変化", "経営対応"], 2],
    ["② 基礎率・ALM・販売後管理", ["影響", "計測", "経営対応"], 2]
  ],
  "9": [
    ["（ア）事後モニタリングと改善アクションの目的・必要性", ["目的", "計測"], 1],
    ["（イ）A．一件当たり収益性の低下要因", ["変化", "影響", "計測"], 2],
    ["（イ）A．一件当たり収益性を改善するアクションと留意点", ["経営対応"], 2],
    ["（イ）B．販売件数の変化要因と改善アクション", ["変化", "影響", "経営対応"], 2],
    ["（イ）総合判断と再モニタリング", ["計測", "経営対応"], 1]
  ],
  "10": [
    ["（ア）米ドル建一時払終身保険の標準利率", ["計測"], 1],
    ["（イ）標準利率を踏まえた予定利率設定", ["変化", "影響", "計測"], 2],
    ["（イ）商品設計と競合後発商品への対応", ["変化", "経営対応"], 2],
    ["（イ）BBB格事業債の信用リスク", ["影響"], 1],
    ["（イ）信用・金利・為替・流動性リスクの管理", ["計測", "経営対応"], 2],
    ["（イ）収益検証と販売後管理", ["計測", "経営対応"], 1]
  ],
  "11": [
    ["（ア）予定利率設定の一般的な留意点", ["計測"], 1],
    ["（イ）① 市中金利上昇が収益性に与える影響", ["変化", "影響"], 1],
    ["（イ）② 物価上昇が収益性に与える影響", ["変化", "影響"], 1],
    ["（ウ）保険料の十分性", ["目的", "計測"], 2],
    ["（ウ）保険料の公平性", ["目的", "影響"], 1],
    ["（ウ）保険料の収益性・改定後の管理", ["計測", "経営対応"], 2]
  ],
  "12": [
    ["（ア）一商品に複数給付を持たせる利点", ["目的", "影響"], 1],
    ["（イ）販売政策", ["変化", "経営対応"], 1],
    ["（イ）三商品の給付設計", ["変化", "経営対応"], 2],
    ["（イ）各商品の基礎率設定", ["影響", "計測"], 2],
    ["（イ）危険選択への影響", ["影響", "計測"], 1],
    ["（イ）事後モニタリング", ["計測"], 1],
    ["（イ）販売後の収益変動と対応", ["影響", "経営対応"], 2]
  ],
  "13": [
    ["（ア）予定事業費の十分性・普遍性・公平性", ["目的", "計測"], 1],
    ["（イ）件数比例・責任準備金比例と費用主義・効用主義", ["計測"], 1],
    ["（ウ）開発目的", ["目的"], 1],
    ["（ウ）保険給付等の詳細設計", ["変化", "経営対応"], 1],
    ["（ウ）販売政策", ["変化", "経営対応"], 1],
    ["（ウ）実際事業費と予定事業費体系", ["影響", "計測"], 2],
    ["（ウ）本商品の収益性と事後管理", ["計測", "経営対応"], 2]
  ],
  "14": [
    ["（ア）① 商品設計による収支変動の制御", ["経営対応"], 1],
    ["（ア）② 契約群団のコントロール", ["経営対応"], 1],
    ["（ア）③ 商品ポートフォリオ", ["経営対応"], 1],
    ["（ア）④ 事後モニタリングと改善アクション", ["計測", "経営対応"], 1],
    ["（イ）環境変化が商品に及ぼす影響", ["変化", "影響"], 2],
    ["（イ）事後モニタリングの内容と目的", ["計測"], 2],
    ["（イ）商品・料率・販売政策その他の対応策", ["経営対応"], 2]
  ],
  "15": [
    ["（ア）年金開始前・開始後にトンチン性を持たせる給付例", ["変化", "経営対応"], 1],
    ["（イ）トンチン性商品の長寿リスク", ["影響"], 1],
    ["（ウ）商品設計と契約取扱い", ["目的", "変化", "経営対応"], 2],
    ["（ウ）計算基礎率の設定", ["影響", "計測"], 2],
    ["（ウ）販売方針", ["目的", "経営対応"], 1],
    ["（ウ）収益の性質と事後モニタリング", ["影響", "計測"], 2],
    ["（ウ）リスク顕在時の改善アクション", ["経営対応"], 1]
  ],
  "16": [
    ["（ア）第三分野の予定発生率設定が困難な三つの理由", ["変化", "影響"], 1],
    ["（イ）商品A・Bの収益性の特徴", ["変化", "影響"], 2],
    ["（イ）競争環境の変化が与える影響", ["変化", "影響"], 1],
    ["（イ）収益性検証の目的", ["目的"], 1],
    ["（イ）収益性検証の実施手順", ["計測"], 2],
    ["（イ）検証結果の活用方法", ["経営対応"], 2],
    ["（イ）事後モニタリングと再検証", ["計測", "経営対応"], 1]
  ]
};

function normalizeFramework(text) {
  const buckets = Object.fromEntries(FRAMEWORK_ORDER.map((key) => [key, []]));
  let current = null;
  let prefix = "";
  let recognized = false;

  String(text || "").split("\n").forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) return;
    const alias = HEADING_ALIASES[line];
    if (alias) {
      current = alias.key;
      prefix = alias.prefix || "";
      recognized = true;
      return;
    }
    if (current) buckets[current].push(`${prefix}${line}`);
  });

  if (!recognized) return String(text || "");
  return FRAMEWORK_ORDER
    .filter((key) => buckets[key].length)
    .map((key) => `【${key}】\n${buckets[key].join("\n")}`)
    .join("\n\n");
}

function RichText({ text }) {
  const lines = String(text || "").split("\n");
  const elements = [];
  let paragraph = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    elements.push(<p key={`p-${elements.length}`}>{paragraph.join(" ")}</p>);
    paragraph = [];
  };

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      return;
    }
    if (/^(【.+】|■.+|[①-⑩].+)/.test(line)) {
      flushParagraph();
      elements.push(<h3 key={`h-${index}`}>{line}</h3>);
      return;
    }
    if (/^[-・]/.test(line)) {
      flushParagraph();
      elements.push(<p className={styles.bullet} key={`b-${index}`}>{line.replace(/^[-・]\s*/, "")}</p>);
      return;
    }
    paragraph.push(line);
  });
  flushParagraph();

  return <div className={styles.text}>{elements}</div>;
}

function splitAtSentenceBoundary(text) {
  const sentences = String(text).match(/[^。！？]+[。！？]?/g)?.map((part) => part.trim()).filter(Boolean) || [];
  if (sentences.length >= 2) {
    const midpoint = Math.ceil(sentences.length / 2);
    return [sentences.slice(0, midpoint).join(""), sentences.slice(midpoint).join("")];
  }

  const commaPositions = [...String(text).matchAll(/、/g)].map((match) => match.index + 1);
  if (commaPositions.length) {
    const center = text.length / 2;
    const cut = commaPositions.reduce((best, value) => (
      Math.abs(value - center) < Math.abs(best - center) ? value : best
    ), commaPositions[0]);
    return [text.slice(0, cut).trim(), text.slice(cut).trim()].filter(Boolean);
  }

  if (text.length >= 80) {
    const cut = Math.floor(text.length / 2);
    return [text.slice(0, cut).trim(), text.slice(cut).trim()].filter(Boolean);
  }
  return [text];
}

function answerUnits(text, minimumCount) {
  const units = String(text || "").split(/\n\s*\n/).map((part) => part.trim()).filter(Boolean);

  while (units.length < minimumCount) {
    let candidateIndex = -1;
    let candidateParts = null;

    units.forEach((unit, index) => {
      const parts = splitAtSentenceBoundary(unit);
      if (parts.length < 2) return;
      if (candidateIndex < 0 || unit.length > units[candidateIndex].length) {
        candidateIndex = index;
        candidateParts = parts;
      }
    });

    if (candidateIndex < 0) break;
    units.splice(candidateIndex, 1, ...candidateParts);
  }
  return units;
}

function allocateUnits(units, sections) {
  const remaining = [...units];
  let remainingWeight = sections.reduce((total, section) => total + (section[2] || 1), 0);

  return sections.map((section, index) => {
    if (index === sections.length - 1) return remaining.splice(0);

    const weight = section[2] || 1;
    const sectionsAfter = sections.length - index - 1;
    const proportional = Math.round(remaining.length * weight / remainingWeight);
    const count = Math.max(1, Math.min(proportional, remaining.length - sectionsAfter));
    remainingWeight -= weight;
    return remaining.splice(0, count);
  });
}

function StructuredAnswer({ row }) {
  const sections = ANSWER_STRUCTURES[String(row.id)] || [
    ["問題文に沿った答案", ["目的", "変化", "影響", "計測", "経営対応"], 1],
  ];
  const units = answerUnits(row.合格レベル答案, sections.length);
  const groups = allocateUnits(units, sections);

  return (
    <div className={styles.text}>
      {sections.map(([title, framework], index) => (
        <div key={`${row.id}-${title}`}>
          <h3>{title}</h3>
          <p><strong>【フレームワーク：{framework.join("・")}】</strong></p>
          {groups[index].map((paragraph, paragraphIndex) => (
            <p key={`${row.id}-${index}-${paragraphIndex}`}>{paragraph}</p>
          ))}
        </div>
      ))}
    </div>
  );
}

export default function ShokenAnswerView({ row }) {
  return (
    <div className={styles.answerView}>
      <section className={styles.section}>
        <h2>① フレームワークを用いた論点整理</h2>
        <RichText text={normalizeFramework(row.フレームワークを用いた論点整理)} />
      </section>
      <section className={styles.section}>
        <div className={styles.answerHeading}>
          <h2>② 合格レベル答案</h2>
          <span>問題文の指定順序を優先し、フレームワークとの対応を表示</span>
        </div>
        <StructuredAnswer row={row} />
      </section>
    </div>
  );
}
