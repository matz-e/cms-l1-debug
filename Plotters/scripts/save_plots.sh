#!/bin/sh

[ -z "$dirs" ] && dirs=$(cat <<EOF
digiplotter
rechitplotter
rechitplotter00_5
rechitplotter01_0
rechitplotter02_0
transverserechitplotter
transverserechitplotter00_5
transverserechitplotter01_0
transverserechitplotter02_0
EOF
)

pus="2012C 45 66"

for d in $dirs; do
   while [ $(jobs|wc -l) -ge 10 ]; do
      sleep .1
   done

   save_plots.py plot_only="pileupplotter|trackplotter|$d\$" "cmp/{d}/recoAll_{p}.eps" \
      plots_{data,mc}_raw+reco-{2012C,45,66}.root &
   for p in $pus; do
      save_plots.py plot_only="pileupplotter|trackplotter|$d\$" "cmp/{d}/reco${p}_{p}.eps" \
         plots_{data,mc}_raw+reco-${p}.root &
   done
done

wait
echo "finito!"
