echo Imperativos
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Imperativos" $file | wc -l; done
echo no distorsión
for file in ./RC_data_to_annotate_90%_ann_*; do grep "no distorsi" $file | wc -l; done
echo Razonamiento emocional
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Razonamiento emocional" $file | wc -l; done
echo Leer la mente
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Leer la mente" $file | wc -l; done
echo Personalización
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Personalizaci" $file | wc -l; done
echo Abstracción
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Abstracci" $file | wc -l; done
echo Sobregeneralización
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Sobregeneralizaci" $file | wc -l; done
echo Adivinación
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Adivinaci" $file | wc -l; done
echo Catastrofismo
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Catastrofismo" $file | wc -l; done
echo Pensamiento absolutista
for file in ./RC_data_to_annotate_90%_ann_*; do grep "Pensamiento absolutista" $file | wc -l; done