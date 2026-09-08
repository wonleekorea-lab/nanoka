#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lives.json を検める。日本語の書き方が崩れていたら落とす。

書き方の規則（追記するときもこれに合わせる）:
  1. 一文で終える。読点は多くて2つ。
  2. 故人は過去形、存命の人は現在形。混ぜない。
  3. 体言止めにしない。「〜した」「〜する」で締める。
  4. 伝聞は「という」「と伝わる」で締め、断定しない。
  5. 主語は書かない（誰の話かは名前で分かる）。
  6. 数字は算用数字。単位は日本語。
  7. 直訳調（「〜することを自らに課した」等）を使わない。
  8. 肩書きは2〜10字の日本語。
"""
import json, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "lives.json")

NG = ["ことを自らに課した", "することを心がけた", "を行った", "であった。",
      "ということをした", "を実施した"]

def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    people = data.get("people")
    if not isinstance(people, list) or len(people) < 20:
        print("people が足りない"); return 1

    err = []
    seen = {}
    for i, p in enumerate(people):
        who, what, did = p.get("who", ""), p.get("what", ""), p.get("did", "")
        at = "%d:%s" % (i, who or "(名前なし)")

        if not who or not what or not did:
            err.append((at, "欠けている項目がある")); continue
        if who in seen:
            err.append((at, "名前が重複している（%d行目と）" % seen[who]))
        seen[who] = i

        if who != who.upper():
            err.append((at, "名前は英大文字で書く"))
        if not (2 <= len(what) <= 10):
            err.append((at, "肩書きは2〜10字"))
        if not did.endswith("。"):
            err.append((at, "句点で終えていない"))
        if "。" in did[:-1]:
            err.append((at, "二文になっている"))
        if did.count("、") > 2:
            err.append((at, "読点が多い"))
        if not (12 <= len(did) <= 60):
            err.append((at, "本文は12〜60字（いまは%d字）" % len(did)))
        if re.search(r"[A-Za-z]", did):
            err.append((at, "本文に英字が混じっている"))
        for ng in NG:
            if ng in did:
                err.append((at, "硬い言い回し「%s」" % ng))

    if err:
        for at, why in err:
            print("NG %s: %s" % (at, why))
        print("---")
        print("%d件の問題。%d人。" % (len(err), len(people)))
        return 1

    print("OK %d人。重複なし、書き方も揃っている。" % len(people))
    return 0

if __name__ == "__main__":
    sys.exit(main())
