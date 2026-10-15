from pathlib import Path
import re, shutil, hashlib, datetime
import pcbnew as p
src=Path(r'G:\C++\CLOCK-master\hardware\schematic\v1.0\CLOCK_CORE\CLOCK_CORE.kicad_pcb')
data=src.read_bytes()
text=data.decode('utf-8')
# Find balanced property forms, respecting quoted strings and escapes.
starts=list(re.finditer(r'\(property\s+"Reference"',text))
edits=[]
for m in starts:
    depth=0; quoted=False; escaped=False; end=None
    for i in range(m.start(),len(text)):
        ch=text[i]
        if quoted:
            if escaped: escaped=False
            elif ch=='\\': escaped=True
            elif ch=='"': quoted=False
        elif ch=='"': quoted=True
        elif ch=='(': depth+=1
        elif ch==')':
            depth-=1
            if depth==0: end=i+1; break
    if end is None: raise RuntimeError('Unbalanced property')
    form=text[m.start():end]
    if not re.search(r'\(layer\s+"[FB]\.SilkS"\)',form): continue
    if re.search(r'\(hide\s+yes\)',form): continue
    if re.search(r'\(hide\s+no\)',form):
        updated=re.sub(r'\(hide\s+no\)','(hide yes)',form,count=1)
    else:
        updated=re.sub(r'(\(layer\s+"[FB]\.SilkS"\))',r'\1 (hide yes)',form,count=1)
    edits.append((m.start(),end,updated))
for start,end,new in reversed(edits): text=text[:start]+new+text[end:]
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=src.with_name(src.name+'.backup-hide-references-'+stamp)
shutil.copy2(src,backup)
tmp=src.with_name('CLOCK_CORE.hide-reference-check.kicad_pcb')
try:
    tmp.write_bytes(text.encode('utf-8'))
    board=p.LoadBoard(str(tmp))
    visible=[f.GetReference() for f in board.GetFootprints() if f.Reference().GetLayer() in (p.F_SilkS,p.B_SilkS) and f.Reference().IsVisible()]
    if visible: raise RuntimeError('Visible references remain: '+str(visible))
    if src.read_bytes()!=data: raise RuntimeError('PCB changed concurrently; original not overwritten')
    src.write_bytes(tmp.read_bytes())
    print('Hidden reference fields:',len(edits))
    print('Remaining visible silk references:',len(visible))
    print('Backup:',backup)
    print('Only Reference property hide flags changed; all other bytes preserved.')
finally:
    if tmp.exists(): tmp.unlink()
