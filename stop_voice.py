#!/usr/bin/env python3
"""Claude Code の Stop フック。その回の返事と使った道具を見て、作り置きの声から1本選んで鳴らす。"""
import json, pathlib, random, re, subprocess, sys

SOUNDS = pathlib.Path(__file__).parent / "sounds"


def last_turn(transcript_path):
    """最後の人の指示より後の「Claudeの文章」「使った道具と結果」「人の指示」を返す"""
    texts, tools, results, prompt = [], [], {}, ""
    for line in reversed(pathlib.Path(transcript_path).read_text().splitlines()):
        d = json.loads(line)
        content = (d.get("message") or {}).get("content")
        if d.get("type") == "user":
            raw = content if isinstance(content, str) else "".join(
                b.get("text", "") for b in content or [] if b.get("type") == "text")
            said = re.sub(r"<system-reminder>.*?</system-reminder>", "", raw, flags=re.S).strip()
            if said and not d.get("isMeta"):
                prompt = said
                break
            for b in content or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = json.dumps(b.get("content"), ensure_ascii=False)
        elif d.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if b.get("type") == "text":
                    texts.append(b["text"])
                elif b.get("type") == "tool_use":
                    tools.append(b)
    for t in tools:
        t["result"] = results.get(t.get("id"), "")
    return "\n".join(reversed(texts)), tools, prompt


def choose(text, tools, prompt):
    # 1) こちらに返事が要るもの：返事の最後だけ見る。「」（）と表の行は説明なので見ない
    tail = re.sub(r"「[^」]*」|（[^）]*）|`[^`]*`", "",
                  "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|")))[-300:]
    if "決めてほしい" in tail:
        return "Claudeから/決めてほしいことがあります"
    if "確認させてください" in tail:
        return "Claudeから/ひとつ確認させてください"

    # 2) 起きたこと：コマンドを書いたかではなく、成功の出力があったかで見る
    bash = [t for t in tools if t.get("name") == "Bash"]
    if any("git push" in t["input"].get("command", "") and re.search(r"^To \S+", t["result"], re.M) for t in bash):
        return "作業の報告/バックアップしました"

    # 3) 頼まれたもの：指示の言葉が1種類だけなら言い切る（手を動かした回だけ）
    worked = any(t.get("name") in ("Edit", "Write", "Bash") for t in tools)
    kinds = {"動画": "動画ができました確認してください", "資料": "資料ができました確認してください",
             "記事": "記事ができました確認してください", "画像": "画像ができました確認してください"}
    hits = [v for k, v in kinds.items() if k in prompt]
    if worked and len(hits) == 1:
        return "頼んだものができた/" + hits[0]

    # 4) 調べた回・編集した回
    if any(t.get("name") in ("WebSearch", "WebFetch") for t in tools):
        return "Claudeから/調べ終わりました"
    if any(t.get("name") in ("Edit", "Write") for t in tools):
        return "作業が終わった/作業が終わりました"
    return "作業が終わった/*"  # どれでもなければランダム


def main():
    data = json.load(sys.stdin)
    text, tools, prompt = last_turn(data["transcript_path"])
    text = data.get("last_assistant_message") or text
    folder, name = choose(text, tools, prompt).split("/")
    files = sorted((SOUNDS / folder).glob(f"*{'' if name == '*' else '_' + name}.mp3")) \
        or sorted((SOUNDS / "作業が終わった").glob("*.mp3"))
    subprocess.Popen(["afplay", str(random.choice(files))], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
