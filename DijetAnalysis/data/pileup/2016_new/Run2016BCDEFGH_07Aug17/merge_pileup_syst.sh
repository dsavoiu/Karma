#!/bin/sh
for f in _brilcalc_separate/pileup_80bins_*_Nominal*_FromBrilcalc.root; do

  f_up=`echo $f | sed -e 's|Nominal|MinBiasXSUp|g'`
  f_down=`echo $f | sed -e 's|Nominal|MinBiasXSDown|g'`
  out_file=`echo $f | sed -e 's|_Nominal||g'`
  out_file=${out_file#*/}
  
  if [ -f "${out_file}" ]; then
    echo "[INFO] Skipping existing file: ${out_file}"
    continue
  else
    echo "[INFO] Merging to file: ${out_file}..."
  fi
  
  python ${CMSSW_BASE}/src/TripleDiffDijets/work/Summer16_17Jul2018_v2/shape/palisade_tasks/extract_objects.py \
    -o pileup \
    -f "$f" "$f_up" "$f_down" \
    -n pileup{,Up,Down} \
    -d '.' \
    -w "${out_file}"
  
  if [[ $? != 0 ]]; then
    echo "[ERROR] Task failed, removing output: ${out_file}"
    rm "${out_file}"
  fi

done
