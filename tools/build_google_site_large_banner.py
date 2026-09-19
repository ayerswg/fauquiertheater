"""Build the Google Sites 'Large banner' header image.

Full building photo fits inside the banner height, sides fade into the site's
navy gradient, and extra sky is added above the roof sign so the Google Sites
navigation bar (which overlays the top of the header) never covers 'THEATER'.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops

NAVY_DARK=(0x12,0x29,0x5a); NAVY_DEEP=(0x0d,0x1f,0x45)
RED=(0xd9,0x2b,0x34); GREEN=(0x3a,0xa6,0x3f)
OUT='assets/google-site'

def navy_bg(W,H):
    bg=Image.new('RGB',(W,H)); px=bg.load()
    for y in range(H):
        for x in range(W):
            t=(x/W*0.35+y/H*0.65)
            px[x,y]=tuple(int(NAVY_DARK[i]+(NAVY_DEEP[i]-NAVY_DARK[i])*t) for i in range(3))
    glow=Image.new('RGB',(W,H),(0,0,0)); g=ImageDraw.Draw(glow)
    g.ellipse((int(W*0.55),int(-H*0.6),int(W*1.05),int(H*0.5)),fill=tuple(int(c*.22) for c in GREEN))
    g.ellipse((int(-W*0.2),int(H*0.5),int(W*0.35),int(H*1.6)),fill=tuple(int(c*.24) for c in RED))
    return ImageChops.add(bg,glow.filter(ImageFilter.GaussianBlur(W//8)))

def fade_mask(w,h,a=0.17,b=0.83):
    m=Image.new('L',(w,h)); px=m.load()
    for x in range(w):
        t=x/(w-1); v=t/a if t<a else (1-t)/(1-b) if t>b else 1
        for y in range(h): px[x,y]=int(255*max(0,min(1,v)))
    return m

def build(W,H,headroom,name):
    photo=Image.open('assets/images/fauquier-community-theatre-hero-1600.jpg').convert('RGB')
    ph=H-headroom; pw=int(photo.width*ph/photo.height)
    p=photo.resize((pw,ph),Image.LANCZOS)
    # Extend the sky upward: each column continues the photo's top-row colour,
    # deepening toward navy at the very top so white nav text stays legible.
    top=[p.getpixel((x,0)) for x in range(pw)]
    sky=Image.new('RGB',(pw,headroom)); sp=sky.load()
    for y in range(headroom):
        t=y/max(1,headroom-1); k=0.45+0.55*(t*t)  # 0.45 navy blend at top -> 1.0 at photo edge
        for x in range(pw):
            c=top[x]; sp[x,y]=tuple(int(NAVY_DARK[i]*(1-k)+c[i]*k) for i in range(3))
    full=Image.new('RGB',(pw,H)); full.paste(sky,(0,0)); full.paste(p,(0,headroom))
    bg=navy_bg(W,H); bg.paste(full,((W-pw)//2,0),fade_mask(pw,H))
    bg.save(f'{OUT}/{name}',quality=90,optimize=True,progressive=True); print(name,bg.size)

if __name__=='__main__':
    build(1440,600,100,'fct-large-banner-google-site-1440x600.jpg')
    build(2048,853,142,'fct-large-banner-google-site-2048x853.jpg')
