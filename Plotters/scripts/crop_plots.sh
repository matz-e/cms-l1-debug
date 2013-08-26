#!/bin/sh

if [ -z "$1" ]; then
   echo "usage: $0 dir"
   exit 1
fi

set -e

find $* -name *.eps|while read file; do
   while [ $(jobs|wc -l) -ge 30 ]; do
      sleep .1
   done
   (
      echo "converting $file..."
      epstopdf -o="${file%.eps}_tmp.pdf" "$file"
      pdfcrop "${file%.eps}_tmp.pdf" "${file%eps}pdf"
      rm "$file" "${file%.eps}_tmp.pdf"
   ) &
done

wait
echo "finito!"
