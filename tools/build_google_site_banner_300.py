"""Build the Google Sites 'Banner' header (1440x300 and 2x).

The whole building photo fits the banner height and feathers out to solid
#12295a on all four sides.
"""
from PIL import Image

NAVY_DARK=(0x12,0x29,0x5a)
OUT='assets/google-site'

def feather(w,h,fx=0.20,fy_top=0.05,fy_bot=0.14):
    """Mask that is opaque in the middle and fades to 0 at every edge."""
    m=Image.new('L',(w,h)); px=m.load()
    def ramp(t,a,b):
        v=t/a if t<a else (1-t)/(1-b) if t>b else 1
        v=max(0,min(1,v)); return v*v*(3-2*v)  # smoothstep
    xs=[ramp(x/(w-1),fx,1-fx) for x in range(w)]
    ys=[ramp(y/(h-1),fy_top,1-fy_bot) for y in range(h)]
    for y in range(h):
        for x in range(w): px[x,y]=int(255*xs[x]*ys[y])
    return m

def build(W,H,name):
    photo=Image.open('assets/images/fauquier-community-theatre-hero-1600.jpg').convert('RGB')
    ph=H; pw=int(photo.width*ph/photo.height)
    p=photo.resize((pw,ph),Image.LANCZOS)
    bg=Image.new('RGB',(W,H),NAVY_DARK)
    bg.paste(p,((W-pw)//2,0),feather(pw,ph))
    bg.save(f'{OUT}/{name}',quality=90,optimize=True,progressive=True); print(name,bg.size)

if __name__=='__main__':
    build(1440,300,'fct-banner-google-site-1440x300.jpg')
    build(2880,600,'fct-banner-google-site-2880x600.jpg')
