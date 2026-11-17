"""게시 버전 5의 JavaScript 계산식을 Python으로 변환한 순수 계산 모듈."""
import json
import math
from pathlib import Path

COP = dict(json.loads(Path(__file__).with_name('cop_data.json').read_text()))
NAMES = ['누진제', '일반용', '계절시간별']
DEFAULTS = dict(q=1143.34, g=98.1288, b=226.1, kw=10., kw2=10.,
                f=6160., f2=4310., p=119., l1=200., l2=400.,
                p1=120., p2=214.6, p3=307.3, off=138.7, mid=184.7,
                peak=220.5, w1=40., w2=10., w3=50., keep=False,
                efElectric=.4173, efGas=.20245)

def validate(s):
    for k in DEFAULTS:
        if not math.isfinite(float(s[k])) or s[k] < 0:
            raise ValueError('입력값은 유한한 0 이상의 수여야 합니다.')
    if s['q'] <= 0 or s['g'] <= 0:
        raise ValueError('열수요와 가스 유효 열단가는 0보다 커야 합니다.')
    if not 0 < s['l1'] < s['l2']:
        raise ValueError('누진 상한은 0 < 1단계 < 2단계여야 합니다.')
    if abs(s['w1'] + s['w2'] + s['w3'] - 100) > 1e-7:
        raise ValueError('계절시간별 전력비중 합계는 100%여야 합니다.')

def rate(s):
    return sum(s[p]*s[w] for p,w in [('off','w1'),('mid','w2'),('peak','w3')])/100

def bill(e,s):
    return (min(e,s['l1'])*s['p1'] + max(0,min(e,s['l2'])-s['l1'])*s['p2']
            + max(0,e-s['l2'])*s['p3'])

def cost(k,x,c,s):
    power=x*s['q']/c
    gas=(1-x)*s['q']*s['g']
    if k == 0:
        elec=bill(s['b']+power,s)-bill(s['b'],s)
    else:
        fixed=s['kw']*s['f'] if k == 1 else s['kw2']*s['f2']
        elec=(fixed if x>0 or s['keep'] else 0)+(s['p'] if k==1 else rate(s))*power
    return dict(total=elec+gas,elec=elec,gas=gas,power=power,x=x)

def optimum(k,t,s):
    c=COP[t]
    clip=lambda x:max(0,min(1,x))
    xs=[0,clip((s['l1']-s['b'])*c/s['q']),clip((s['l2']-s['b'])*c/s['q']),1] if k==0 else [0,1]
    best=cost(k,0,c,s)
    for x in xs:
        candidate=cost(k,x,c,s)
        if candidate['total'] < best['total']-1e-7:
            best=candidate
    base=cost(k,0,c,s)['total']
    hp=cost(k,1,c,s)['total']
    return dict(**best,c=c,base=base,saving=base-best['total'],
                percent=(base-best['total'])/base if base>0 else None,
                hpOnly=hp,hpSaving=hp-best['total'],
                hpPercent=(hp-best['total'])/hp if hp>0 else None)

def impact(x,c,s):
    power=x*s['q']/c
    baseline=s['q']*s['efGas']
    emissions=power*s['efElectric']+(1-x)*baseline
    return dict(emissions=emissions,reduction=baseline-emissions,
                power=power,fleetPower=power*3.5)
