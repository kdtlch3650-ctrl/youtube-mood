import { useState } from 'react'
import './App.css'

const sampleTags = ['calm', 'warm', 'late-night']

function App() {
  const [inputText, setInputText] = useState('')
  const [submittedText, setSubmittedText] = useState('')
  const isResultView = Boolean(submittedText)

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmittedText(inputText.trim())
  }

  const handleReset = () => {
    setSubmittedText('')
  }

  return (
    <main className="app-shell">
      {!isResultView ? (
        <>
          <section className="intro-section" aria-labelledby="service-title">
            <p className="eyebrow">Mood based music recommendation</p>
            <h1 id="service-title">감정 기반 음악 추천</h1>
            <p className="intro-copy">
              지금 느끼는 감정이나 상황을 문장으로 입력하면, 어울리는 음악과
              플레이리스트를 추천하는 서비스입니다.
            </p>
          </section>

          <section className="input-section" aria-labelledby="input-title">
            <h2 id="input-title">현재 기분 입력</h2>
            <form className="mood-form" onSubmit={handleSubmit}>
              <label htmlFor="mood-input">감정이나 상황</label>
              <textarea
                id="mood-input"
                value={inputText}
                onChange={(event) => setInputText(event.target.value)}
                placeholder="예: 오늘은 지쳤지만 너무 무거운 음악은 듣고 싶지 않아"
                rows={5}
              />
              <button type="submit" disabled={!inputText.trim()}>
                음악 추천 받기
              </button>
            </form>
          </section>
        </>
      ) : (
        <section className="result-section" aria-labelledby="result-title">
          <p className="eyebrow">Recommendation result</p>
          <h1 id="result-title">추천 결과</h1>

          <div className="result-content">
            <div>
              <p className="result-label">입력 문장</p>
              <p className="submitted-text">{submittedText}</p>
            </div>
            <div>
              <p className="result-label">분위기 태그 예시</p>
              <ul className="tag-list">
                {sampleTags.map((tag) => (
                  <li key={tag}>{tag}</li>
                ))}
              </ul>
            </div>
            <p className="placeholder-text">
              다음 단계에서 백엔드 분석 API와 연결해 실제 감정 결과를 표시합니다.
            </p>
            <button type="button" className="secondary-button" onClick={handleReset}>
              다시 입력하기
            </button>
          </div>
        </section>
      )}
    </main>
  )
}

export default App
