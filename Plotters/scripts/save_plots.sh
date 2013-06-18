#!/bin/sh

[ -z "$dirs" ] && dirs=$(cat <<EOF
rechitplotter
rechitplotter00_5
rechitplotter01_0
rechitplotter02_0
trackplotter
transverserechitplotter
transverserechitplotter00_1
transverserechitplotter00_2
transverserechitplotter00_5
transverserechitplotter01_0
transverserechitplotter02_0
calotowerplotter
EOF
)

[ -z "$pus" ] && pus="2012C 45 66 front back"

for d in $dirs; do
   while [ $(jobs|wc -l) -ge 10 ]; do
      sleep .1
   done

   save_plots.py reemulated=n reweighed=n unweighed=y plot_only="$d\$" "cmp/{d}/recoVLPU_{p}.eps" \
      plots_{data,mc}_*reco-none*.root &

   save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAll_{p}.eps" \
      plots_{data,mc}_raw+reco-{2012C,45,66}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir_{p}.eps" \
      # plots_{data,mc}_raw+reco-{2012C,front,back}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir2012C_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,front,back}*.root &
   save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAll2012C_{p}.eps" \
      plots_{data,mc}_*reco-2012C{,ext2,ext3}.root &
   for p in $pus; do
      save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/reco${p}_{p}.eps" \
         plots_{data,mc}_*reco-${p}*.root &
   done
done

wait
echo "finito!"
