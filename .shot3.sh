#!/bin/bash
# $1=name $2=url $3=W $4=H $5=minlum
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
PY="C:/Users/Administrator/.dsh/dsh-runtimes/dsh-plugin-desktop-primary-runtime/dependencies/python/python.exe"
OUT="F:/服务器开发/网站开发/phase7-after/$1.png"
for try in 1 2 3 4; do
  PROF="C:/Users/ADMINI~1/AppData/Local/Temp/edge90_$1_$try"
  rm -rf "$PROF"
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$PROF" --screenshot="$OUT" --window-size=$3,$4 --virtual-time-budget=90000 "$2" >/dev/null 2>&1
  LUM=$("$PY" -c "
from PIL import Image
im = Image.open(r'$OUT').convert('L')
w,h = im.size
box = (0, int(h*0.3), w, int(h*0.95))
px = list(im.crop(box).getdata())
print(round(sum(px)/len(px), 1))
" 2>/dev/null)
  echo "$1 try$try lum=$LUM"
  if awk "BEGIN{exit !($LUM > $5)}"; then echo "OK $1"; rm -rf "$PROF"; exit 0; fi
  rm -rf "$PROF"
done
echo "WARN $1"
