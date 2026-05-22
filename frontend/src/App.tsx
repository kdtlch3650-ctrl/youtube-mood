import { useState } from 'react'
import './App.css'

type AnalyzeResult = {
  input_text: string
  emotions: string[]
  mood_tags: string[]
  search_keywords: string[]
  recommended_tracks: RecommendationItem[]
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
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const isResultView = Boolean(analysisResult)
  const recommendedTracks = analysisResult?.recommended_tracks ?? []
  const activeTrack =
    recommendedTracks.find((track) => track.id === selectedTrackId) ?? recommendedTracks[0]
  const moodHighlights = [
    ...(analysisResult?.emotions ?? []),
    ...(analysisResult?.mood_tags ?? []),
  ].slice(0, 4)

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
      setSelectedTrackId(result.recommended_tracks[0]?.id ?? null)
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
    setSelectedTrackId(null)
  }

  return (
    <main className="app-shell">
      {!isResultView ? (
        <section className="start-screen" aria-labelledby="service-title">
          <div className="start-card">
            <p className="eyebrow">Mood based music recommendation</p>
            <h1 id="service-title">오늘의 감정에 맞는 음악을 찾습니다</h1>
            <p className="intro-copy">
              감정이나 상황을 문장으로 입력하면 분위기 태그를 분석하고, 어울리는 곡과
              플레이리스트를 추천합니다.
            </p>

            <form className="mood-form" onSubmit={handleSubmit}>
              <label htmlFor="mood-input">지금 상태를 문장으로 입력하세요</label>
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
          </div>
        </section>
      ) : (
        <section className="music-dashboard" aria-labelledby="result-title">
          <aside className="dashboard-sidebar">
            <p className="sidebar-logo">Moodify</p>
            <nav className="recommendation-tabs" aria-label="추천 유형">
              <button
                type="button"
                className={selectedTab === 'track' ? 'active' : ''}
                onClick={() => setSelectedTab('track')}
              >
                <span>▮▮</span>
                추천 곡
              </button>
              <button
                type="button"
                className={selectedTab === 'playlist' ? 'active' : ''}
                onClick={() => setSelectedTab('playlist')}
              >
                <span>♪</span>
                플레이리스트
              </button>
            </nav>
            <button type="button" className="reset-link" onClick={handleReset}>
              다시 입력하기
            </button>
          </aside>

          <section className="dashboard-main">
            <section className="recommendation-area" aria-label="추천 음악 결과">
              <h1 id="result-title">{selectedTab === 'track' ? 'Explore new' : 'Playlists'}</h1>
              {selectedTab === 'track' ? (
                <div className="track-grid">
                  {recommendedTracks.map((track) => (
                    <button
                      type="button"
                      className={`track-card ${activeTrack?.id === track.id ? 'active' : ''}`}
                      key={track.id}
                      onClick={() => setSelectedTrackId(track.id)}
                    >
                      {track.thumbnail_url && <img src={track.thumbnail_url} alt="" />}
                      <h3>{track.title}</h3>
                      <p>{track.channel_title}</p>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="playlist-grid">
                  {analysisResult?.recommended_playlists.map((playlist, index) => (
                    <article className="playlist-row" key={playlist.id}>
                      {playlist.thumbnail_url ? (
                        <img src={playlist.thumbnail_url} alt="" className="row-thumbnail" />
                      ) : (
                        <span className="row-index">{index + 1}</span>
                      )}
                      <div>
                        <h3>{playlist.title}</h3>
                        <p>{playlist.channel_title}</p>
                      </div>
                      <a href={playlist.url} className="row-link" target="_blank" rel="noreferrer">
                        열기
                      </a>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <div className="detail-grid">
              <section className="selected-track-section" aria-label="선택한 대표곡">
                <h2>Popular</h2>
                <article className="selected-track-card">
                  {activeTrack?.thumbnail_url && (
                    <img src={activeTrack.thumbnail_url} alt="" className="selected-track-image" />
                  )}
                  <div>
                    <p className="card-type">Selected track</p>
                    <h3>{activeTrack?.title}</h3>
                    <p className="channel-name">{activeTrack?.channel_title}</p>
                    <p>{activeTrack?.reason}</p>
                    <a href={activeTrack?.url} className="youtube-link" target="_blank" rel="noreferrer">
                      YouTube에서 열기
                    </a>
                  </div>
                </article>
              </section>
              <section className="mood-panel" aria-label="감정 분석 결과">
                <h2>Mood</h2>
                {moodHighlights.map((tag) => (
                  <div className="mood-card" key={tag}>
                    <strong>{tag}</strong>
                  </div>
                ))}
              </section>
            </div>

            <footer className="player-bar">
              <span className="play-button">▶</span>
              {activeTrack?.thumbnail_url && <img src={activeTrack.thumbnail_url} alt="" />}
              <div>
                <p>{activeTrack?.title}</p>
                <span>{activeTrack?.channel_title}</span>
              </div>
              <a href={activeTrack?.url} target="_blank" rel="noreferrer">
                YouTube
              </a>
            </footer>
          </section>
        </section>
      )}
    </main>
  )
}

export default App
