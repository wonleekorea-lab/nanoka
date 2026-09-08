#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lives.json に人物を書き足す。Claude に下書きさせ、機械で検めてから足す。

出来上がりは PR に載せる。そのまま本番へは入れない（事実の確認は人がやる）。
使い方: ANTHROPIC_API_KEY を渡して  python3 scripts/extend_lives.py --count 12
"""
import argparse, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "lives.json")

RULES = """日本語の書き方（全件この規則で揃えてある。必ず合わせること）:
1. 一文で終える。読点は多くて2つ。
2. 故人は過去形、存命の人は現在形。混ぜない。
3. 体言止めにしない。「〜した」「〜する」で締める。
4. 伝聞や逸話の域を出ないものは「という」「と伝わる」で締め、断定しない。
5. 主語は書かない（誰の話かは名前で分かる）。
6. 数字は算用数字。単位は日本語。
7. 直訳調（「〜することを自らに課した」「〜を行った」等）を使わない。
8. 本文は12〜60字。肩書きは2〜10字の日本語。"""


def build_prompt(existing, count):
    return (
        "習慣アプリに載せる「実在の人物が実際に続けていた日課」の項目を書いてください。\n"
        "毎日か、それに近い頻度で繰り返していた具体的な行いだけを採ってください。\n"
        "業績・名言・性格の話は要りません。行いだけです。\n\n"
        "確かな記録や本人の発言が残っているものだけにしてください。\n"
        "怪しいものは書かないでください。数を埋めるより、確かさを優先します。\n\n"
        + RULES + "\n\n"
        "分野が偏らないようにしてください（作家・科学者・画家・音楽家・"
        "競技者・経営者・思想家・建築家・料理人・映画監督など）。\n"
        "地域も偏らせないでください。\n\n"
        "すでに入っている人（重複させないこと）:\n" + "、".join(existing) + "\n\n"
        "次の形のJSON配列だけを返してください。説明は要りません。\n"
        '[{"who":"NAME IN CAPITALS","what":"肩書き","did":"本文。"}]\n'
        "%d件。" % count
    )


def parse_json(text):
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    body = m.group(1) if m else text
    a, b = body.find("["), body.rfind("]")
    if a < 0 or b <= a:
        raise ValueError("JSONが見つからない")
    return json.loads(body[a:b + 1])


def acceptable(p, existing):
    who, what, did = p.get("who", ""), p.get("what", ""), p.get("did", "")
    if not who or not what or not did:
        return False
    if who in existing or who != who.upper():
        return False
    if not (2 <= len(what) <= 10):
        return False
    if not did.endswith("。") or "。" in did[:-1]:
        return False
    if did.count("、") > 2 or not (12 <= len(did) <= 60):
        return False
    if re.search(r"[A-Za-z]", did):
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=12)
    args = ap.parse_args()

    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    people = data["people"]
    existing = [p["who"] for p in people]

    import anthropic
    client = anthropic.Anthropic()
    res = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        messages=[{"role": "user", "content": build_prompt(existing, args.count)}],
    )
    if res.stop_reason == "refusal":
        print("断られた。何も足さない。")
        return 0
    text = "".join(b.text for b in res.content if b.type == "text")

    got = parse_json(text)
    seen = set(existing)
    added = []
    for p in got:
        if acceptable(p, seen):
            seen.add(p["who"])
            added.append({"who": p["who"], "what": p["what"], "did": p["did"]})

    if not added:
        print("通ったものが無い。何も足さない。")
        return 0

    data["people"] = people + added
    data["updated"] = datetime.date.today().isoformat()
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    print("%d件のうち%d件を足した:" % (len(got), len(added)))
    for p in added:
        print("  " + p["who"] + " / " + p["did"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
