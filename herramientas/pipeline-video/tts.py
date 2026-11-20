import json, re, os, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
P=os.path.dirname(os.path.abspath(__file__))
blocks=json.load(open(f"{P}/blocks.json"))
k=Kokoro(f"{P}/tts/kokoro-v1.0.onnx",f"{P}/tts/voices-v1.0.bin")
REP=[("Juicy Fruit","Yúsi Frut"),("Henley Beach","Jénli Bich"),("Footscray","Futscréi"),("ADN","a de ene"),
("Boxall","Bóksol"),("Colleen","Colín"),("Derek Abbott","Dérek Ábot"),("Abbott","Ábot"),("Jessica","Yésica"),
("Cedric Stanton Hicks","Sédric Stánton Jiks"),("John Harber Phillips","Yon Járber Fílips"),("Gordon Cramer","Górdon Créimer"),
("Dorothy Robertson","Dóroti Róbertson"),("Freda","Frida"),("Thomas","Tómas"),("Charles","Chárls"),("Army Club","Armi Clab"),
("Somerton","Sómerton"),("Melbourne","Mélburn"),("Sydney","Sídni"),("Keane","Kin"),("Webb","Uéb"),("Glenelg","Glenélg"),
("Ellen","Élen"),("Jo,","Yo,"),("Carl ","Carl "),("Kensitas","Kensítas"),("ouabaína","ua-baína"),("Fitzpatrick","Fitspátrik")]
def clean(t): return t.replace('*','').replace('—',', ').replace('...','…')
def phon(t):
    for a,b in REP: t=t.replace(a,b)
    return t
os.makedirs(f"{P}/audio",exist_ok=True)
out=[]
for i,(typ,txt) in enumerate(blocks):
    if typ!='N': continue
    txt=clean(txt)
    sents=[s for s in re.split(r'(?<=[.!?…])\s+(?=[¿¡"“A-ZÁÉÍÓÚÑ0-9])',txt) if s.strip()]
    for j,s in enumerate(sents):
        fn=f"{P}/audio/b{i:03d}_{j:02d}.wav"
        if not os.path.exists(fn):
            a,sr=k.create(phon(s),voice="em_alex",speed=0.93,lang="es-419")
            # trim silence
            nz=np.where(np.abs(a)>0.01)[0]
            if len(nz): a=a[max(0,nz[0]-240):nz[-1]+2400]
            sf.write(fn,a,sr)
        info=sf.info(fn)
        out.append({"block":i,"sent":j,"text":s,"file":fn,"dur":info.frames/info.samplerate})
    print(i,len(sents),flush=True)
json.dump(out,open(f"{P}/sentences.json","w"),ensure_ascii=False,indent=1)
print("total speech sec",sum(o['dur'] for o in out))
