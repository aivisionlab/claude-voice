#!/usr/bin/env python3
"""音声台本.tsv の行を ElevenLabs で音声にして 音声/ に保存する。
同じ「まとめ先」の行は上から順につないで 音声/<まとめ先>.mp3 も作る。
作り済みのファイルは作り直さない（文字数を使わない）。使った文字数は 文字数の記録.csv に1行ずつ残す。

  export ELEVENLABS_API_KEY=（自分のキー）
  python3 make_voices.py          # 作る
  python3 make_voices.py --dry    # APIを呼ばず、作る行と文字数だけ出す
"""
import csv, datetime, json, os, pathlib, ssl, sys, urllib.error, urllib.request

try:
    import certifi  # python.org版のPythonはMacの証明書を見ないので、certifiの証明書を使う
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()

HERE = pathlib.Path(__file__).parent
TABLE = HERE / "音声台本.tsv"
OUT = HERE / "音声"
LOG = HERE / "文字数の記録.csv"
VOICE_ID = os.getenv("VOICE_ID", "xeuGp5e7xzV9lMbAK8Vd")  # 例は作者（Takamasa）の声。自分の声のIDに変えてOK
MODEL_ID = "eleven_v4"


def rows():
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        group, name, text = line.split("\t")
        yield group, name, text.replace("\\n", "\n")


def tts(key, text, prev_text, next_text):
    body = {"text": text, "model_id": MODEL_ID}
    # 前後の文を渡すと、段落ごとに作っても声の調子がつながりやすい
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"止まりました（{e.code}）：{e.read().decode(errors='replace')[:300]}")


def main():
    dry = "--dry" in sys.argv
    all_rows = list(rows())
    OUT.mkdir(exist_ok=True)
    key = "" if dry else os.getenv("ELEVENLABS_API_KEY", "")
    if not dry and not key:
        raise SystemExit("ELEVENLABS_API_KEY にAPIキーを入れてください")

    made = chars = 0
    for i, (group, name, text) in enumerate(all_rows):
        path = OUT / f"{name}.mp3"
        if path.exists():
            continue  # 作り済みは作らない＝文字数を使わない
        prev_text = all_rows[i - 1][2] if i > 0 and all_rows[i - 1][0] == group else ""
        next_text = all_rows[i + 1][2] if i + 1 < len(all_rows) and all_rows[i + 1][0] == group else ""
        print(f"{'作る予定' if dry else '作成'} {name}（{len(text)}字）")
        chars += len(text)
        if dry:
            continue
        path.write_bytes(tts(key, text, prev_text, next_text))
        made += 1
        new = not LOG.exists()
        with LOG.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["日時", "ファイル", "文字数", "モデル"])
            w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), name, len(text), MODEL_ID])

    # まとめ先ごとに1本へつなぐ（同じ形式のmp3なので、そのまま続けて書けば再生できる）
    groups = {}
    for group, name, _ in all_rows:
        groups.setdefault(group, []).append(OUT / f"{name}.mp3")
    for group, parts in groups.items():
        if len(parts) > 1 and all(p.exists() for p in parts):
            (OUT / f"{group}.mp3").write_bytes(b"".join(p.read_bytes() for p in parts))

    print(f"合計 {chars}字（{'APIは呼んでいません' if dry else f'{made}本作成'}）")


if __name__ == "__main__":
    main()
