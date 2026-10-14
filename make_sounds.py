#!/usr/bin/env python3
"""phrases.tsv のセリフを ElevenLabs で音声にして sounds/<場面>/<番号>_<セリフ>.mp3 に保存する。
作り済みのファイルは作り直さない（文字数を使わない）。"""
import json, os, pathlib, re, urllib.request

HERE = pathlib.Path(__file__).parent
VOICE_ID = os.getenv("VOICE_ID", "xeuGp5e7xzV9lMbAK8Vd")  # 例は作者（Takamasa）の声。自分の声のIDに変えてOK
MODEL_ID = "eleven_v4"

try:
    import certifi, ssl  # python.org版のPythonはMacの証明書を見ないため
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = None


def main():
    key = os.environ["ELEVENLABS_API_KEY"]
    count = {}
    for line in (HERE / "phrases.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        folder, text = line.split("\t")
        count[folder] = count.get(folder, 0) + 1
        label = re.sub(r"[。、？！?!\s]", "", text)
        path = HERE / "sounds" / folder / f"{count[folder]:02d}_{label}.mp3"
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
            data=json.dumps({"text": text, "model_id": MODEL_ID}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=CTX) as r:
            path.write_bytes(r.read())
        print("作成:", path.relative_to(HERE))


if __name__ == "__main__":
    main()
