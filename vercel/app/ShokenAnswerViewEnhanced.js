import styles from "./ShokenAnswerView.module.css";

const ORDER = ["目的", "商品設計", "基礎率設定", "収益性", "リスク対応"];
const KEYS = {
  目的: ["目的", "意義", "ニーズ", "契約者", "公平", "理解", "保障"],
  商品設計: ["商品", "設計", "給付", "保障", "保険期間", "払込", "返戻", "年金", "販売", "チャネル", "査定"],
  基礎率設定: ["基礎率", "予定", "死亡率", "発生率", "解約率", "利率", "事業費", "データ", "安全割増", "標準利率"],
  収益性: ["収益", "利益", "損益", "収支", "検証", "キャッシュフロー", "責任準備金", "資本", "費差", "利差", "価格"],
  リスク対応: ["リスク", "管理", "ストレス", "感応度", "モニタリング", "改善", "再保険", "ヘッジ", "ALM", "販売上限", "流動性"],
};
const FRAMEWORK_GUIDE = {
  目的: "誰のどのニーズに応え、何を実現するか。",
  商品設計: "給付・期間・払方・返戻金・販売方法をどう組み合わせるか。",
  基礎率設定: "死亡・発生・利率・事業費・解約をどう置くか。",
  収益性: "十分性・公平性・収益性・標準責任準備金をどう確認するか。",
  リスク対応: "モニタリング、ストレス、ALM、再保険、改善へどうつなぐか。",
};

const STRUCTURES = {
  "1": { essayStart: 2, sections: [
    ["① 解約返戻金額と死亡保険金額に起因する契約者間の公平性", ["目的"], 1],
    ["① 低・無解約返戻金型商品における契約者理解", ["目的"], 1],
    ["② 死亡者持分を生存者へ移転する商品設計", ["目的", "商品設計"], 2],
    ["② 予定死亡率その他の計算基礎率", ["基礎率設定"], 2],
    ["② 解約益と将来利益の関係・収益検証", ["収益性"], 2],
    ["② 販売方針と事後モニタリング", ["リスク対応"], 1],
  ]},
  "2": { essayStart: 1, sections: [
    ["① 保険料率の細分化における公平性", ["目的"], 1],
    ["② ライフスタイル指標を料率区分に用いる要件", ["基礎率設定"], 2],
    ["② 商品設計上の留意点", ["商品設計"], 1],
    ["② 価格設定と危険選択", ["基礎率設定", "収益性"], 2],
    ["② 契約者説明・プライバシー・社会的容認性", ["目的", "リスク対応"], 1],
    ["② 収益検証と販売後モニタリング", ["収益性", "リスク対応"], 1],
  ]},
  "3": { essayStart: 2, sections: [
    ["① 第三分野の予定発生率と死亡保険の予定死亡率の相違", ["基礎率設定"], 1],
    ["① 社会保険制度に連動する場合の困難性", ["リスク対応"], 1],
    ["② 介護終身年金の商品設計", ["目的", "商品設計"], 2],
    ["② 予定発生率の設定", ["基礎率設定"], 2],
    ["② その他の計算基礎率と収益検証", ["基礎率設定", "収益性"], 1],
    ["② 保険収支の不確実性を制御する方策", ["商品設計", "リスク対応"], 2],
    ["② 販売後のモニタリングと改善", ["リスク対応"], 1],
  ]},
  "4": { essayStart: 0, sections: [
    ["選択① 国内金利の上昇", ["収益性", "リスク対応"], 2],
    ["選択② 死亡率の低下", ["基礎率設定", "収益性"], 2],
    ["選択③ 顧客による余命推定技術の普及", ["商品設計", "リスク対応"], 2],
  ]},
  "5": { essayStart: 2, sections: [
    ["①（ア）危険選択の目的", ["目的"], 1],
    ["①（イ）医的査定と環境査定", ["基礎率設定"], 1],
    ["② インターネットチャネルにおける危険選択の特徴", ["目的", "商品設計"], 2],
    ["② 商品設計上の留意点", ["商品設計"], 1],
    ["② 価格設定上の留意点", ["基礎率設定", "収益性"], 1],
    ["② 営業職員チャネル・他社商品との関係", ["商品設計", "収益性"], 1],
    ["② リスク管理と事後モニタリング", ["リスク対応"], 1],
  ]},
  "6": { essayStart: 2, sections: [
    ["① 商品毎収益検証の目的", ["目的"], 1],
    ["① 商品毎収益検証を実施する三つの手順", ["収益性"], 1],
    ["② A．商品特性および解約率の特性", ["商品設計", "基礎率設定"], 2],
    ["② B．解約率シナリオと他シナリオの連動性", ["基礎率設定", "収益性"], 2],
    ["② C．感応度分析・ストレステスト", ["収益性", "リスク対応"], 1],
    ["② D．検証結果の経営への活用", ["リスク対応"], 2],
  ]},
  "7": { essayStart: 2, sections: [
    ["① 自社データを用いる場合のメリット・デメリット", ["基礎率設定"], 1],
    ["① 公共データを用いる場合のメリット・デメリット", ["基礎率設定"], 1],
    ["② 認知症保険の商品設計", ["目的", "商品設計"], 2],
    ["② 計算基礎率の設定", ["基礎率設定"], 2],
    ["② 商品導入に伴うリスク", ["収益性", "リスク対応"], 1],
    ["② リスク管理・事後モニタリング", ["リスク対応"], 2],
  ]},
  "8": { essayStart: 1, sections: [
    ["① 個人年金保険の代表的な四つの年金支払種類", ["目的"], 1],
    ["② 安定的な商品供給", ["目的", "収益性"], 1],
    ["② 将来の金利上昇に対する機動的な対応", ["商品設計", "リスク対応"], 2],
    ["② 長寿リスクに対する顧客ニーズ", ["目的", "商品設計"], 1],
    ["② 競合他社に対する優位性と商品設計上の工夫", ["商品設計", "収益性"], 2],
    ["② 基礎率・ALM・販売後管理", ["基礎率設定", "リスク対応"], 2],
  ]},
  "9": { essayStart: 1, sections: [
    ["（ア）事後モニタリングと改善アクションの目的・必要性", ["目的"], 1],
    ["（イ）A．一件当たり収益性の低下要因", ["収益性"], 2],
    ["（イ）A．一件当たり収益性を改善するアクションと留意点", ["商品設計", "リスク対応"], 2],
    ["（イ）B．販売件数の変化要因と改善アクション", ["収益性", "リスク対応"], 2],
    ["（イ）総合判断と再モニタリング", ["リスク対応"], 1],
  ]},
  "10": { essayStart: 1, sections: [
    ["（ア）米ドル建一時払終身保険の標準利率", ["基礎率設定"], 1],
    ["（イ）標準利率を踏まえた予定利率設定", ["基礎率設定", "収益性"], 2],
    ["（イ）商品設計と競合後発商品への対応", ["商品設計", "収益性"], 2],
    ["（イ）BBB格事業債の信用リスク", ["リスク対応"], 1],
    ["（イ）信用・金利・為替・流動性リスクの管理", ["リスク対応"], 2],
    ["（イ）収益検証と販売後管理", ["収益性", "リスク対応"], 1],
  ]},
  "11": { essayStart: 3, sections: [
    ["（ア）予定利率設定の一般的な留意点", ["基礎率設定"], 1],
    ["（イ）① 市中金利上昇が収益性に与える影響", ["収益性"], 1],
    ["（イ）② 物価上昇が収益性に与える影響", ["収益性"], 1],
    ["（ウ）保険料の十分性", ["目的", "収益性"], 2],
    ["（ウ）保険料の公平性", ["目的", "収益性"], 1],
    ["（ウ）保険料の収益性・改定後の管理", ["収益性", "リスク対応"], 2],
  ]},
  "12": { essayStart: 1, sections: [
    ["（ア）一商品に複数給付を持たせる利点", ["商品設計"], 1],
    ["（イ）販売政策", ["目的", "商品設計"], 1],
    ["（イ）三商品の給付設計", ["商品設計"], 2],
    ["（イ）各商品の基礎率設定", ["基礎率設定"], 2],
    ["（イ）危険選択への影響", ["商品設計", "基礎率設定"], 1],
    ["（イ）事後モニタリング", ["リスク対応"], 1],
    ["（イ）販売後の収益変動と対応", ["収益性", "リスク対応"], 2],
  ]},
  "13": { essayStart: 2, sections: [
    ["（ア）予定事業費の十分性・普遍性・公平性", ["基礎率設定"], 1],
    ["（イ）件数比例・責任準備金比例と費用主義・効用主義", ["基礎率設定"], 1],
    ["（ウ）開発目的", ["目的"], 1],
    ["（ウ）保険給付等の詳細設計", ["商品設計"], 1],
    ["（ウ）販売政策", ["商品設計", "収益性"], 1],
    ["（ウ）実際事業費と予定事業費体系", ["基礎率設定", "収益性"], 2],
    ["（ウ）本商品の収益性と事後管理", ["収益性", "リスク対応"], 2],
  ]},
  "14": { essayStart: 4, sections: [
    ["（ア）① 商品設計による収支変動の制御", ["商品設計"], 1],
    ["（ア）② 契約群団のコントロール", ["リスク対応"], 1],
    ["（ア）③ 商品ポートフォリオ", ["リスク対応"], 1],
    ["（ア）④ 事後モニタリングと改善アクション", ["リスク対応"], 1],
    ["（イ）環境変化が商品に及ぼす影響", ["収益性", "リスク対応"], 2],
    ["（イ）事後モニタリングの内容と目的", ["収益性", "リスク対応"], 2],
    ["（イ）商品・料率・販売政策その他の対応策", ["商品設計", "リスク対応"], 2],
  ]},
  "15": { essayStart: 2, sections: [
    ["（ア）年金開始前・開始後にトンチン性を持たせる給付例", ["商品設計"], 1],
    ["（イ）トンチン性商品の長寿リスク", ["収益性"], 1],
    ["（ウ）商品設計と契約取扱い", ["目的", "商品設計"], 2],
    ["（ウ）計算基礎率の設定", ["基礎率設定"], 2],
    ["（ウ）販売方針", ["商品設計", "収益性"], 1],
    ["（ウ）収益の性質と事後モニタリング", ["収益性", "リスク対応"], 2],
    ["（ウ）リスク顕在時の改善アクション", ["リスク対応"], 1],
  ]},
  "16": { essayStart: 1, sections: [
    ["（ア）第三分野の予定発生率設定が困難な三つの理由", ["基礎率設定"], 1],
    ["（イ）商品A・Bの収益性の特徴", ["商品設計", "収益性"], 2],
    ["（イ）競争環境の変化が与える影響", ["収益性"], 1],
    ["（イ）収益性検証の目的", ["目的", "収益性"], 1],
    ["（イ）収益性検証の実施手順", ["収益性"], 2],
    ["（イ）検証結果の活用方法", ["リスク対応"], 2],
    ["（イ）事後モニタリングと再検証", ["リスク対応"], 1],
  ]},
};

const sentences = (text) => String(text || "").replace(/\r/g, "")
  .split(/(?<=[。！？])|\n+/).map((x) => x.trim()).filter((x) => x.length >= 10);

const short = (text, n = 112) => {
  const value = String(text || "").replace(/\s+/g, " ").trim();
  return value.length <= n ? value : `${value.slice(0, n).replace(/[、。\s]+$/, "")}…`;
};

function splitAtSentenceBoundary(text) {
  const list = sentences(text);
  if (list.length >= 2) {
    const midpoint = Math.ceil(list.length / 2);
    return [list.slice(0, midpoint).join(""), list.slice(midpoint).join("")];
  }
  if (String(text).length >= 100) {
    const cut = Math.floor(String(text).length / 2);
    return [String(text).slice(0, cut).trim(), String(text).slice(cut).trim()].filter(Boolean);
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

function allocateEssayUnits(units, sections, essayStart) {
  const remaining = [...units];
  const groups = [];
  for (let index = 0; index < essayStart; index += 1) {
    const requested = sections[index][2] || 1;
    const leave = Math.max(0, sections.length - index - 1);
    const count = Math.max(1, Math.min(requested, remaining.length - leave));
    groups.push(remaining.splice(0, count));
  }
  const essaySections = sections.slice(essayStart);
  let remainingWeight = essaySections.reduce((total, section) => total + (section[2] || 1), 0);
  essaySections.forEach((section, essayIndex) => {
    if (essayIndex === essaySections.length - 1) {
      groups.push(remaining.splice(0));
      return;
    }
    const weight = section[2] || 1;
    const sectionsAfter = essaySections.length - essayIndex - 1;
    const proportional = Math.round(remaining.length * weight / remainingWeight);
    const count = Math.max(1, Math.min(proportional, remaining.length - sectionsAfter));
    groups.push(remaining.splice(0, count));
    remainingWeight -= weight;
  });
  return groups;
}

function focusCategories(row) {
  const source = `${row.問題文 || ""}\n${row.合格レベル答案 || ""}`;
  return ORDER.map((name) => ({
    name,
    score: (KEYS[name] || []).reduce((sum, key) => sum + (source.includes(key) ? 1 : 0), 0),
  }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)
    .map((item) => item.name);
}

function EssayFramework({ row }) {
  const focus = focusCategories(row);
  return <div className={styles.text}>
    <h3>論文式の思考フレーム</h3>
    <p><strong>{ORDER.join(" → ")}</strong></p>
    {focus.length > 0 && <p><strong>この問題の主軸：</strong>{focus.join("・")}</p>}
    {ORDER.map((name) => <p key={name}><strong>{name}：</strong>{FRAMEWORK_GUIDE[name]}</p>)}
    <p>問題文がA・B・C・D等の順序を指定している場合は、その順序を崩さず、各パートの中で上記の観点を用いて論点を広げる。</p>
  </div>;
}

function threePoints(parts, title) {
  const result = [];
  for (const text of sentences(parts.join("\n"))) {
    const value = short(text, 118);
    if (!result.includes(value)) result.push(value);
    if (result.length === 3) break;
  }
  const fallback = [
    `${title}について、問題文固有の前提と一般原則を結び付ける。`,
    "契約者・商品収支・会社全体への影響を分けて示す。",
    "対応策の効果だけでなく、限界・副作用・事後検証まで述べる。",
  ];
  for (const value of fallback) {
    if (result.length === 3) break;
    if (!result.includes(value)) result.push(value);
  }
  return result.slice(0, 3);
}

function StructuredAnswer({ row }) {
  const config = STRUCTURES[String(row.id)] || {
    essayStart: 0,
    sections: [["論文式答案", ORDER, 1]],
  };
  const shortUnits = config.sections.slice(0, config.essayStart)
    .reduce((total, section) => total + (section[2] || 1), 0);
  const minimumUnits = shortUnits + Math.max(1, config.sections.length - config.essayStart) * 2;
  const units = answerUnits(row.合格レベル答案, minimumUnits);
  const groups = allocateEssayUnits(units, config.sections, config.essayStart);

  return <div className={styles.text}>
    {config.sections.map(([title, framework], index) => {
      const isEssay = index >= config.essayStart;
      const body = groups[index] || [];
      return <div key={`${row.id}-${title}`}>
        {index === config.essayStart && <EssayFramework row={row} />}
        <h3>{title}</h3>
        {isEssay && <p><strong>【フレームワーク：{framework.join("・")}】</strong></p>}
        {isEssay && threePoints(body, title).map((point, pointIndex) => (
          <p className={styles.bullet} key={`${row.id}-${index}-point-${pointIndex}`}>
            <strong>論点{pointIndex + 1}</strong>　{point}
          </p>
        ))}
        {body.map((paragraph, paragraphIndex) => (
          <p key={`${row.id}-${index}-body-${paragraphIndex}`}>{paragraph}</p>
        ))}
      </div>;
    })}
  </div>;
}

export default function ShokenAnswerViewEnhanced({ row }) {
  return <div className={styles.answerView}>
    <section className={styles.section}>
      <div className={styles.answerHeading}>
        <h2>合格レベル答案</h2>
        <span>前半は模範解答、最後の高配点論文式のみフレームワークで展開</span>
      </div>
      <StructuredAnswer row={row} />
    </section>
  </div>;
}
