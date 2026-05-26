# ML 학습 작업 공간

이 폴더는 감정 분석 모델을 학습하기 위한 파일을 모아두는 공간이다.

백엔드의 `backend/app/ai/`는 서비스 실행용 코드이고, 이 `ml/` 폴더는 모델을 학습하고 결과물을 준비하는 용도다.

## 1. 목표

사용자 자연어 문장을 입력받아 KOTE 감정 라벨을 예측하는 모델을 만든다.

`mood_tags`는 모델이 직접 예측하지 않는다.
서비스 백엔드에서 감정 라벨을 음악 추천용 분위기 태그로 변환한다.

1차 학습 모델은 `klue/roberta-small`을 사용한다.

## 2. 기본 구조

```text
ml/
  README.md
  data-labeling-guide.md
  prepare_kote.py
  train.py
  data/
    raw/
      .gitkeep
    kote_training_data.jsonl
    sample_training_data.jsonl
  models/
    .gitkeep
```

## 3. 학습 데이터 형식

학습 데이터는 JSON Lines 형식으로 관리한다.

한 줄이 하나의 학습 예시다.

```json
{"text":"오늘 너무 지치고 아무것도 하기 싫다","labels":["힘듦/지침","귀찮음"]}
```

KOTE 데이터셋을 사용할 때는 원본 감정 라벨을 우선 유지한다.
감정 라벨을 음악 추천용 분위기로 바꾸는 기준은 `data-labeling-guide.md`에 정리한다.

## 4. 앞으로 추가할 파일

실제 학습 단계에서는 아래 파일을 사용한다.

- `prepare_kote.py`: KOTE 원본 TSV를 JSONL 학습 데이터로 변환하는 스크립트
- `train.py`: 모델 학습 스크립트 초안
- `evaluate.py`: 검증 데이터 평가 스크립트
- `predict_sample.py`: 학습된 모델로 샘플 문장을 테스트하는 스크립트

## 5. KOTE 데이터 준비 흐름

KOTE 원본 TSV 파일은 Git에 직접 포함하지 않고 `ml/data/raw/` 폴더에 둔다.

예상 파일명:

- `train.tsv`
- `val.tsv`
- `test.tsv`

아래 명령으로 학습용 JSONL 파일을 만든다.

```bash
python ml/prepare_kote.py
```

생성 결과:

```text
ml/data/kote_training_data.jsonl
```

## 6. 학습 스크립트 흐름

`train.py`는 아래 순서로 동작한다.

- `kote_training_data.jsonl` 파일을 읽는다.
- 감정 라벨 목록을 정리한다.
- 한 문장에 여러 라벨이 붙을 수 있도록 멀티라벨 형식으로 변환한다.
- `klue/roberta-small` 토크나이저와 모델을 불러온다.
- 학습이 끝나면 모델과 라벨 목록을 `ml/models/mood-roberta-small/`에 저장한다.

## 7. 학습 의존성

1차 학습에 필요한 라이브러리는 `ml/requirements.txt`에 따로 관리한다.

- `torch`: 모델 학습과 추론에 사용한다.
- `transformers`: `klue/roberta-small` 모델과 토크나이저를 불러온다.
- `scikit-learn`: 학습/검증 데이터 분리와 평가 지표 계산에 사용한다.

설치는 실제 학습 스크립트를 만들기 전에 진행한다.

## 8. 주의할 점

- 학습용 코드는 백엔드 실행 코드와 분리한다.
- KOTE 원본 TSV와 변환된 JSONL은 재생성 가능한 데이터이므로 Git에 포함하지 않는다.
- 학습된 모델 파일은 크기가 커질 수 있으므로 Git에 바로 올릴지 따로 판단한다.
- 새 라이브러리 설치가 필요하면 먼저 목적과 영향을 확인한 뒤 추가한다.
