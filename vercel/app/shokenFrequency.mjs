export const FREQUENCY_PERIOD = "2018–2025年度";
export const FREQUENCY_TOTAL_YEARS = 8;

const topic = (label, years, terms) => ({
  label,
  years,
  terms: [...new Set(terms)].sort((left, right) => right.length - left.length),
  level: years.length >= 6 ? "must" : "frequent",
});

// 日本アクチュアリー会の2018～2025年度「生保1」問題・模範解答を年度横断で検索し、
// 4年度以上で確認できた論点だけを表示対象とする。
export const FREQUENCY_TOPICS = [
  topic("契約者保護・公平性", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["契約者間の公平性", "新旧契約間の公平性", "社会的公平性", "世代間公平", "契約者保護", "公平性"]),
  topic("収益性・将来収支", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["商品毎収益検証", "将来収支", "利益現価", "将来利益", "収益検証", "収益性"]),
  topic("感応度分析・ストレステスト", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["リバースストレス", "ストレステスト", "複合ストレス", "複合シナリオ", "感応度分析", "感応度"]),
  topic("逆選択・モラルリスク", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["モラルリスク", "情報非対称", "リスク濃縮", "選択効果", "逆選択"]),
  topic("ALM・流動性", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["資産デュレーション", "流動性バッファー", "再投資リスク", "デュレーション", "流動性", "ALM"]),
  topic("販売上限・リスク限定", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["保険金額上限", "販売停止基準", "販売量上限", "加入年齢", "給付限度", "販売上限", "待期間"]),
  topic("予定事業費・費用管理", [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], ["事業費インフレ", "固定費回収", "予定事業費", "実際事業費", "広告費"]),
  topic("基礎データ・安全割増", [2018, 2019, 2021, 2022, 2023, 2024, 2025], ["公的データ", "公共データ", "外部データ", "自社データ", "データ不足", "安全割増"]),
  topic("事後モニタリング・見直し", [2018, 2019, 2022, 2023, 2024, 2025], ["事後モニタリング", "モニタリング", "計画対実績", "発売後", "PDCA"]),
];

export function frequentTopicsFor(text) {
  const source = String(text || "");
  return FREQUENCY_TOPICS
    .filter((item) => item.terms.some((term) => source.includes(term)))
    .sort((left, right) => right.years.length - left.years.length || left.label.localeCompare(right.label, "ja"));
}

export function primaryFrequencyFor(text) {
  const matches = frequentTopicsFor(text);
  if (!matches.length) return null;
  return { ...matches[0], matches };
}

export function frequentTermsFor(text, topics) {
  const source = String(text || "");
  return [...new Set((topics || []).flatMap((item) => item.terms))]
    .filter((term) => source.includes(term))
    .sort((left, right) => right.length - left.length);
}
