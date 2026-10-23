"""音声/ の段落ごとのmp3を、間（無音）を入れて1本のm4aにつなぐ。ffmpegは使わない（Mac標準の afconvert とPythonだけ）"""
import pathlib, subprocess, sys, tempfile, wave

GAP = 0.7  # 段落の間の無音（秒）

def to_wav(mp3, wav):
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@44100", "-c", "1", str(mp3), str(wav)], check=True)

def main(src_dir, prefix, out):
    parts = sorted(pathlib.Path(src_dir).glob(f"{prefix}_*.mp3"))
    with tempfile.TemporaryDirectory() as tmp:
        wavs = []
        for p in parts:
            w = pathlib.Path(tmp) / (p.stem + ".wav")
            to_wav(p, w)
            wavs.append(w)
        joined = pathlib.Path(tmp) / "joined.wav"
        with wave.open(str(wavs[0])) as first:
            params = first.getparams()
        silence = b"\x00" * int(params.framerate * GAP) * params.sampwidth * params.nchannels
        with wave.open(str(joined), "wb") as out_w:
            out_w.setparams(params)
            for i, w in enumerate(wavs):
                with wave.open(str(w)) as r:
                    out_w.writeframes(r.readframes(r.getnframes()))
                if i < len(wavs) - 1:
                    out_w.writeframes(silence)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(joined), out], check=True)
    print(f"{len(parts)}本をつないで {out} を作りました")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
