# 히트펌프·가스보일러 최적운영 계산기 — Streamlit

기존 웹 계산기 게시 버전 5의 계산식을 Python으로 변환한 앱입니다.
누진제·일반용·계절시간별 최적운전, 가스 단독 비용, HP 100% 대비 절감률,
온실가스 감축량, 350만대 전력사용량, 직접 혼합비율 비교 및 CSV 다운로드를 제공합니다.

## Streamlit Community Cloud 배포

1. ZIP 압축을 풉니다.
2. GitHub에서 저장소를 생성합니다. 예: hybrid-heat-calculator.
3. 이 폴더 안의 파일들을 저장소 루트에 업로드하고 커밋합니다.
   - streamlit_app.py
   - model.py
   - cop_data.json
   - requirements.txt
   - .streamlit/config.toml (테마 설정, 선택)
   - README.md, .gitignore, test_model.py
4. https://share.streamlit.io/ 에서 로그인하고 GitHub 저장소를 연결합니다.
5. Create app → Yup, I have an app을 선택합니다.
6. Repository에 업로드한 저장소, Branch에 실제 브랜치(보통 main),
   Main file path에 streamlit_app.py를 입력합니다.
7. Advanced settings에서 Python 3.12를 선택하고 Deploy를 누릅니다.

API 키나 Secrets는 필요하지 않습니다. .streamlit/config.toml이 누락되어도 기본 테마로 실행됩니다.
ZIP 자체를 저장소에 올리지 말고 압축을 푼 파일을 올리세요.
하위 폴더에 올렸다면 Main file path도 해당 폴더/streamlit_app.py로 지정해야 합니다.
배포 후 앱 접근권한을 의도한 공개 범위로 설정하세요.

공식 안내: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## PC에서 실행

Python 3.12를 설치한 후 이 폴더에서 실행합니다.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

macOS/Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

터미널에 표시되는 Local URL로 접속합니다. 종료는 Ctrl+C입니다.

## 파일 역할

| 파일 | 역할 |
|---|---|
| streamlit_app.py | 입력, 결과 카드, Plotly 그래프, CSV·JSON 다운로드 |
| model.py | 기존 계산기의 목적함수와 최적화 로직 |
| cop_data.json | 외기온도 −20~20℃의 기존 COP 데이터 |
| requirements.txt | 검증한 Python 라이브러리 버전 |
| .streamlit/config.toml | 테마 색상 |
| test_model.py | 재현 가능한 계산 검증 |

## 기본값

기존 웹 기본값: 월 열수요 1,143.34kWh열, 기저전력 226.1kWh, 계약전력 10kW,
계절시간별 전력비중 40/10/50%, HP 미사용 월 기본요금 회피.
‘업로드 엑셀 v3 조건 적용’은 전력비중을 40/40/20%, 기본요금을 계속 납부하는 조건으로 설정합니다.
두 버튼은 요금·열수요·배출계수를 함께 초기화합니다.

## 계산과 한계

- HP 전력 = xQ/COP, 가스 난방비 = (1−x)Qg.
- 누진제는 기저전력 청구액을 차감한 난방 증가분을 계산합니다.
- 일반용·계절시간별은 HP 별도계약을 가정합니다.
- 누진제의 0%, 100%, 누진 경계 후보를 비교해 연속 최적비율을 구합니다.
- 일반용·계절시간별은 선형 변동비 조건에서 0%, 100% 비용을 비교합니다.
- 계절시간별 비중은 전력량 비중이며 시간별 최적 스케줄을 구하는 모델은 아닙니다.
- 가스 유효 열단가·배출계수는 기존 파일과 동일하게 사용하며 별도 효율 보정을 추가하지 않았습니다.
- 세금·기금·설비비·보조금·축열조·용량제약·연간 기상 가중은 별도로 반영하지 않았습니다.
- COP 선형 보정과 시험자료 산점도는 미반영이며 기존 COP 표를 사용합니다.
- 입력 요금은 분석 시나리오이며 최신 공식 요금이나 실제 계약 적용 가능성을 보장하지 않습니다.
- 입력은 세션별로 처리되고 앱에 영구 저장되지 않습니다. 필요한 조건은 JSON으로 다운로드하세요.
- 이 패키지를 제공한 것과 실제 GitHub·Streamlit 계정에 배포한 것은 구분됩니다. 클라우드 배포는 아직 수행하지 않았습니다.

## 검증

기존 JavaScript와 3개 조건 × 41개 온도 × 3개 요금제 = 369개 결과를 대조했습니다.
최대 수치 차이는 약 2.91×10⁻¹¹로 부동소수점 오차 수준입니다.
계산 검증 재실행: python -m unittest test_model.py

원본: 기존 웹 계산기 버전 5, 커밋 a04ab21e7e13396d63752c29deb56035c5c4146e.
별도 오픈소스 라이선스는 지정하지 않았습니다.
