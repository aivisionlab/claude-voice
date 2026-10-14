#!/bin/zsh
# 使い方: play.sh <場面のフォルダ名>　そのフォルダから1本をランダムに鳴らす
files=("${0:A:h}/sounds/$1"/*.mp3(N))
(( ${#files} )) && afplay "${files[$(( RANDOM % ${#files} + 1 ))]}" >/dev/null 2>&1 &!
exit 0
