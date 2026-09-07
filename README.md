# 七日の灯

習慣を「1分でできる行動 ＋ すでにやっている行動へのくっつけ先」に割り、
7日連続でともし切ると浄化して記録に移す。同時に持てるのは3つまで。

画面は横に三面。中央が今日で、三行あるだけ。行にふれると灯り、7本目で浄化する。
押し続ける（または今日もう灯した行にふれる）と、その行を直せる。
左が登録で、投げる箱がひとつだけ。右が記録。下の点を押しても移れる。
色は和紙と、その向こうから来る光。夜は灯を受けた紙になる。
周辺の言葉は小文字の英語。日本語は自分が書いた習慣と、灯した瞬間の「よし」だけ。

Sokuganと同じ形の standalone PWA。iPhoneのSafariで開いて「ホーム画面に追加」すると、
Safariのバーもタブもない全画面アプリとして起動する。

## 構成

```
index.html      アプリ本体（1ファイル。フレームワークなし）
manifest.json   display:standalone / アイコン / テーマ色
sw.js           ネット優先・キャッシュ退避。圏外でも開ける
icons/          180(apple-touch) / 192 / 512
```

## 公開（GitHub Pages）

```bash
gh repo create nanoka --public --source="/Users/wota/Documents/ChatGPT/AI Engineering/nanoka" --push
```

そのあとリポジトリの Settings → Pages で Source を `main` / `/ (root)` にする。
数分で `https://<account>.github.io/nanoka/` が生きる。

更新は push するだけ。`sw.js` の `CACHE` の値（`nanoka-v1`）を変えると、
古いキャッシュを捨てて確実に新しい版が入る。

## ホーム画面に置く

1. iPhoneのSafariで公開URLを開く
2. 共有ボタン → 「ホーム画面に追加」
3. アイコンから起動。以後は全画面

## 記録の保存先

この端末のブラウザ（localStorage）だけ。サーバーには何も送らない。
端末を移すときは 記録の面 → settings → copy out で文字列を控え、移す先で bring in。

## クエストの下書き（任意）

記録の面 → settings に Anthropic の APIキーを入れると、投げたあとに Claude が
「1分でやること ＋ くっつけ先」を3案出す。ふれるとその行が置きかわる。無視してもよい。
使うモデルは `claude-opus-5`。

- キーはこの端末のブラウザにだけ保存される。リポジトリにも、他のサーバーにも入らない
- 送信先は `api.anthropic.com` のみ（`anthropic-dangerous-direct-browser-access` を使った直接呼び出し）
- 1回の下書きで数円。空のままでも、手書きでクエストは作れる

公開リポジトリに置くのはHTMLだけで、キーはコードに含まれない。
ただしブラウザに保存する以上、その端末を他人が触れる状態にはしないこと。
