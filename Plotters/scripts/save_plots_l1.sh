#!/bin/sh

[ -z "$dirs" ] && dirs=$(cat <<EOF
pileupplotter
trackplotter
caloregionplotter
gctplotter
EOF
)
# digiplotter
# jetplotter
# triggerprimitivedigiplotter

[ -z "$pus" ] && pus="2012C 45 66"

for d in $dirs; do
   while [ $(jobs|wc -l) -ge 10 ]; do
      sleep .1
   done

   save_plots.py reemulated=n reweighed=n unweighed=y plot_only="$d\$" "cmp/{d}/recoVLPU_{p}.eps" \
      plots_{data,mc}_*reco-none*.root &

   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAll_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,45,66}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,front,back}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir2012C_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,front,back}*.root &
   # for p in $pus; do
      # save_plots.py reemulated=n reweighed=y unweighed=y plot_only="$d\$" "cmp/{d}/reco${p}_{p}.eps" \
         # plots_{data,mc}_*reco-${p}*.root &
      # save_plots.py reemulated=n reweighed=y unweighed=n plot_only="$d\$" "cmp/{d}.reweigh/reco${p}_{p}.eps" \
         # plots_{data,mc}_*reco-${p}*.root &
      # save_plots.py reemulated=y reweighed=y unweighed=n plot_only="$d\$" "cmp/{d}.reemul/reco${p}_{p}.eps" \
         # plots_{data,mc}_*reco-${p}*.root &
   # done
done

wait
echo "finito!"
