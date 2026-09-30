"use client";

const files = [
  {
    type: "PDF / 日本語",
    title: "ICA2026 日本語版 論文",
    filename: "★ICA2026_20260930_ja.pdf",
    href: "/admin-files/%E2%98%85ICA2026_20260930_ja.pdf",
  },
  {
    type: "PDF / English",
    title: "ICA2026 English Paper",
    filename: "★ICA2026_20260930.pdf",
    href: "/admin-files/%E2%98%85ICA2026_20260930.pdf",
  },
  {
    type: "PDF / English",
    title: "ICA2026 English Presentation",
    filename: "0930_English_fin.pdf",
    href: "/admin-files/0930_English_fin.pdf",
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
          <p>ICA2026関連ファイルをこのサイトから直接ダウンロードできます。</p>
        </div>

        <div className="textbook-grid">
          {files.map((file) => (
            <article className="textbook" key={file.href}>
              <span>{file.type}</span>
              <h3>{file.title}</h3>
              <p style={{ margin: "0 0 18px", color: "#687771", fontSize: "12px", overflowWrap: "anywhere" }}>
                {file.filename}
              </p>
              <a href={file.href} download={file.filename}>ダウンロード ↓</a>
            </article>
          ))}
        </div>
      </main>

      <footer>アクチュアリー2次試験 生保1 管理者用資料</footer>
    </div>
  );
}
