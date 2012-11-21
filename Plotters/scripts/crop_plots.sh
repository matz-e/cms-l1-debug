#!/bin/sh

if [ -z "$1" ]; then
   echo "usage: $0 dir"
   exit 1
fi

set -e

(
   cd "$1"
   for f in *.ps; do
      ps2pdf "$f" tmp.pdf
      pdfcrop tmp.pdf "${f%%s}df"
      rm "$f" tmp.pdf
   done
)
