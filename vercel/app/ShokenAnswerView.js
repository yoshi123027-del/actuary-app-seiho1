import styles from "./ShokenAnswerView.module.css";

function blocks(text) {
  return String(text || "")
    .replace(/\r/g, "")
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function RichText({ text }) {
  const lines = String(text || "").replace(/\r/g, "").split("\n");
  return (
    <div className={styles.text}>
      {lines.map((rawLine, index) => {
        const line = rawLine.trim();
        if (!line) return null;
        if (/^(【.+】|■.+|[0-9０-９]+[．.]|[A-FＡ-Ｆ][．.]|[①-⑩]|〇)/.test(line)) {
          return <h3 key={index}>{line}</h3>;
        }
        if (/^[-・]/.test(line)) {
          return <p className={styles.bullet} key={index}>{line.replace(/^[-・]\s*/, "")}</p>;
        }
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

function Framework({ text }) {
  return (
    <div className={styles.frameworkBox}>
      <h3>論文式の思考フレーム</h3>
      <p className={styles.frameworkFlow}><strong>目的 → 商品設計 → 基礎率設定 → 収益性 → リスク対応</strong></p>
      <RichText text={text} />
      <p className={styles.frameworkNote}>1分程度で答案の骨格と加点論点を整理するメモ。</p>
    </div>
  );
}

export default function ShokenAnswerView({ row = {} }) {
  const answerBlocks = blocks(row.合格レベル答案);
  const shortAnswer = answerBlocks.length > 1 ? answerBlocks[0] : "";
  const essayAnswer = answerBlocks.length > 1 ? answerBlocks.slice(1).join("\n\n") : answerBlocks.join("\n\n");

  return (
    <div className={styles.answerView}>
      <section className={styles.section}>
        <div className={styles.answerHeading}><h2>合格レベル答案</h2></div>
        {shortAnswer && <div className={styles.shortAnswer}><RichText text={shortAnswer} /></div>}
        <Framework text={row.フレームワークを用いた論点整理} />
        <div className={styles.essayHeading}><h3>論文式答案</h3></div>
        <RichText text={essayAnswer} />
      </section>
    </div>
  );
}
