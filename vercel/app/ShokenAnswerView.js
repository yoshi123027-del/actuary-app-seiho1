import styles from "./ShokenAnswerView.module.css";

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

export default function ShokenAnswerView({ row }) {
  return (
    <div className={styles.answerView}>
      <section className={styles.section}>
        <h2>論文式の思考フレーム</h2>
        <RichText text={row.フレームワークを用いた論点整理} />
        <p className={styles.text}>1分程度で答案の骨格と加点論点を整理するメモ。</p>
      </section>
      <section className={styles.section}>
        <div className={styles.answerHeading}>
          <h2>合格レベル答案</h2>
          <span>公式解答例を土台に整理</span>
        </div>
        <RichText text={row.合格レベル答案} />
      </section>
    </div>
  );
}
