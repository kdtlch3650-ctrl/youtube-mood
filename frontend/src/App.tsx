import { useState } from 'react'
import './App.css'

type AnalyzeResult = {
  input_text: string
  emotions: string[]
  mood_tags: string[]
  search_keywords: string[]
  recommended_track: RecommendationItem
  recommended_playlists: RecommendationItem[]
}

type RecommendationTab = 'track' | 'playlist'

type RecommendationItem = {
  id: string
  title: string
  channel_title: string
  url: string
  thumbnail_url: string
  reason: string
}

function App() {
  const [inputText, setInputText] = useState('')
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null)
  const [selectedTab, setSelectedTab] = useState<RecommendationTab>('track')
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const isResultView = Boolean(analysisResult)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const trimmedText = inputText.trim()
    if (!trimmedText) {
      return
    }

    setIsLoading(true)
    setErrorMessage('')

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: trimmedText }),
      })

      if (!response.ok) {
        throw new Error('분석 요청에 실패했습니다.')
      }

      const result: AnalyzeResult = await response.json()
      setAnalysisResult(result)
    } catch {
      setErrorMessage('분석 결과를 불러오지 못했습니다. 백엔드 서버를 확인해 주세요.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setAnalysisResult(null)
    setErrorMessage('')
    setSelectedTab('track')
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
                {isLoading ? '분석 중...' : '음악 추천 받기'}
              </button>
              {errorMessage && <p className="error-message">{errorMessage}</p>}
            </form>
          </section>
        </>
      ) : (
        <section className="result-section" aria-labelledby="result-title">
          <p className="eyebrow">Recommendation result</p>
          <h1 id="result-title">추천 결과</h1>

          <div className="result-layout">
            <aside className="result-sidebar" aria-label="분석 요약과 추천 유형 선택">
              <div>
                <p className="result-label">입력 문장</p>
                <p className="submitted-text">{analysisResult?.input_text}</p>
              </div>
              <div>
                <p className="result-label">감정</p>
                <ul className="tag-list">
                  {analysisResult?.emotions.map((emotion) => (
                    <li key={emotion}>{emotion}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="result-label">분위기 태그</p>
                <ul className="tag-list">
                  {analysisResult?.mood_tags.map((tag) => (
                    <li key={tag}>{tag}</li>
                  ))}
                </ul>
              </div>
              <nav className="recommendation-tabs" aria-label="추천 유형">
                <button
                  type="button"
                  className={selectedTab === 'track' ? 'active' : ''}
                  onClick={() => setSelectedTab('track')}
                >
                  한 곡 추천
                </button>
                <button
                  type="button"
                  className={selectedTab === 'playlist' ? 'active' : ''}
                  onClick={() => setSelectedTab('playlist')}
                >
                  플레이리스트
                </button>
              </nav>
              <button type="button" className="secondary-button" onClick={handleReset}>
                다시 입력하기
              </button>
            </aside>

            <section className="recommendation-panel" aria-label="추천 음악 결과">
              {selectedTab === 'track' ? (
                <article className="recommendation-card featured-card">
                  {analysisResult?.recommended_track.thumbnail_url && (
                    <img
                      src={analysisResult.recommended_track.thumbnail_url}
                      alt=""
                      className="recommendation-thumbnail"
                    />
                  )}
                  <p className="card-type">한 곡 추천</p>
                  <h2>{analysisResult?.recommended_track.title}</h2>
                  <p className="channel-name">{analysisResult?.recommended_track.channel_title}</p>
                  <p>{analysisResult?.recommended_track.reason}</p>
                  <a
                    href={analysisResult?.recommended_track.url}
                    className="youtube-link"
                    target="_blank"
                    rel="noreferrer"
                  >
                    YouTube에서 열기
                  </a>
                </article>
              ) : (
                <div className="playlist-grid">
                  {analysisResult?.recommended_playlists.map((playlist) => (
                    <article className="recommendation-card" key={playlist.id}>
                      {playlist.thumbnail_url && (
                        <img src={playlist.thumbnail_url} alt="" className="recommendation-thumbnail" />
                      )}
                      <p className="card-type">플레이리스트</p>
                      <h2>{playlist.title}</h2>
                      <p className="channel-name">{playlist.channel_title}</p>
                      <p>{playlist.reason}</p>
                      <a href={playlist.url} className="youtube-link" target="_blank" rel="noreferrer">
                        YouTube에서 열기
                      </a>
                    </article>
                  ))}
                </div>
              )}

              <div className="keyword-box">
                <p className="result-label">검색 키워드</p>
                <ul className="keyword-list">
                  {analysisResult?.search_keywords.map((keyword) => (
                    <li key={keyword}>{keyword}</li>
                  ))}
                </ul>
              </div>
            </section>
          </div>
        </section>
      )}
    </main>
  )
}

export default App
