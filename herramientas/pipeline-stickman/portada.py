import cairo, numpy as np, math
import engine as E
from PIL import Image, ImageFilter
W,H=1920,1080; GL=500
arr=np.zeros((H,W,4),np.uint8); surf=cairo.ImageSurface.create_for_data(memoryview(arr),cairo.FORMAT_RGB24,W,H,W*4); c=cairo.Context(surf)
def grad(x0,y0,x1,y1,stops):
    g=cairo.LinearGradient(x0,y0,x1,y1)
    for o,rgb in stops: g.add_color_stop_rgb(o,*rgb)
    return g
def outlined_stick(x,gy,s,p,face,d,acc,shirt,ol=(1,1,1),olw=12):
    ink=E.INK; E.INK=ol
    E.stick(c,x,gy,s,p,face,d,acc,shirt,0.0,lw=7.5+olw/s,blink=False)
    E.INK=ink
    return E.stick(c,x,gy,s,p,face,d,acc,shirt,0.0,lw=7.5,blink=False)
def btext(s,x,y,size,fill,sw=24,rot=0.0,align='l'):
    c.save(); c.translate(x,y); c.rotate(rot)
    c.select_font_face("Inter Display",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    e=c.text_extents(s); dx={'c':-e.width/2-e.x_bearing,'l':-e.x_bearing,'r':-e.width-e.x_bearing}[align]; dy=-e.height/2-e.y_bearing
    c.move_to(dx+9,dy+12); c.text_path(s); E.col(c,(0,0,0),0.45); c.fill()
    c.move_to(dx,dy); c.text_path(s); c.set_line_width(sw); c.set_line_join(cairo.LINE_JOIN_ROUND); E.col(c,E.INK); c.stroke_preserve(); E.col(c,fill); c.fill()
    c.restore(); return e.width

# --- sky ---
c.set_source(grad(0,0,0,GL,[(0,(0.53,0.78,0.97)),(1,(0.82,0.92,0.99))])); c.rectangle(0,0,W,GL); c.fill()
# police light glow
for k,(rgb,x) in enumerate([((1,0.2,0.2),1180),((0.2,0.4,1),1250)]):
    g=cairo.RadialGradient(x,380,10,x,380,260); g.add_color_stop_rgba(0,*rgb,0.35); g.add_color_stop_rgba(1,*rgb,0)
    c.set_source(g); c.rectangle(0,0,W,GL); c.fill()
# bank
E.bank(c,1560,GL,620,380,sign="BANCO",sub="Sucursal Acassuso")
E.police_car(c,1175,GL,0.0,1,0.62)
for i,x in enumerate([830,960,1085]):
    outlined_stick(x,GL,0.95,E.pose('point' if i==1 else ('shrug' if i==2 else 'stand'),0.4+i),'o',1,('cap_police',),E.BLUE,olw=6)
# --- underground ---
c.set_source(grad(0,GL,0,H,[(0,(0.50,0.36,0.24)),(1,(0.30,0.21,0.14))])); c.rectangle(0,GL,W,H-GL); c.fill()
rng=np.random.default_rng(5)
for i in range(70):
    x=rng.uniform(0,W); y=rng.uniform(GL+20,H); r=rng.uniform(4,14)
    E.circle(c,x,y,r,fill=(0.40,0.29,0.19),stroke=None)
E.line(c,[(0,GL),(W,GL)],14,E.INK)
c.set_source_rgb(0.33,0.62,0.30); c.rectangle(0,GL-10,W,10); c.fill(); E.line(c,[(0,GL-10),(W,GL-10)],5,E.INK)
# tunnel
ty0,ty1=650,1080
c.new_path(); c.move_to(-50,ty0+40); c.curve_to(500,ty0-30,1400,ty0-30,1980,ty0+40); c.line_to(1980,ty1); c.line_to(-50,ty1); c.close_path()
c.set_source(grad(0,ty0,0,ty1,[(0,(0.10,0.09,0.09)),(1,(0.05,0.05,0.06))])); c.fill_preserve(); c.set_line_width(12); E.col(c,E.INK); c.stroke()
# shaft from bank vault down to tunnel
c.new_path(); c.move_to(1460,GL+8); c.curve_to(1420,560,1300,610,1240,660); c.set_line_width(70); c.set_line_cap(cairo.LINE_CAP_ROUND); E.col(c,(0.10,0.09,0.09)); c.stroke()
# lantern glow
g=cairo.RadialGradient(720,820,20,720,820,560); g.add_color_stop_rgba(0,1,0.85,0.45,0.55); g.add_color_stop_rgba(1,1,0.85,0.45,0); c.set_source(g); c.rectangle(0,ty0-40,W,H); c.fill()
# water
c.set_source(grad(0,950,0,H,[(0,(0.30,0.52,0.70)),(1,(0.17,0.32,0.46))])); c.rectangle(0,950,W,130); c.fill()
for i in range(18): E.line(c,[(i*115+20,975+(i%3)*28),(i*115+70,975+(i%3)*28)],5,(0.65,0.82,0.95))
# boat + robbers
E.boat(c,700,960,2.3)
for i,x in enumerate([470,690,910]):
    outlined_stick(x,935,1.38,E.pose('paddle',0.35+i*0.55),'grin',1,('mask',),E.DARK,olw=10)
E.money_bag(c,1080,860,1.45); E.money_bag(c,1210,900,1.15)
for i,(x,y) in enumerate([(1120,760),(1260,800),(1010,770)]): E.text(c,"$",x,y,64,(0.55,0.90,0.45))
# text
btext("NADIE MIRÓ",60,120,150,(1,1,1),sw=26,rot=-0.03)
btext("ABAJO",60,300,210,(0.99,0.80,0.15),sw=30,rot=-0.03)
# arrow from text into tunnel
c.new_path(); c.move_to(250,415); c.curve_to(230,520,250,600,300,680); c.set_line_width(28); c.set_line_cap(cairo.LINE_CAP_ROUND)
E.col(c,E.INK); c.stroke_preserve(); c.set_line_width(15); E.col(c,(0.93,0.20,0.18)); c.stroke()
E.poly(c,[(345,745),(262,690),(330,650)],fill=(0.93,0.20,0.18),stroke=E.INK,lw=7)
surf.flush()
img=Image.fromarray(arr[...,[2,1,0]])
img.resize((1280,720),Image.LANCZOS).save('portada_final.jpg',quality=95)
img.save('portada_final_1920.png')
# mobile previews
sm=img.resize((246,138),Image.LANCZOS); sm.save('portada_mobile.png')
print('ok')
