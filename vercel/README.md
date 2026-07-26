# Vercel版（生保1）

既存のStreamlit版を残したまま、静的配信できるNext.js版を `vercel/` に追加しています。

## ローカル確認

```bash
cd vercel
npm install
npm run dev
```

## Vercel設定

- Framework Preset: Next.js
- Root Directory: `vercel`
- Build Command: `npm run build`
- Output Directory: `out`

GitHubの `main` ブランチへ反映されると、同じVercel URLへ自動デプロイできます。

学習履歴・自己評価・復習フラグはブラウザのlocalStorageに保存されます。
