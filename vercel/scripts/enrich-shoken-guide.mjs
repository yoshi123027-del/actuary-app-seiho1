import fs from "node:fs";

const pagePath = new URL("../app/page.js", import.meta.url);
let source = fs.readFileSync(pagePath, "utf8");
const original = source;

const configImport = 'import { appConfig } from "./config";';
const templateImport = 'import ShokenProductTemplate from "./ShokenProductTemplate";';

if (!source.includes(templateImport)) {
  if (!source.includes(configImport)) {
    throw new Error("page.js のimport挿入位置を確認できませんでした。");
  }
  source = source.replace(configImport, `${configImport}\n${templateImport}`);
}

const guideAnchor = "          <p>契約者保護、健全性、公平性、収益性、実務負荷、説明責任などの視点から、問題に応じた論点を組み立てます。</p>";
const templateElement = "          <ShokenProductTemplate />";

if (!source.includes(templateElement)) {
  if (!source.includes(guideAnchor)) {
    throw new Error("所見の習得方法への挿入位置を確認できませんでした。");
  }
  source = source.replace(guideAnchor, `${guideAnchor}\n${templateElement}`);
}

if (source !== original) {
  fs.writeFileSync(pagePath, source, "utf8");
  console.log("所見ガイドへ商品開発・商品設計の答案フレームを追加しました。");
} else {
  console.log("商品開発・商品設計の答案フレームは追加済みです。");
}
