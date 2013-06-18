#!/bin/sh

shopt -s extglob

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

   # save_plots.py reemulated=n reweighed=n unweighed=y plot_only="$d\$" "cmp/{d}/recoVLPU_{p}.eps" \
      # plots_{data,mc}_*reco-none*.root &

   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAll_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,45,66}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,front,back}.root &
   # save_plots.py unweighed=n plot_only="$d\$" "cmp/{d}/recoAllDir2012C_{p}.eps" \
      # plots_{data,mc}_*reco-{2012C,front,back}*!(no*).root &
   for p in $pus; do
      save_plots.py reemulated=n reweighed=y unweighed=y plot_only="$d\$" "cmp/{d}/reco${p}_{p}.eps" \
         $(ls plots_{data,mc}_*reco-${p}*.root|grep -v no) &
      save_plots.py reemulated=n reweighed=y unweighed=n plot_only="$d\$" "cmp/{d}.reweigh/reco${p}_{p}.eps" \
         $(ls plots_{data,mc}_*reco-${p}*.root|grep -v no) &
      save_plots.py reemulated=y reweighed=y unweighed=n unemulated=n plot_only="$d\$" "cmp/{d}.reemul/reco${p}_{p}.eps" \
         $(ls plots_{data,mc}_*reco-${p}*.root|grep -v no) &
      if [ $p == "2012C" ]; then
         save_plots.py reemulated=n reweighed=y unweighed=y plot_only="$d\$" "cmp/{d}/reco${p}noE_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noE.root plots_mc_*reco-${p}{,ext2,ext3}noE.root) &
         save_plots.py reemulated=n reweighed=y unweighed=n plot_only="$d\$" "cmp/{d}.reweigh/reco${p}noE_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noE.root plots_mc_*reco-${p}{,ext2,ext3}noE.root) &
         save_plots.py reemulated=y reweighed=y unweighed=n unemulated=n plot_only="$d\$" "cmp/{d}.reemul/reco${p}noE_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noE.root plots_mc_*reco-${p}{,ext2,ext3}noE.root) &
         save_plots.py reemulated=n reweighed=y unweighed=y plot_only="$d\$" "cmp/{d}/reco${p}noH_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noH.root plots_mc_*reco-${p}{,ext2,ext3}noH.root) &
         save_plots.py reemulated=n reweighed=y unweighed=n plot_only="$d\$" "cmp/{d}.reweigh/reco${p}noH_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noH.root plots_mc_*reco-${p}{,ext2,ext3}noH.root) &
         save_plots.py reemulated=y reweighed=y unweighed=n unemulated=n plot_only="$d\$" "cmp/{d}.reemul/reco${p}noH_{p}.eps" \
            $(ls -U plots_data_*reco-${p}noH.root plots_mc_*reco-${p}{,ext2,ext3}noH.root) &
      fi
   done
done

wait
echo "finito!"
