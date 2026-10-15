import pcbnew as p, json, collections, math, pathlib, hashlib
src=pathlib.Path(r'G:\C++\CLOCK-master\hardware\schematic\v1.0\CLOCK_CORE\CLOCK_CORE.kicad_pcb')
b=p.LoadBoard(str(src)); mm=lambda n:round(p.ToMM(n),6); xy=lambda v:[mm(v.x),mm(v.y)]
tracks=list(b.GetTracks()); vias=[t for t in tracks if isinstance(t,p.PCB_VIA)]; traces=[t for t in tracks if not isinstance(t,p.PCB_VIA)]
outline=[]
for s in b.GetDrawings():
 if s.GetLayer()==p.Edge_Cuts: outline.append({'shape':s.GetShapeStr(),'start':xy(s.GetStart()),'end':xy(s.GetEnd()),'width':mm(s.GetWidth())})
holes=[]; texts=[]; pad_sizes=collections.Counter()
for f in b.GetFootprints():
 for pad in f.Pads():
  d=xy(pad.GetDrillSize())
  if max(d)>0:
   holes.append({'ref':f.GetReference(),'pad':pad.GetNumber(),'net':pad.GetNetname(),'pos':xy(pad.GetPosition()),'drill':d,'size':xy(pad.GetSize()),'npth':pad.GetAttribute()==p.PAD_ATTRIB_NPTH})
 for t in [f.Reference(), f.Value()]+[x for x in f.GraphicalItems() if isinstance(x,p.PCB_TEXT)]:
  if t.IsVisible() and t.GetLayer() in (p.F_SilkS,p.B_SilkS): texts.append({'ref':f.GetReference(),'text':t.GetText(),'size':xy(t.GetTextSize()),'thickness':mm(t.GetTextThickness())})
vs=[{'net':v.GetNetname(),'pos':xy(v.GetPosition()),'drill':mm(v.GetDrillValue()),'diameter':mm(v.GetWidth(p.F_Cu)),'type':int(v.GetViaType())} for v in vias]
circular=[{'ref':'via','pos':v['pos'],'d':v['drill']} for v in vs]+[{'ref':h['ref']+'.'+h['pad'],'pos':h['pos'],'d':h['drill'][0]} for h in holes if h['drill'][0]==h['drill'][1]]
near=[]
for i,a in enumerate(circular):
 for c in circular[i+1:]:
  gap=math.dist(a['pos'],c['pos'])-(a['d']+c['d'])/2
  near.append((round(gap,6),a,c))
near.sort(key=lambda a:a[0])
out={'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'layers':b.GetCopperLayerCount(),'thickness':mm(b.GetDesignSettings().GetBoardThickness()),'outline':outline,'footprints':len(list(b.GetFootprints())),'track_count':len(traces),'track_widths':dict(sorted(collections.Counter(mm(t.GetWidth()) for t in traces).items())),'via_count':len(vias),'via_sizes':dict(collections.Counter(str((v['diameter'],v['drill'],v['type'])) for v in vs)),'pad_holes':holes,'via_min_annulus':min((v['diameter']-v['drill'])/2 for v in vs),'closest_circular_holes':near[:10],'small_silk_texts':[t for t in texts if min(t['size'])<0.8 or t['thickness']<0.15],'zones':[{'name':z.GetZoneName(),'net':z.GetNetname(),'layers':[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],'clearance':mm(z.GetLocalClearance()),'min_thickness':mm(z.GetMinThickness())} for z in b.Zones()]}
dest=pathlib.Path(r'G:\C++\CLOCK-master\reports\CLOCK_CORE-jlc-audit-20261015\measurements.json'); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['small_silk_texts','pad_holes','zones']},ensure_ascii=False,indent=2))
print('HOLE_SIZES',dict(collections.Counter(str((h['drill'],h['size'],h['npth'])) for h in holes)))
print('MIN_PAD_HOLE', min(min(h['drill']) for h in holes)); print('SMALL_TEXT_COUNT',len(out['small_silk_texts'])); print('ZONE_COUNT',len(out['zones']))
