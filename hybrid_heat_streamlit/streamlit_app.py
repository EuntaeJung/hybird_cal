import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from model import DEFAULTS, COP, NAMES, validate, rate, cost, optimum, impact

st.set_page_config(page_title='히트펌프·가스보일러 최적운영 계산기', page_icon='🏠', layout='wide')
COLORS=['#087f80','#b57717','#7561b3']
for key,value in DEFAULTS.items():
    st.session_state.setdefault(key,value)

def preset(excel=False):
    st.session_state.update(DEFAULTS)
    if excel:
        st.session_state.update(w2=40.,w3=20.,keep=True)

def fields(items):
    for key,label in items:
        st.number_input(label,min_value=0.,step=.1,format='%.4f',key=key)

with st.sidebar:
    st.title('운전·요금 설정')
    st.button('기존 웹 기본값 복원',on_click=preset,width='stretch')
    st.button('업로드 엑셀 v3 조건 적용',on_click=preset,args=(True,),width='stretch')
    st.caption('엑셀 조건: 10kW · 기본요금 유지 · 전력비중 40/40/20%. 버튼은 요금·열수요·배출계수를 함께 초기화합니다.')
    temp=st.slider('외기온도 (℃)',-20,20,0)
    st.metric('COP',f'{COP[temp]:.3f}')
    fields([('q','월 열수요 (kWh열)'),('g','가스 유효 열단가 (원/kWh열)')])
    st.checkbox('HP 미사용 월에도 기본요금 계속 납부',key='keep')
    with st.expander('누진제 · 기저전력',expanded=True):
        fields([('b','기저전력 (kWh/월)'),('l1','1단계 상한 (kWh)'),('l2','2단계 상한 (kWh)'),('p1','1단계 (원/kWh)'),('p2','2단계 (원/kWh)'),('p3','3단계 (원/kWh)')])
    with st.expander('일반용'):
        fields([('kw','일반용 계약전력 (kW)'),('f','일반용 기본요금 (원/kW·월)'),('p','일반용 전력량요금 (원/kWh)')])
    with st.expander('계절시간별 · 겨울철'):
        fields([('kw2','계시별 계약전력 (kW)'),('f2','계시별 기본요금 (원/kW·월)'),('off','경부하 (원/kWh)'),('mid','중간부하 (원/kWh)'),('peak','최대부하 (원/kWh)'),('w1','경부하 전력비중 (%)'),('w2','중간부하 전력비중 (%)'),('w3','최대부하 전력비중 (%)')])
        st.caption('시간비중이 아닌 전력량 비중입니다. 경부하 22~08시 / 중간 08~16시 / 최대 16~22시 가정.')
    with st.expander('온실가스 배출계수'):
        fields([('efElectric','전력 (kgCO₂eq/kWh)'),('efGas','가스 (kgCO₂eq/kWh)')])

s={k:st.session_state[k] for k in DEFAULTS}
st.title('히트펌프 & 가스보일러 최적운영 조합 탐색')
st.caption('운영비 최소화 · 누진제 / 일반용 / 계절시간별 비교')
try:
    validate(s)
except ValueError as e:
    st.error(str(e))
    st.stop()

st.metric('가스보일러 단독 사용요금',f"{s['q']*s['g']:,.0f} 원/월")
st.caption('월 열수요 × 가스 유효 열단가. HP 전기 기본요금과 가구 기저전력 요금 제외.')
results=[optimum(k,temp,s) for k in range(3)]
for k,col in enumerate(st.columns(3)):
    r=results[k]
    with col:
        st.subheader(NAMES[k])
        st.metric('최적 월 난방비',f"{r['total']:,.0f} 원")
        st.write(f"**HP {r['x']:.1%} / 가스 {1-r['x']:.1%}**")
        st.write(f"HP 100% 비용: {r['hpOnly']:,.0f}원")
        percent='산정 불가' if r['hpPercent'] is None else f"{r['hpPercent']:.2%}"
        st.write(f"HP 100% 대비 **{r['hpSaving']:,.0f}원 절감 ({percent})**")
        label='기본요금 유지·가스 운전 기준' if k>0 and s['keep'] else '가스 단독'
        st.caption(f"{label} 대비 {r['saving']:,.0f}원 절감 ({r['percent']:.2%})")
        m=impact(r['x'],r['c'],s)
        st.write(f"HP 전력: {r['power']:,.1f} kWh/월")
        st.write(f"전기요금: {r['elec']:,.0f}원 · 가스요금: {r['gas']:,.0f}원")
        st.write(f"온실가스 감축: {m['reduction']:,.2f} kgCO₂eq/가구·월")
        st.write(f"350만대 HP 전력: {m['fleetPower']:,.2f} GWh/월")

st.info(f"계절시간별 가중평균 전력단가: {rate(s):.2f}원/kWh. 온실가스 감축량은 가스 단독 대비이며 음수는 배출 증가입니다.")
records=[]
for t in range(-20,21):
    for k,name in enumerate(NAMES):
        r=optimum(k,t,s);m=impact(r['x'],r['c'],s)
        records.append({'외기온도(℃)':t,'COP':r['c'],'요금제':name,
          '최적 HP 비율(%)':r['x']*100,'가스 비율(%)':(1-r['x'])*100,
          '월 난방비(원)':r['total'],'HP100 비용(원)':r['hpOnly'],
          'HP100 대비 절감액(원)':r['hpSaving'],
          'HP100 대비 절감률(%)':None if r['hpPercent'] is None else r['hpPercent']*100,
          'HP 전력(kWh/월)':r['power'],'전기요금(원)':r['elec'],'가스요금(원)':r['gas'],
          '온실가스 감축(kgCO2eq/가구월)':m['reduction'],'350만대 전력(GWh/월)':m['fleetPower']})
df=pd.DataFrame(records)

st.subheader('외기온도별 요금제 비교')
mode=st.radio('그래프 선택',['최적 HP 비율(%)','월 난방비(원)','HP100 대비 절감률(%)'],horizontal=True)
fig=go.Figure()
for k,name in enumerate(NAMES):
    d=df[df['요금제']==name]
    fig.add_trace(go.Scatter(x=d['외기온도(℃)'],y=d[mode],name=name,mode='lines',
      line=dict(color=COLORS[k],width=4 if k==1 else 2.5,dash='dash' if k==2 else 'solid'),
      hovertemplate='%{x}℃ · %{y:,.2f}<extra>%{fullData.name}</extra>'))
if mode=='월 난방비(원)':
    fig.add_trace(go.Scatter(x=[-20,20],y=[s['q']*s['g']]*2,name='가스보일러 단독',line=dict(color='#c4473a',dash='dash')))
fig.add_vline(x=temp,line_dash='dot',line_color='gray')
fig.update_layout(xaxis_title='외기온도 (℃)',yaxis_title=mode,legend=dict(orientation='h',y=1.15),height=430,template='plotly_white')
st.plotly_chart(fig,width='stretch')
st.caption('절감률 = (동일 요금제 HP 100% 비용 − 최적비용) ÷ HP 100% 비용. 기준 비용이 0원이면 미표시. 0% 선은 겹칠 수 있습니다.')

st.subheader('직접 혼합비율 비교')
manual=st.slider('HP 열공급비율 (%)',0,100,50)
rows=[]
for k,name in enumerate(NAMES):
    r=cost(k,manual/100,COP[temp],s)
    rows.append({'요금제':name,'선택비율 비용(원)':r['total'],'최적비용(원)':results[k]['total'],'최적 대비 추가비용(원)':max(0,r['total']-results[k]['total'])})
st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
ratios=[]
for i in range(0,101,10):
    m=impact(i/100,COP[temp],s)
    ratios.append({'HP 비율(%)':i,'가스 비율(%)':100-i,'HP 전력(kWh/월)':m['power'],'온실가스 감축(kgCO2eq/가구월)':m['reduction'],'350만대 전력(GWh/월)':m['fleetPower']})
ratio_df=pd.DataFrame(ratios)
with st.expander('사용비율별 온실가스·전력 및 온도별 상세 결과'):
    st.dataframe(ratio_df,hide_index=True,width='stretch')
    st.dataframe(df,hide_index=True,width='stretch')
st.download_button('온도별 최적운전 CSV 다운로드',df.to_csv(index=False).encode('utf-8-sig'),'최적운전_결과.csv','text/csv')
st.download_button('현재 온도 사용비율별 CSV 다운로드',ratio_df.to_csv(index=False).encode('utf-8-sig'),'사용비율별_결과.csv','text/csv')
st.download_button('입력조건 JSON 다운로드',json.dumps(dict(s,temp=temp,manual=manual),ensure_ascii=False,indent=2),'입력조건.json','application/json')

with st.expander('계산식·자료 출처·적용 범위'):
    st.markdown('''
**x**: HP 열공급비율, **Q**: 월 열수요, **c**: COP, **B**: 기저전력, **g**: 가스 유효 열단가.

- HP 전력 = xQ/c; 가스 난방비 = (1−x)Qg.
- 누진제 = bill(B+xQ/c)−bill(B)+(1−x)Qg.
- 일반용·계절시간별 = 적용 기본요금 + p·xQ/c + (1−x)Qg.
- 누진제는 양 끝점과 누진 경계 후보를 비교합니다. 나머지는 선형 변동비 조건에서 양 끝점을 비교합니다.
- 기본요금 유지 선택 시 HP 0%에도 기본요금을 포함합니다. 순간 정지에 따른 요금 면제를 의미하지 않습니다.
- 동률은 가스 비율이 높은 조합을 표시합니다.
- 감축량 = Q×가스배출계수 − [xQ/c×전력배출계수 + (1−x)Q×가스배출계수]. 원자료처럼 별도 보일러 효율 보정은 하지 않습니다.
- 350만대 전력 = xQ/c × 3,500,000 ÷ 1,000,000 (GWh/월).

**출처:** 기존 웹 계산기 게시 버전 5의 계산식·COP 표. 업로드 요금 자료를 사용하는 시나리오이며 최신 공식 요금과 적용 자격을 검증한 결과가 아닙니다.
누진제는 기저전력 요금을 차감한 난방 증가분, 다른 요금제는 HP 별도계약을 가정합니다.
전기 부가세·기금, 설비비·보조금은 추가하지 않았습니다.
월 열수요는 온도별로 일정하며, 시간별 최적 스케줄·제상·용량제약·축열조 모델은 포함하지 않습니다.
COP 선형 보정·시험값 산점도는 아직 반영되지 않은 기존 COP 모델입니다.
350만대 모두 동일한 열수요·온도·HP 비율을 가정합니다. 기저전력은 HP 전력량에 포함하지 않습니다.
''')
