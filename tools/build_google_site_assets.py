from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
OUT='assets/google-site'
NAVY=(0x1b,0x3a,0x7a); NAVY_DARK=(0x12,0x29,0x5a); NAVY_DEEP=(0x0d,0x1f,0x45)
RED=(0xd9,0x2b,0x34); GREEN=(0x3a,0xa6,0x3f)
SERIF='/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
SANS='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

def unwhite(im):
    # Un-mix a white background into alpha: a = 1 - min(r,g,b)/255
    im=im.convert('RGB'); px=im.load(); w,h=im.size
    out=Image.new('RGBA',(w,h)); o=out.load()
    for y in range(h):
        for x in range(w):
            r,g,b=px[x,y]; a=255-min(r,g,b)
            if a<=0: o[x,y]=(0,0,0,0); continue
            f=255/a
            o[x,y]=(min(255,int((r-255+a)*f)),min(255,int((g-255+a)*f)),min(255,int((b-255+a)*f)),a)
    return out
def circle_star(d):
    src=unwhite(Image.open('assets/images/fct-star.png'))
    star=src.resize((d*4,d*4),Image.LANCZOS)
    mask=Image.new('L',(d*4,d*4),0); ImageDraw.Draw(mask).ellipse((0,0,d*4-1,d*4-1),fill=255)
    from PIL import ImageChops
    star.putalpha(ImageChops.multiply(star.getchannel('A'),mask))
    return star.resize((d,d),Image.LANCZOS)

def logo(h, text_color, sub_color, name):
    S=4  # supersample for crisp text
    f1=ImageFont.truetype(SERIF, int(h*0.46*S)); f2=ImageFont.truetype(SANS, int(h*0.19*S))
    t1='Fauquier'; t2='COMMUNITY THEATRE'; track=int(h*0.05*S)
    tmp=ImageDraw.Draw(Image.new('L',(1,1)))
    w1=tmp.textlength(t1,font=f1); w2=sum(tmp.textlength(c,font=f2) for c in t2)+track*(len(t2)-1)
    gap=int(h*0.22*S); tw=int(max(w1,w2)); W=h*S+gap+tw+int(h*0.06*S)
    im=Image.new('RGBA',(W,h*S),(0,0,0,0)); d=ImageDraw.Draw(im)
    im.alpha_composite(circle_star(h*S),(0,0))
    x=h*S+gap
    a1=f1.getbbox('Fg'); a2=f2.getbbox('CT')
    h1=a1[3]-a1[1]; h2=a2[3]-a2[1]; sp=int(h*0.07*S)
    total=h1+sp+h2; y=(h*S-total)//2
    d.text((x,y-a1[1]),t1,font=f1,fill=text_color)
    yy=y+h1+sp-a2[1]
    for c in t2:
        d.text((x,yy),c,font=f2,fill=sub_color); x+=tmp.textlength(c,font=f2)+track
    im=im.resize((W//S,h),Image.LANCZOS)
    im.save(f'{OUT}/{name}'); print(name, im.size)

logo(240,NAVY_DARK,GREEN,'fct-logo-google-site-240h.png')
logo(240,(255,255,255),(0xf2,0xb6,0x32),'fct-logo-google-site-240h-white.png')
circle_star(512).save(f'{OUT}/fct-star-icon-512.png')

def navy_bg(W,H):
    bg=Image.new('RGB',(W,H)); px=bg.load()
    for y in range(H):
        for x in range(W):
            t=(x/W*0.35+y/H*0.65)
            px[x,y]=tuple(int(NAVY_DARK[i]+(NAVY_DEEP[i]-NAVY_DARK[i])*t) for i in range(3))
    glow=Image.new('RGB',(W,H),(0,0,0)); g=ImageDraw.Draw(glow)
    g.ellipse((int(W*0.55),int(-H*0.6),int(W*1.05),int(H*0.5)),fill=(int(GREEN[0]*.22),int(GREEN[1]*.22),int(GREEN[2]*.22)))
    g.ellipse((int(-W*0.2),int(H*0.5),int(W*0.35),int(H*1.6)),fill=(int(RED[0]*.24),int(RED[1]*.24),int(RED[2]*.24)))
    glow=glow.filter(ImageFilter.GaussianBlur(W//8))
    from PIL import ImageChops
    return ImageChops.add(bg,glow)

photo=Image.open('assets/images/fauquier-community-theatre-hero-1600.jpg').convert('RGB')

def fade_mask(w,h,a,b):
    m=Image.new('L',(w,h)); px=m.load()
    for x in range(w):
        t=x/(w-1)
        v=t/a if t<a else (1-t)/(1-b) if t>b else 1
        v=max(0,min(1,v))
        for y in range(h): px[x,y]=int(255*v)
    return m

def banner_navy(W,H,name,scale_h=None):
    bg=navy_bg(W,H)
    ph=scale_h or H; pw=int(photo.width*ph/photo.height)
    p=photo.resize((pw,ph),Image.LANCZOS)
    m=fade_mask(pw,ph,0.17,0.83)
    bg.paste(p,((W-pw)//2,(H-ph)//2),m)
    bg.save(f'{OUT}/{name}',quality=88,optimize=True,progressive=True); print(name,bg.size)

def banner_photo(W,H,name,focus=0.38):
    pw=W; ph=int(photo.height*W/photo.width)
    p=photo.resize((pw,ph),Image.LANCZOS)
    top=int((ph-H)*focus); p=p.crop((0,top,W,top+H))
    p.save(f'{OUT}/{name}',quality=88,optimize=True,progressive=True); print(name,p.size)

banner_navy(1440,480,'fct-banner-google-site-1440x480.jpg')
banner_navy(1440,1024,'fct-cover-google-site-1440x1024.jpg',scale_h=760)
banner_photo(1440,480,'fct-banner-google-site-photo-1440x480.jpg',focus=0.0)
