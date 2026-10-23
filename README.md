# claude-voice

Claude Code の作業が終わったら、AIで作った声で知らせる仕組みです。
場面ごとに鳴らし分けるだけでなく、返事の中身を読んで「決めてほしいことがあります」「動画ができました 確認してください」のように言い分けます。

解説記事：https://zenn.dev/takamasa_ai/articles/14dfe1741e140d

例の声（Takamasa）は ElevenLabs のボイスライブラリで公開しています：https://elevenlabs.io/app/voice-library?voiceId=xeuGp5e7xzV9lMbAK8Vd

## 入っているもの

| ファイル | 中身 |
|---|---|
| `sounds/` | すぐ使える声10本（下の一覧） |
| `phrases.tsv` | セリフの一覧（約130本）。行を足せば自分の言葉も作れます |
| `make_sounds.py` | `phrases.tsv` のセリフを ElevenLabs で音声にする |
| `play.sh` | 場面のフォルダから1本をランダムに鳴らす |
| `stop_voice.py` | 返事の中身と使った道具を見て、合う声を選んで鳴らす |
| `settings.example.json` | Claude Code に登録する設定の例 |

すぐ使える10本：終わりました／できました／完了しました／終わりました 確認してください／次は何をしますか？／続けますか？／確認をお願いします／許可をお願いします／エラーで途中で止まってしまいました／お疲れさまでした

## 使い方（Mac）

1. このフォルダを `~/claude-voice` に置く
2. `settings.example.json` の中身を `~/.claude/settings.json` に足す
3. Claude Code を開き直す

これで10本の声が鳴ります。

## 声を増やす・自分の言葉を足す

ElevenLabs の APIキーが要ります。

```bash
export ELEVENLABS_API_KEY=（自分のキー）
python3 make_sounds.py
```

`phrases.tsv` にあって `sounds/` にまだ無いセリフだけが作られます。

- 声は最初から作者の声（`VOICE_ID=xeuGp5e7xzV9lMbAK8Vd`）になっています。自分の声やライブラリの別の声にしたい場合は `VOICE_ID=（声のID） python3 make_sounds.py` のように変えてください
- モデルは `eleven_v4` です。日本語は v4 がいちばん自然でした
- APIキーは「テキスト読み上げ」だけの権限にして、クレジットの上限を入れておくのがおすすめです

## プレゼンの冒頭をAIの声で流す（`presentation/`）

解説記事（2本目）：（公開したらここにリンク）

長い原稿を段落ごとに作って1本につなぎ、スライドのボタンで流すための道具です。

| ファイル | 中身 |
|---|---|
| `presentation/音声台本.tsv` | 台本の表。1行＝1段落（例は3行） |
| `presentation/make_voices.py` | 表の行を段落ごとに音声にし、まとめ先ごとに1本につなぐ。前後の段落を `previous_text`／`next_text` で渡す |
| `presentation/join_with_gap.py` | 段落の間に0.7秒の無音を入れて1本のm4aにする（Mac標準の `afconvert` とPythonだけ・ffmpeg不要） |
| `presentation/slide_example.html` | 音声をボタンで流すスライドの最小の例 |

```bash
cd presentation
export ELEVENLABS_API_KEY=（自分のキー）
python3 make_voices.py --dry        # APIを呼ばずに、作る行と文字数だけ見る
python3 make_voices.py              # 作る（作り済みの段落は作らない）
python3 join_with_gap.py 音声 冒頭 冒頭.m4a   # 間を入れて1本に
```

- 作り直したい段落は `音声/` のそのファイルを消してから、もう一度実行します
- 使った文字数は `文字数の記録.csv` に残ります
- 声は最初から作者の声です。`VOICE_ID=（声のID）` で変えられます

## 使っていい範囲

`sounds/` の声は、AIで作った作者（Takamasa）の声です。

- PCの通知や、自分の作業に使うのは自由です（個人・仕事とも）
- 音声ファイルをそのまま人に配る・売ることはしないでください
- 作者のふりをすること、AIの声だと隠して使うことはしないでください

コード（`.py` `.sh` `.json`）は自由に使って、変えてかまいません。
