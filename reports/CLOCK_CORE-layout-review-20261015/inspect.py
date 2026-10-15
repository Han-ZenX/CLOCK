import pcbnew as p,json,collections,pathlib
b=p.LoadBoard(r'hardware\schematic\v1.0\CLOCK_CORE\CLOCK_CORE.kicad_pcb'); mm=lambda n:round(p.ToMM(n),4)
for f in b.GetFootprints():
 if f.GetReference().startswith(('U','J','CN','RF','H','TP')) or f.GetReference() in ['R20','C51']:
  print(f.GetReference(),f.GetValue(),f.GetLayerName(),mm(f.GetPosition().x),mm(f.GetPosition().y),'DNP',f.IsDNP())
  if f.GetReference().startswith(('U','J','CN','H','TP')): print(' pads:',[(x.GetNumber(),x.GetNetname()) for x in f.Pads() if x.GetDrillSizeX()==0 or x.GetNumber()!='49'])
print('BOARD TEXTS',[(x.GetText(),mm(x.GetTextSize().y),mm(x.GetTextThickness()),x.GetLayerName()) for x in b.GetDrawings() if isinstance(x,p.PCB_TEXT)])
print('ZONES',[(z.GetNetname(),[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],z.GetPadConnection(),mm(z.GetThermalReliefGap()),mm(z.GetThermalReliefSpokeWidth())) for z in b.Zones() if z.GetNetname() in ['GND','VDDDIG']])
d=json.load(open(r'reports\CLOCK_CORE-layout-review-20261015\drc.json',encoding='utf-8')); print('DRC',collections.Counter((x['severity'],x['type']) for x in d['violations']))
import fitz
s=fitz.open(r'reports\CLOCK_CORE-layout-review-20261015\front.svg'); pdf=fitz.open('pdf',s.convert_to_pdf()); pdf[0].get_pixmap(matrix=fitz.Matrix(5,5)).save(r'reports\CLOCK_CORE-layout-review-20261015\front.png')
