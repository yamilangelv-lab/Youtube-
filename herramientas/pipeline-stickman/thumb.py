import cairo, numpy as np, math, sys
import engine as E
from PIL import Image
W,H=1920,1080
def new():
    arr=np.zeros((H,W,4),np.uint8); s=cairo.ImageSurface.create_for_data(memoryview(arr),cairo.FORMAT_RGB24,W,H,W*4); return arr,s,cairo.Context(s)
def save(arr,surf,name):
    surf.flush(); Image.fromarray(arr[...,[2,1,0]]).resize((1280,720),Image.LANCZOS).save(name,quality=95)
def burst(c,cx,cy,a,b,n=28):
    E.col(c,a); c.paint()
    for i in range(n):
        if i%2: continue
        a0=i/n*2*math.pi; a1=(i+1)/n*2*math.pi
        c.move_to(cx,cy); c.line_to(cx+3000*math.cos(a0),cy+3000*math.sin(a0)); c.line_to(cx+3000*math.cos(a1),cy+3000*math.sin(a1)); c.close_path()
        E.col(c,b); c.fill()
def btext(c,s,x,y,size,fill,stroke=E.INK,sw=22,rot=0.0,align='c'):
    c.save(); c.translate(x,y); c.rotate(rot)
    c.select_font_face("Inter Display",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    e=c.text_extents(s); dx={'c':-e.width/2-e.x_bearing,'l':-e.x_bearing,'r':-e.width-e.x_bearing}[align]
    c.move_to(dx+8,-e.height/2-e.y_bearing+10); c.text_path(s); E.col(c,(0,0,0),0.35); c.fill()
    c.move_to(dx,-e.height/2-e.y_bearing); c.text_path(s)
    c.set_line_width(sw); c.set_line_join(cairo.LINE_JOIN_ROUND); E.col(c,stroke); c.stroke_preserve(); E.col(c,fill); c.fill(); c.restore()
def glow_stick(c,x,gy,s,p,face,d,acc,shirt,lw=7.5):
    # white outline for separation from background
    E.stick(c,x,gy,s,p,face,d,acc,shirt,0.0,lw=lw+9,blink=False,alpha=1.0) if False else None
    E.stick(c,x,gy,s,p,face,d,acc,shirt,0.0,lw=lw,blink=False)
def sweat(c,x,y,s=1.0):
    c.save(); c.translate(x,y); c.scale(s,s); c.move_to(0,-30); c.curve_to(18,0,14,22,0,22); c.curve_to(-14,22,-18,0,0,-30)
    E.col(c,(0.55,0.8,1.0)); c.fill_preserve(); c.set_line_width(4); E.col(c,E.INK); c.stroke(); c.restore()

# ---------- A: LA TRAICIÓN ----------
arr,surf,c=new()
burst(c,960,600,(0.98,0.76,0.20),(0.96,0.66,0.12))
E.col(c,(0.62,0.48,0.34)); c.rectangle(0,980,W,100); c.fill(); E.line(c,[(0,980),(W,980)],10)
for (x,y,s) in [(180,950,1.5),(380,965,1.7),(290,820,1.3)]: E.money_bag(c,x,y,s)
r=E.stick(c,620,980,1.95,E.pose('handsup',0.2,shake=0),'o',1,('mask',),E.DARK,0.0,lw=9,blink=False)
sweat(c,r['head'][0]+80,r['head'][1]-10,1.3)
a=E.stick(c,1450,980,1.95,E.pose('point',0.0),'angry',-1,('hair_long',('dress',E.PURPLE),'dress'),None,0.0,lw=9,blink=False)
E.heart(c,1050,560,1.3,broken=0.9)
btext(c,"TRAICIONADOS",960,140,170,(1,1,1),sw=26,rot=-0.02)
btext(c,"$19M",1640,330,140,(0.45,0.85,0.40),sw=20,rot=0.06)
save(arr,surf,'thumb_A.jpg')

# ---------- B: LA FUGA ----------
arr,surf,c=new()
E.col(c,(0.10,0.10,0.12)); c.paint()
c.new_path(); c.arc(760,600,620,0,2*math.pi); E.col(c,(0.24,0.24,0.27)); c.fill()
for k in range(3): E.circle(c,760,600,640+k*34,stroke=E.INK,w=14)
E.col(c,E.WATER); c.rectangle(0,820,W,260); c.fill()
for i in range(16): E.line(c,[(i*130,850+(i%3)*40),(i*130+60,850+(i%3)*40)],6,(0.75,0.88,0.98))
E.boat(c,760,830,2.6)
for i in range(3): E.stick(c,500+i*230,800,1.45,E.pose('paddle',0.3+i*0.6),'grin',1,('mask',),E.DARK,0.0,lw=8,blink=False)
E.money_bag(c,1110,700,1.5); E.money_bag(c,1230,740,1.2)
btext(c,"19 MILLONES",1380,170,160,(0.45,0.85,0.40),sw=24,rot=-0.02)
btext(c,"POR LAS CLOACAS",1420,330,96,(1,1,1),sw=18,rot=-0.02)
E.stick(c,1660,1060,1.6,E.pose('shrug',0.5),'o',-1,('cap_police',),E.BLUE,0.0,lw=8,blink=False)
E.question(c,1820,700,260,1.0)
save(arr,surf,'thumb_B.jpg')

# ---------- C: LA NOTA ----------
arr,surf,c=new()
burst(c,1300,540,(0.96,0.95,0.92),(0.90,0.89,0.85))
E.note(c,1250,560,1.35,-0.06,["En barrio de ricachones,","sin armas ni rencores.","Es solo plata, no amores."],46)
E.stick(c,330,1060,2.2,E.pose('shrug',0.5),'o',1,('cap_police',),E.BLUE,0.0,lw=9,blink=False)
btext(c,"LES DEJARON",1260,150,150,(1,1,1),sw=24,rot=-0.02)
btext(c,"ESTO",1500,930,170,(0.95,0.25,0.22),sw=24,rot=-0.05)
E.arrow(c,1380,900,1280,790,E.RED,16,1.0,46)
save(arr,surf,'thumb_C.jpg')
print('ok')
