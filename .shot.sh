#!/bin/bash
# $1=name $2=url $3=W $4=H
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
PY="C:/Users/Administrator/.dsh/dsh-runtimes/dsh-plugin-desktop-primary-runtime/dependencies/python/python.exe"
OUT="F:/服务器开发/网站开发/phase7-before/$1.png"
for try in 1 2 3; do
  PROF="C:/Users/ADMINI~1/AppData/Local/Temp/edge_prof_$1_$try"
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$PROF" --screenshot="$OUT" --window-size=$3,$4 --virtual-time-budget=20000 "$2" >/dev/null 2>&1
  LUM=$("$PY" -c "
from PIL import Image
im = Image.open(r'$OUT').convert('L')
w,h = im.size
box = (int(w*0.72), int(h*0.45), int(w*0.86), int(h*0.65))
reg = im.crop(box)
px = list(reg.getdata())
print(round(sum(px)/len(px), 1))
" 2>/dev/null)
  echo "$1 try$try lum=$LUM"
  if awk "BEGIN{exit !($LUM > 50)}"; then echo "OK $1"; rm -rf "$PROF"; exit 0; fi
  rm -rf "$PROF"
done
echo "WARN $1"
