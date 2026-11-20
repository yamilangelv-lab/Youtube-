import json, re, os, sys, hashlib, soundfile as sf, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Youtube-/30e2fd9b-da38-5087-977b-a559c36efb67/scratchpad/stick")
from beats import BEATS
from kokoro_onnx import Kokoro
k=Kokoro("/tmp/claude-0/-home-user-Youtube-/30e2fd9b-da38-5087-977b-a559c36efb67/scratchpad/prod/tts/kokoro-v1.0.onnx","/tmp/claude-0/-home-user-Youtube-/30e2fd9b-da38-5087-977b-a559c36efb67/scratchpad/prod/tts/voices-v1.0.bin")
REP=[("Vitette","Vitéte"),("Sellanes","Sellánes"),("Di Tullio","Di Túlio"),("Zalloecheverría","Sayo Echeverría"),("Acassuso","Acasuso"),("Sileo","Siléo"),("Bolster","Bólster"),("La Casa de Papel","La Casa de Papel")]
def phon(t):
    for a,b in REP: t=t.replace(a,b)
    return t
out=[]
for i,(sc,p,txt) in enumerate(BEATS):
    if not txt: continue
    sents=[s for s in re.split(r'(?<=[.!?…])\s+(?=[¿¡"“A-ZÁÉÍÓÚÑ0-9])',txt) if s.strip()]
    for j,s in enumerate(sents):
        fn=os.path.join(os.path.dirname(os.path.abspath(__file__)),"audio",hashlib.md5((s+"|0.97").encode()).hexdigest()[:16]+".wav")
        if not os.path.exists(fn):
            a,sr=k.create(phon(s),voice="em_alex",speed=0.97,lang="es-419")
            nz=np.where(np.abs(a)>0.01)[0]
            if len(nz): a=a[max(0,nz[0]-240):nz[-1]+2400]
            sf.write(fn,a,sr)
        inf=sf.info(fn); out.append({"beat":i,"sent":j,"text":s,"file":fn,"dur":inf.frames/inf.samplerate})
json.dump(out,open("/tmp/claude-0/-home-user-Youtube-/30e2fd9b-da38-5087-977b-a559c36efb67/scratchpad/stick/sentences.json","w"),ensure_ascii=False,indent=0)
print("words",sum(len(t.split()) for _,_,t in BEATS),"speech s",round(sum(o['dur'] for o in out),1))
