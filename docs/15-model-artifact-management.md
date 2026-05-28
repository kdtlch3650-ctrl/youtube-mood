# 모델 산출물 관리

## 1. 문서 목적

이 문서는 학습된 AI 모델 파일을 GitHub에 직접 올리지 않는 이유와, 모델이 없을 때 프로젝트가 어떻게 동작하는지 정리한다.

이 프로젝트는 AI 모델을 직접 학습하지만, 학습된 모델 파일은 코드 저장소가 아니라 로컬 또는 별도 저장소에서 관리한다.

## 2. 모델 파일을 Git에 포함하지 않는 이유

학습된 모델 파일은 크기가 크다.

현재 로컬 모델의 대표 파일은 아래와 같다.

```text
ml/models/grouped-mood-roberta-small/model.safetensors
ml/models/mood-roberta-small/model.safetensors
```

각 모델 가중치 파일은 약 270MB 수준이다.

이 파일을 GitHub 저장소에 직접 올리면 아래 문제가 생긴다.

- 저장소 용량이 커진다.
- clone과 pull 시간이 길어진다.
- 코드 변경 이력과 모델 바이너리 이력이 섞인다.
- GitHub 일반 저장소에서 대용량 모델 파일을 관리하기 어렵다.

따라서 모델 파일은 Git에 포함하지 않는다.

## 3. 현재 Git 관리 기준

`.gitignore`에서 모델 산출물을 제외한다.

```gitignore
ml/models/*
!ml/models/.gitkeep
```

의미:

- `ml/models/` 아래 실제 모델 파일은 Git에서 제외한다.
- `ml/models/.gitkeep`만 남겨 폴더 구조를 유지한다.

Git에 포함하는 것:

- 학습 코드
- 평가 코드
- 모델 연결 코드
- 문서
- 라벨 기준
- 테스트 케이스

Git에 포함하지 않는 것:

- 학습된 모델 가중치
- 체크포인트
- optimizer 상태 파일
- 원본 학습 데이터
- 변환된 대용량 학습 데이터

## 4. 백엔드 모델 로딩 흐름

백엔드는 실행 시 로컬 모델 파일이 있는지 확인한다.

현재 우선순위는 아래와 같다.

```text
1. ml/models/grouped-mood-roberta-small/
2. ml/models/mood-roberta-small/
3. 규칙 기반 fallback 모델
```

즉, 그룹 라벨 모델이 있으면 먼저 사용한다.

그룹 라벨 모델이 없고 기존 KOTE 모델이 있으면 기존 모델을 사용한다.

둘 다 없거나 모델 의존성이 부족하면 규칙 기반 fallback 모델을 사용한다.

## 5. fallback 모델의 의미

fallback 모델은 학습된 AI 모델이 없을 때 서비스가 완전히 멈추지 않도록 하는 안전장치다.

예를 들어 다른 사람이 GitHub에서 프로젝트를 clone하면 모델 파일은 포함되어 있지 않다.

이 경우에도 백엔드는 실행 가능해야 한다.

fallback 모델은 키워드 기반으로 감정과 분위기를 대략 추론한다.

예:

```text
불안, 걱정 → anxious, soft, quiet
지쳤, 피곤 → tired, soft, quiet
집중 → focused, minimal, quiet
```

다만 fallback은 학습 모델보다 표현 이해 범위가 좁다.

따라서 실제 AI 모델 기반 결과를 확인하려면 학습된 모델 파일이 필요하다.

## 6. 학습된 모델을 백엔드에서 사용하려면

학습이 끝난 모델 폴더를 아래 위치에 둔다.

```text
ml/models/grouped-mood-roberta-small/
```

필요한 대표 파일:

```text
config.json
labels.json
model.safetensors
tokenizer.json
tokenizer_config.json
```

백엔드 실행 환경에는 추론에 필요한 라이브러리가 설치되어 있어야 한다.

예:

```text
torch
transformers
```

모델 폴더가 있고 의존성도 설치되어 있으면 백엔드는 학습된 모델을 사용한다.

## 7. 모델을 다시 학습하는 방법

학습 작업은 백엔드 실행 환경과 분리된 `ml/` 환경에서 진행한다.

예시:

```powershell
ml\.venv\Scripts\python.exe ml\train_grouped.py
```

학습 결과는 아래 위치에 저장한다.

```text
ml/models/grouped-mood-roberta-small/
```

학습과 평가 방법은 [ml/README.md](../ml/README.md)에 정리한다.

## 8. 모델 관리 방식 요약

이 프로젝트는 모델 가중치 파일을 코드 저장소에 포함하지 않는다.

모델 가중치는 대용량 산출물이기 때문에 로컬 또는 별도 저장소에서 관리한다.

대신 저장소에는 아래 내용을 남긴다.

- 학습 코드
- 평가 코드
- 모델 연결 방식
- fallback 구조
- 테스트 케이스
- 모델 사용 방법

이 구조를 통해 모델 파일이 없어도 프로젝트 구조와 실행 흐름을 이해할 수 있고, 필요한 경우 모델을 다시 학습해 같은 위치에 배치할 수 있다.

## 9. 이후 개선 방향

배포 단계에서는 모델 파일을 별도 저장소에 올릴 수 있다.

후보:

- Hugging Face Hub
- 클라우드 스토리지
- 배포 서버의 파일 시스템
- GitHub Release

현재 단계에서는 로컬 모델 관리와 문서화로 충분하다.
