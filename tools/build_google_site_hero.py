"""Build the hero image for use as an inline image on the Google Site.

The section behind it is solid #12295a. The photo's sides fade into that
navy (as on fauquiertheater.org), a sky buffer is added above the roof sign
that eases gently from navy into the photo's own sky, and the bottom edge is
left hard because the section cuts it off.
"""
from PIL import Image

NAVY_DARK=(0x12,0x29,0x5a)
OUT='assets/google-site'

def smooth(t): return t*t*(3-2*t)

def build(buffer=90, blend_into_photo=40, name='fct-hero-google-site-1600.jpg'):
    photo=Image.open('assets/images/fauquier-community-theatre-hero-1600.jpg').convert('RGB')
    pw,ph=photo.size; H=ph+buffer
    im=Image.new('RGB',(pw,H),NAVY_DARK); im.paste(photo,(0,buffer))
    px=im.load(); top=[photo.getpixel((x,0)) for x in range(pw)]
    # Vertical ease: pure navy at the top row -> pure sky `blend_into_photo` px
    # below the photo's top edge, so the join never reads as a hard band.
    span=buffer+blend_into_photo
    for y in range(span):
        k=smooth(y/(span-1))
        for x in range(pw):
            src=top[x] if y<buffer else px[x,y]
            px[x,y]=tuple(int(NAVY_DARK[i]*(1-k)+src[i]*k) for i in range(3))
    # Horizontal fade on both sides, same stops as the site's CSS mask (17% / 83%).
    a,b=0.17,0.83
    for x in range(pw):
        t=x/(pw-1); v=t/a if t<a else (1-t)/(1-b) if t>b else 1
        v=smooth(max(0,min(1,v)))
        if v>=1: continue
        for y in range(H):
            c=px[x,y]; px[x,y]=tuple(int(NAVY_DARK[i]*(1-v)+c[i]*v) for i in range(3))
    im.save(f'{OUT}/{name}',quality=90,optimize=True,progressive=True); print(name,im.size)

if __name__=='__main__':
    build()
