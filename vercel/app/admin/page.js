"use client";

const files = [
  {
    type: "PDF / 日本語",
    title: "ICA2026 日本語版 論文",
    filename: "ICA2026_Japanese_refined_v5.pdf",
    href: "https://drive.google.com/file/d/1CFQs366N7VsVIRC4yZtyjc33uC2xDeND/view?usp=drivesdk",
  },
  {
    type: "PowerPoint / 日本語",
    title: "ICA2026 日本語版 発表資料",
    filename: "0818 日本語版完成.pptx",
    href: "https://docs.google.com/presentation/d/1w8GFarXMPh0IHCeF8DTmYtTwqGGBXqw6/edit?usp=drivesdk&ouid=111821978937673879276&rtpof=true&sd=true",
  },
  {
    type: "PDF / English",
    title: "ICA2026 English Paper",
    filename: "ICA2026_English_refined_v5.pdf",
    href: "https://drive.google.com/file/d/1V47cxZImeJ40DJYz6n-pSfMuC-PSnQ1R/view?usp=drivesdk",
  },
];

export default function AdminPage() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <span className="eyebrow">ADMIN MATERIALS</span>
          <h1>アクチュアリー2次試験 <b>生保1</b></h1>
        </div>
      </header>

      <nav className="main-nav" aria-label="管理者用メニュー">
        <button type="button" onClick={() => { window.location.href = "/"; }}>← 学習画面に戻る</button>
      </nav>

      <main>
        <div className="page-heading">
          <span>ADMIN DOWNLOADS</span>
          <h2>管理者用</h2>
          <p>ICA2026関連ファイルをGoogle Driveから開いてダウンロードできます。</p>
        </div>

        <div className="textbook-grid">
          {files.map((file) => (
            <article className="textbook" key={file.href}>
              <span>{file.type}</span>
              <h3>{file.title}</h3>
              <p style={{ margin: "0 0 18px", color: "#687771", fontSize: "12px", overflowWrap: "anywhere" }}>
                {file.filename}
              </p>
              <a href={file.href} target="_blank" rel="noreferrer">Google Driveで開く / ダウンロード ↗</a>
            </article>
          ))}
        </div>
      </main>

      <footer>アクチュアリー2次試験 生保1 管理者用資料</footer>
    </div>
  );
}
