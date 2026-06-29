import { useEffect, useRef, useState, type MouseEvent } from 'react'
import './App.css'

type AnalyzeResult = {
  input_text: string
  emotion_text?: string
  request_text?: string
  emotions: string[]
  mood_tags: string[]
  genre?: string | null
  search_keywords: string[]
  request_keywords?: string[]
  blocked_mood_tags?: string[]
  has_avoidance?: boolean
  has_negation?: boolean
  recommended_tracks: RecommendationItem[]
  recommended_playlists: RecommendationItem[]
}

type SearchRecordItem = {
  id: string
  title: string
  channel_title: string
  url: string
  thumbnail_url: string
  reason?: string
  playlist_tracks?: PlaylistTrackItem[]
}

type SearchRecord = {
  id: string
  created_at: string
  input_text: string
  emotion_text?: string
  request_text?: string
  search_scope: SearchScope
  emotions: string[]
  mood_tags: string[]
  genre?: string | null
  search_keywords: string[]
  request_keywords?: string[]
  blocked_mood_tags?: string[]
  has_avoidance?: boolean
  has_negation?: boolean
  recommended_tracks: SearchRecordItem[]
  recommended_playlists: SearchRecordItem[]
}

type SearchScope = 'all' | 'korean'

type RecommendationTab = 'track' | 'playlist'
type ScreenMode = 'search' | 'history'
type KeywordTooltipState = {
  label: string
  top: number
  left: number
  value: string
} | null

type AuthSession = {
  accessToken: string
  idToken: string
  expiresAt: number
  user: {
    email?: string
    name?: string
    picture?: string
    sub?: string
  }
}

type PlaylistTrackItem = {
  title: string
  thumbnail_url: string
  url: string
  video_id: string
}

type RecommendationItem = {
  id: string
  title: string
  channel_title: string
  url: string
  thumbnail_url: string
  reason?: string
  playlist_tracks?: PlaylistTrackItem[]
}

type YouTubePlayer = {
  destroy: () => void
  getCurrentTime: () => number
  getDuration: () => number
  loadVideoById: (videoId: string) => void
  pauseVideo: () => void
  playVideo: () => void
  seekTo: (seconds: number, allowSeekAhead: boolean) => void
}

type YouTubePlayerEvent = {
  data: number
}

type YouTubePlayerOptions = {
  events: {
    onStateChange: (event: YouTubePlayerEvent) => void
  }
  height: string
  playerVars: {
    autoplay: number
    playsinline: number
  }
  videoId?: string
  width: string
}

type YouTubeApi = {
  Player: new (elementId: string, options: YouTubePlayerOptions) => YouTubePlayer
  PlayerState: {
    ENDED: number
    PAUSED: number
    PLAYING: number
  }
}

declare global {
  interface Window {
    YT?: YouTubeApi
    onYouTubeIframeAPIReady?: () => void
  }
}

const samplePlaylistTracks = [
  '첫 번째 추천 트랙',
  '두 번째 추천 트랙',
  '세 번째 추천 트랙',
  '네 번째 추천 트랙',
  '다섯 번째 추천 트랙',
]
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
const COGNITO_DOMAIN = (import.meta.env.VITE_COGNITO_DOMAIN ?? '').replace(/\/$/, '')
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID ?? ''
const COGNITO_REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI ?? window.location.origin
const COGNITO_LOGOUT_URI = import.meta.env.VITE_COGNITO_LOGOUT_URI ?? COGNITO_REDIRECT_URI
const COGNITO_SCOPE = (import.meta.env.VITE_COGNITO_SCOPE ?? 'openid email profile').trim()
const APP_ENV = (import.meta.env.VITE_APP_ENV ?? 'local').trim().toLowerCase()
const ENVIRONMENT_LABEL = APP_ENV === 'prod' || APP_ENV === 'production' ? 'PROD' : 'LOCAL'
const APP_SESSION_STORAGE_KEY = 'youtube-mood-session-id'
const AUTH_SESSION_STORAGE_KEY = 'youtube-mood-auth-session'
const AUTH_PKCE_VERIFIER_KEY = 'youtube-mood-auth-pkce-verifier'
const AUTH_PKCE_STATE_KEY = 'youtube-mood-auth-pkce-state'
const AUTH_PKCE_HANDLED_KEY = 'youtube-mood-auth-pkce-handled'

const YOUTUBE_IFRAME_API_URL = 'https://www.youtube.com/iframe_api'
const YOUTUBE_PLAYER_ELEMENT_ID = 'youtube-player-anchor'

const apiUrl = (path: string) => `${API_BASE_URL}${path}`

const getYoutubeVideoId = (url: string) => {
  try {
    const youtubeUrl = new URL(url)
    if (youtubeUrl.hostname === 'youtu.be') {
      return youtubeUrl.pathname.replace('/', '') || null
    }

    return youtubeUrl.searchParams.get('v')
  } catch {
    return null
  }
}

const formatTime = (seconds: number) => {
  if (!Number.isFinite(seconds) || seconds <= 0) {
    return '0:00'
  }

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)

  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const createAppSessionId = () => {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }

  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

const getOrCreateAppSessionId = () => {
  const storedSessionId = window.localStorage.getItem(APP_SESSION_STORAGE_KEY)
  if (storedSessionId) {
    return storedSessionId
  }

  const sessionId = createAppSessionId()
  window.localStorage.setItem(APP_SESSION_STORAGE_KEY, sessionId)
  return sessionId
}

function App() {
  const trackRailRef = useRef<HTMLDivElement>(null)
  const playlistRailRef = useRef<HTMLDivElement>(null)
  const youtubePlayerRef = useRef<YouTubePlayer | null>(null)
  const loadedVideoIdRef = useRef<string | null>(null)
  const progressTimerRef = useRef<number | null>(null)
  const playlistTrackScrollRef = useRef<HTMLDivElement>(null)
  const playlistTrackItemRefs = useRef<Array<HTMLLIElement | null>>([])
  const progressBarRef = useRef<HTMLDivElement>(null)
  const cardPressStartX = useRef(0)
  const ignoreClickAfterDrag = useRef(false)
  const analysisModalCloseTimerRef = useRef<number | null>(null)
  const progressDragState = useRef({
    isDragging: false,
    wasPlaying: false,
  })
  const playlistDragState = useRef({
    isDragging: false,
    lastTime: 0,
    lastY: 0,
    startY: 0,
    scrollTop: 0,
    velocity: 0,
  })
  const dragState = useRef({
    isDragging: false,
    lastTime: 0,
    lastX: 0,
    startX: 0,
    scrollLeft: 0,
    velocity: 0,
  })
  const [inputText, setInputText] = useState('')
  const [searchScope, setSearchScope] = useState<SearchScope>('all')
  const [screenMode, setScreenMode] = useState<ScreenMode>('search')
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null)
  const [searchRecords, setSearchRecords] = useState<SearchRecord[]>([])
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null)
  const [historySearchText, setHistorySearchText] = useState('')
  const [playlistTracksById, setPlaylistTracksById] = useState<Record<string, PlaylistTrackItem[]>>({})
  const [selectedTab, setSelectedTab] = useState<RecommendationTab>('track')
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null)
  const [selectedPlaylistId, setSelectedPlaylistId] = useState<string | null>(null)
  const [currentPlaylistTrackIndex, setCurrentPlaylistTrackIndex] = useState(0)
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isPlayerActive, setIsPlayerActive] = useState(false)
  const [isYoutubeApiReady, setIsYoutubeApiReady] = useState(() => Boolean(window.YT?.Player))
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [keywordTooltip, setKeywordTooltip] = useState<KeywordTooltipState>(null)
  const [isAnalysisModalOpen, setIsAnalysisModalOpen] = useState(false)
  const [appSessionId] = useState(() => getOrCreateAppSessionId())
  const [authSessionState, setAuthSessionState] = useState<AuthSession | null>(null)
  const [authError, setAuthError] = useState('')
  const [isAuthenticating, setIsAuthenticating] = useState(false)
  const analysisModalOpenTimerRef = useRef<number | null>(null)
  const authSession = authSessionState
  const isResultView = Boolean(analysisResult)
  const isHistoryView = screenMode === 'history'
  const recommendedTracks = analysisResult?.recommended_tracks ?? []
  const recommendedPlaylists = analysisResult?.recommended_playlists ?? []
  const selectedRecord =
    searchRecords.find((record) => record.id === selectedRecordId) ?? searchRecords[0] ?? null
  const normalizedHistorySearchText = historySearchText.trim().toLowerCase()
  const filteredSearchRecords = normalizedHistorySearchText
    ? searchRecords.filter((record) => {
        const haystack = [
          record.input_text,
          record.genre ?? '',
          record.emotions.join(' '),
          record.mood_tags.join(' '),
          record.search_keywords.join(' '),
        ]
          .join(' ')
          .toLowerCase()

        return haystack.includes(normalizedHistorySearchText)
      })
    : searchRecords
  const currentTracks: RecommendationItem[] = isHistoryView
    ? selectedRecord?.recommended_tracks ?? []
    : recommendedTracks
  const currentPlaylists: RecommendationItem[] = isHistoryView
    ? selectedRecord?.recommended_playlists ?? []
    : recommendedPlaylists
  const activeTrack = currentTracks.find((track) => track.id === selectedTrackId) ?? currentTracks[0]
  const activePlaylist =
    currentPlaylists.find((playlist) => playlist.id === selectedPlaylistId) ?? currentPlaylists[0]
  const activeRecommendation = selectedTab === 'track' ? activeTrack : activePlaylist
  const activeVideoId = activeTrack
    ? getYoutubeVideoId(activeTrack.url) ?? (activeTrack.id.startsWith('track-') ? null : activeTrack.id)
    : null
  const progressPercent = duration > 0 ? Math.min((currentTime / duration) * 100, 100) : 0
  const loadedPlaylistTracks = activePlaylist ? playlistTracksById[activePlaylist.id] : undefined
  const playlistTrackItems = loadedPlaylistTracks?.length
    ? loadedPlaylistTracks
    : activePlaylist?.playlist_tracks?.length
      ? activePlaylist.playlist_tracks
    : samplePlaylistTracks.map((title) => ({
        title,
        thumbnail_url: '',
        url: 'https://www.youtube.com/',
        video_id: '',
      }))
  const activePlaylistTrackIndex = playlistTrackItems.length
    ? Math.min(currentPlaylistTrackIndex, playlistTrackItems.length - 1)
    : 0
  const activePlaylistTrack = playlistTrackItems[activePlaylistTrackIndex] ?? playlistTrackItems[0] ?? null
  const activePlayerVideoId =
    selectedTab === 'playlist'
      ? activePlaylistTrack?.video_id || null
      : activeVideoId
  const selectedCardImage =
    selectedTab === 'playlist'
      ? activePlaylistTrack?.thumbnail_url || activeRecommendation?.thumbnail_url
      : activeRecommendation?.thumbnail_url
  const selectedCardTitle =
    selectedTab === 'playlist'
      ? activePlaylistTrack?.title || activeRecommendation?.title
      : activeRecommendation?.title
  const selectedCardSubtitle =
    selectedTab === 'playlist'
      ? activePlaylist?.title || activeRecommendation?.channel_title
      : activeRecommendation?.channel_title
  const selectedCardUrl =
    selectedTab === 'playlist'
      ? activePlaylistTrack?.url || activeRecommendation?.url
      : activeRecommendation?.url
  const moodHighlights = Array.from(
    new Map(
      [
        ...(analysisResult?.genre ? [analysisResult.genre] : []),
        ...(analysisResult?.mood_tags ?? []),
      ].map((tag) => [tag.toLowerCase(), tag]),
  ).values(),
  ).slice(0, 4)
  const analysisModalData = isHistoryView ? selectedRecord : analysisResult
  const analysisModalTitle = isHistoryView
    ? selectedRecord?.input_text ?? '기록 상세'
    : analysisResult?.input_text ?? (inputText.trim() || 'Mood based music recommendation')
  const isAuthConfigured = Boolean(COGNITO_DOMAIN && COGNITO_CLIENT_ID && COGNITO_REDIRECT_URI)
  const authLabel = authSession?.user.email || authSession?.user.name || 'Google 로그인'

  const persistAuthSession = (session: AuthSession | null) => {
    setAuthSessionState(session)
    if (session) {
      window.localStorage.setItem(AUTH_SESSION_STORAGE_KEY, JSON.stringify(session))
      return
    }

    window.localStorage.removeItem(AUTH_SESSION_STORAGE_KEY)
  }

  const clearAuthState = () => {
    window.sessionStorage.removeItem(AUTH_PKCE_VERIFIER_KEY)
    window.sessionStorage.removeItem(AUTH_PKCE_STATE_KEY)
    window.sessionStorage.removeItem(AUTH_PKCE_HANDLED_KEY)
  }

  const decodeJwtPayload = (token: string) => {
    const payload = token.split('.')[1]
    if (!payload) {
      return {}
    }

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=')

    try {
      return JSON.parse(atob(padded))
    } catch {
      return {}
    }
  }

  const encodeBase64Url = (bytes: Uint8Array) =>
    btoa(String.fromCharCode(...bytes))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/u, '')

  const createCodeVerifier = () => {
    const randomBytes = new Uint8Array(32)
    crypto.getRandomValues(randomBytes)
    return encodeBase64Url(randomBytes)
  }

  const createCodeChallenge = async (verifier: string) => {
    const encoded = new TextEncoder().encode(verifier)
    const digest = await crypto.subtle.digest('SHA-256', encoded)
    return encodeBase64Url(new Uint8Array(digest))
  }

  const buildRequestHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      'X-App-Session-Id': authSession?.user.sub || authSession?.user.email || appSessionId,
    }

    if (authSession?.accessToken) {
      headers.Authorization = `Bearer ${authSession.accessToken}`
    }

    if (authSession?.idToken) {
      headers['X-Cognito-Id-Token'] = authSession.idToken
    }

    return headers
  }

  const finishAuthCallback = async (code: string, returnedState: string | null) => {
    const storedState = window.sessionStorage.getItem(AUTH_PKCE_STATE_KEY)
    const codeVerifier = window.sessionStorage.getItem(AUTH_PKCE_VERIFIER_KEY)

    if (!storedState || !codeVerifier || storedState !== returnedState) {
      throw new Error('로그인 상태를 확인할 수 없습니다. 다시 시도해 주세요.')
    }

    if (!isAuthConfigured) {
      throw new Error('Cognito 설정이 부족합니다.')
    }

    const response = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: COGNITO_CLIENT_ID,
        code,
        code_verifier: codeVerifier,
        redirect_uri: COGNITO_REDIRECT_URI,
      }).toString(),
    })

    if (!response.ok) {
      const responseText = await response.text()
      let errorDetail = responseText.trim()

      try {
        const parsed = JSON.parse(responseText) as { error?: string; error_description?: string }
        errorDetail = [parsed.error, parsed.error_description].filter(Boolean).join(': ')
      } catch {
        // 응답이 JSON이 아닐 수 있어서 원문을 그대로 사용한다.
      }

      throw new Error(
        errorDetail ? `로그인 토큰 교환에 실패했습니다. ${errorDetail}` : '로그인 토큰 교환에 실패했습니다.',
      )
    }

    const tokenPayload = (await response.json()) as {
      access_token?: string
      id_token?: string
      expires_in?: number
    }

    if (!tokenPayload.access_token || !tokenPayload.id_token) {
      throw new Error('로그인 토큰을 받을 수 없습니다.')
    }

    const decoded = decodeJwtPayload(tokenPayload.id_token) as {
      email?: string
      name?: string
      picture?: string
      sub?: string
    }

    persistAuthSession({
      accessToken: tokenPayload.access_token,
      idToken: tokenPayload.id_token,
      expiresAt: Date.now() + (tokenPayload.expires_in ?? 0) * 1000,
      user: {
        email: decoded.email,
        name: decoded.name,
        picture: decoded.picture,
        sub: decoded.sub,
      },
    })
    clearAuthState()

    const cleanUrl = new URL(window.location.href)
    cleanUrl.searchParams.delete('code')
    cleanUrl.searchParams.delete('state')
    cleanUrl.searchParams.delete('error')
    cleanUrl.searchParams.delete('error_description')
    window.history.replaceState({}, '', cleanUrl.toString())
  }

  const startGoogleLogin = async () => {
    if (!isAuthConfigured) {
      setAuthError('Cognito 설정이 아직 없습니다.')
      return
    }

    setAuthError('')
    setIsAuthenticating(true)

    try {
      const codeVerifier = createCodeVerifier()
      const codeChallenge = await createCodeChallenge(codeVerifier)
      const state = createCodeVerifier()

      window.sessionStorage.setItem(AUTH_PKCE_VERIFIER_KEY, codeVerifier)
      window.sessionStorage.setItem(AUTH_PKCE_STATE_KEY, state)
      window.sessionStorage.removeItem(AUTH_PKCE_HANDLED_KEY)

      const authorizeUrl = new URL(`${COGNITO_DOMAIN}/oauth2/authorize`)
      authorizeUrl.searchParams.set('client_id', COGNITO_CLIENT_ID)
      authorizeUrl.searchParams.set('response_type', 'code')
      authorizeUrl.searchParams.set('scope', COGNITO_SCOPE)
      authorizeUrl.searchParams.set('redirect_uri', COGNITO_REDIRECT_URI)
      authorizeUrl.searchParams.set('state', state)
      authorizeUrl.searchParams.set('code_challenge_method', 'S256')
      authorizeUrl.searchParams.set('code_challenge', codeChallenge)

      window.location.assign(authorizeUrl.toString())
    } catch (error) {
      setIsAuthenticating(false)
      setAuthError(error instanceof Error ? error.message : '로그인을 시작할 수 없습니다.')
    }
  }

  const handleLogout = () => {
    persistAuthSession(null)
    clearAuthState()

    if (!isAuthConfigured) {
      return
    }

    const logoutUrl = new URL(`${COGNITO_DOMAIN}/logout`)
    logoutUrl.searchParams.set('client_id', COGNITO_CLIENT_ID)
    logoutUrl.searchParams.set('logout_uri', COGNITO_LOGOUT_URI)
    window.location.assign(logoutUrl.toString())
  }

  useEffect(() => {
    const storedSession = window.localStorage.getItem(AUTH_SESSION_STORAGE_KEY)
    if (!storedSession) {
      return
    }

    try {
      const parsedSession = JSON.parse(storedSession) as AuthSession
      setAuthSessionState(parsedSession)
    } catch {
      window.localStorage.removeItem(AUTH_SESSION_STORAGE_KEY)
    }
  }, [])

  useEffect(() => {
    const currentUrl = new URL(window.location.href)
    const code = currentUrl.searchParams.get('code')
    const returnedState = currentUrl.searchParams.get('state')
    const authErrorCode = currentUrl.searchParams.get('error')
    const authErrorDescription = currentUrl.searchParams.get('error_description')

    if (!code && !authErrorCode) {
      return
    }

    const handledKey = [code ?? '', returnedState ?? '', authErrorCode ?? ''].join('|')
    if (window.sessionStorage.getItem(AUTH_PKCE_HANDLED_KEY) === handledKey) {
      return
    }
    window.sessionStorage.setItem(AUTH_PKCE_HANDLED_KEY, handledKey)

    const handleCallback = async () => {
      setIsAuthenticating(true)
      setAuthError('')

      try {
        if (authErrorCode) {
          throw new Error(authErrorDescription || '로그인이 취소되었거나 실패했습니다.')
        }

        if (!code) {
          throw new Error('로그인 코드를 확인할 수 없습니다.')
        }

        await finishAuthCallback(code, returnedState)
      } catch (error) {
        persistAuthSession(null)
        clearAuthState()
        setAuthError(error instanceof Error ? error.message : '로그인 처리 중 오류가 발생했습니다.')
      } finally {
        setIsAuthenticating(false)
      }
    }

    void handleCallback()
  }, [])

  useEffect(() => {
    return () => {
      if (analysisModalCloseTimerRef.current) {
        window.clearTimeout(analysisModalCloseTimerRef.current)
      }
      if (analysisModalOpenTimerRef.current) {
        window.clearTimeout(analysisModalOpenTimerRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (!isHistoryView || !authSession) {
      return
    }

    const abortController = new AbortController()

    const loadSearchRecords = async () => {
      try {
        const response = await fetch(apiUrl('/search-records'), {
          headers: {
            ...buildRequestHeaders(),
          },
          signal: abortController.signal,
        })

        if (!response.ok) {
          return
        }

        const records: SearchRecord[] = await response.json()
        setSearchRecords(records)
        setSelectedRecordId((currentId) => currentId ?? records[0]?.id ?? null)
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.error(error)
        }
      }
    }

    void loadSearchRecords()

    return () => {
      abortController.abort()
    }
  }, [authSession, appSessionId, isHistoryView])

  useEffect(() => {
    playlistTrackItemRefs.current = playlistTrackItemRefs.current.slice(0, playlistTrackItems.length)
    if (selectedTab !== 'playlist') {
      return
    }

    const activeItem = playlistTrackItemRefs.current[activePlaylistTrackIndex]
    if (!activeItem) {
      return
    }

    activeItem.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }, [activePlaylistTrackIndex, playlistTrackItems.length, selectedTab])

  useEffect(() => {
    if (
      !authSession ||
      !activePlaylist ||
      activePlaylist.playlist_tracks?.length ||
      playlistTracksById[activePlaylist.id]
    ) {
      return
    }

    const abortController = new AbortController()
    const query = new URLSearchParams({ title: activePlaylist.title })

    const loadPlaylistTracks = async () => {
      try {
        const response = await fetch(
          apiUrl(`/playlists/${encodeURIComponent(activePlaylist.id)}/tracks?${query.toString()}`),
          {
            headers: {
              ...buildRequestHeaders(),
            },
            signal: abortController.signal,
          },
        )

        if (!response.ok) {
          return
        }

        const tracks: PlaylistTrackItem[] = await response.json()
        setPlaylistTracksById((currentTracks) => ({
          ...currentTracks,
          [activePlaylist.id]: tracks,
        }))
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.error(error)
        }
      }
    }

    void loadPlaylistTracks()

    return () => {
      abortController.abort()
    }
  }, [activePlaylist, authSession, appSessionId, playlistTracksById])

  useEffect(() => {
    if (window.YT?.Player) {
      return
    }

    const previousReadyHandler = window.onYouTubeIframeAPIReady
    window.onYouTubeIframeAPIReady = () => {
      previousReadyHandler?.()
      setIsYoutubeApiReady(true)
    }

    if (!document.querySelector(`script[src="${YOUTUBE_IFRAME_API_URL}"]`)) {
      const script = document.createElement('script')
      script.src = YOUTUBE_IFRAME_API_URL
      script.async = true
      document.body.appendChild(script)
    }
  }, [])

  useEffect(() => {
    if (!isResultView || !isYoutubeApiReady || !window.YT?.Player || !activePlayerVideoId) {
      return
    }

    if (!youtubePlayerRef.current) {
      youtubePlayerRef.current = new window.YT.Player(YOUTUBE_PLAYER_ELEMENT_ID, {
        height: '1',
        width: '1',
        videoId: activePlayerVideoId,
        playerVars: {
          autoplay: 0,
          playsinline: 1,
        },
        events: {
          onStateChange: (event) => {
            if (event.data === window.YT?.PlayerState.PLAYING) {
              setIsPlayerActive(true)
              return
            }

            if (event.data === window.YT?.PlayerState.ENDED) {
              setIsPlayerActive(false)
            }
          },
        },
      })
      loadedVideoIdRef.current = activePlayerVideoId
      return
    }

    if (loadedVideoIdRef.current !== activePlayerVideoId) {
      youtubePlayerRef.current.loadVideoById(activePlayerVideoId)
      loadedVideoIdRef.current = activePlayerVideoId
      setCurrentTime(0)
      setDuration(0)
    }
  }, [
    activePlayerVideoId,
    isResultView,
    isYoutubeApiReady,
  ])

  useEffect(() => {
    if (progressTimerRef.current) {
      window.clearInterval(progressTimerRef.current)
      progressTimerRef.current = null
    }

    if (!isPlayerActive || !youtubePlayerRef.current) {
      return
    }

    progressTimerRef.current = window.setInterval(() => {
      const player = youtubePlayerRef.current
      if (!player) {
        return
      }

      setCurrentTime(player.getCurrentTime())
      setDuration(player.getDuration())
    }, 500)

    return () => {
      if (progressTimerRef.current) {
        window.clearInterval(progressTimerRef.current)
        progressTimerRef.current = null
      }
    }
  }, [isPlayerActive])

  const analyzeMoodText = async (text: string) => {
    const trimmedText = text.trim()
    if (!trimmedText) {
      return
    }

    setScreenMode('search')
    setIsLoading(true)
    setErrorMessage('')

    try {
      const response = await fetch(apiUrl('/analyze'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...buildRequestHeaders(),
        },
        body: JSON.stringify({ text: trimmedText, search_scope: searchScope }),
      })

      if (!response.ok) {
        const responseText = await response.text()
        let errorDetail = responseText.trim()

        try {
          const parsed = JSON.parse(responseText) as { detail?: string; message?: string }
          errorDetail = parsed.detail ?? parsed.message ?? errorDetail
        } catch {
          // 텍스트 응답이면 원문을 그대로 보여준다.
        }

        throw new Error(
          errorDetail ? `분석 요청에 실패했습니다. ${errorDetail}` : '분석 요청에 실패했습니다.',
        )
      }

      const result: AnalyzeResult = await response.json()
      setAnalysisResult(result)
      setPlaylistTracksById({})
      setSelectedTrackId(result.recommended_tracks[0]?.id ?? null)
      setSelectedPlaylistId(result.recommended_playlists[0]?.id ?? null)
      setCurrentPlaylistTrackIndex(0)
      loadedVideoIdRef.current = null
      setIsPlayerActive(false)
      setCurrentTime(0)
      setDuration(0)
      setInputText('')
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : '분석 결과를 불러오지 못했습니다. 백엔드 서버를 확인해 주세요.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void analyzeMoodText(inputText)
  }

  const getKeywordTooltipPosition = (clientX: number, clientY: number) => {
    const width = 280
    const height = 140
    const margin = 16
    const left = Math.min(clientX + 18, window.innerWidth - width - margin)
    const top = Math.min(clientY + 18, window.innerHeight - height - margin)

    return {
      left: Math.max(margin, left),
      top: Math.max(margin, top),
    }
  }

  const openKeywordTooltip = (label: string, value: string, event: MouseEvent<HTMLDivElement>) => {
    const position = getKeywordTooltipPosition(event.clientX, event.clientY)
    setKeywordTooltip({ label, value, ...position })
  }

  const moveKeywordTooltip = (value: string, event: MouseEvent<HTMLDivElement>) => {
    setKeywordTooltip((current) => {
      if (!current) {
        return current
      }

      return {
        ...current,
        value,
        ...getKeywordTooltipPosition(event.clientX, event.clientY),
      }
    })
  }

  const closeKeywordTooltip = () => {
    setKeywordTooltip(null)
  }

  const scheduleAnalysisModalOpen = () => {
    if (analysisModalOpenTimerRef.current) {
      window.clearTimeout(analysisModalOpenTimerRef.current)
    }

    analysisModalOpenTimerRef.current = window.setTimeout(() => {
      setIsAnalysisModalOpen(true)
      analysisModalOpenTimerRef.current = null
    }, 2000)
  }

  const closeAnalysisModal = () => {
    if (analysisModalOpenTimerRef.current) {
      window.clearTimeout(analysisModalOpenTimerRef.current)
      analysisModalOpenTimerRef.current = null
    }

    if (analysisModalCloseTimerRef.current) {
      window.clearTimeout(analysisModalCloseTimerRef.current)
    }

    analysisModalCloseTimerRef.current = window.setTimeout(() => {
      setIsAnalysisModalOpen(false)
      analysisModalCloseTimerRef.current = null
    }, 120)
  }

  const openSearchMode = () => {
    setScreenMode('search')
  }

  const openHistoryMode = () => {
    setScreenMode('history')
  }

  const renderRecommendationTabs = (layout: 'inline' | 'sidebar' = 'inline') => (
    <nav
      className={layout === 'sidebar' ? 'recommendation-tabs' : 'recommendation-tabs recommendation-tabs-inline'}
      aria-label="추천 유형"
    >
      <button type="button" className={selectedTab === 'track' ? 'active' : ''} onClick={() => setSelectedTab('track')}>
        <span className="tab-icon" aria-hidden="true">
          ♬
        </span>
        추천 곡
      </button>
      <button
        type="button"
        className={selectedTab === 'playlist' ? 'active' : ''}
        onClick={() => setSelectedTab('playlist')}
      >
        <span className="tab-icon" aria-hidden="true">
          ≡
        </span>
        플레이리스트
      </button>
    </nav>
  )

  const renderSearchScopeSwitch = () => (
    <div className="scope-switch" role="group" aria-label="검색 기준 선택">
      <button
        type="button"
        className={searchScope === 'all' ? 'active' : ''}
        onClick={() => setSearchScope('all')}
        aria-label="전체"
        title="전체"
      >
        <span aria-hidden="true" className="scope-switch-icon">
          🌐
        </span>
      </button>
      <button
        type="button"
        className={searchScope === 'korean' ? 'active' : ''}
        onClick={() => setSearchScope('korean')}
        aria-label="한국어 중심"
        title="한국어 중심"
      >
        <span aria-hidden="true" className="scope-switch-text">
          KR
        </span>
      </button>
    </div>
  )

  const renderEnvironmentBadge = () => (
    <div className="auth-actions">
      <span className={`environment-badge ${ENVIRONMENT_LABEL === 'PROD' ? 'prod' : 'local'}`}>
        {ENVIRONMENT_LABEL}
      </span>
    </div>
  )

  const renderAuthControls = () => (
    <div className="auth-actions">
      {authSession ? (
        <>
          <span className="auth-chip" title={authSession.user.email || authSession.user.name || 'Google 로그인'}>
            {authLabel}
          </span>
          <button type="button" className="auth-button secondary" onClick={handleLogout}>
            로그아웃
          </button>
        </>
      ) : (
        <button
          type="button"
          className="auth-button"
          onClick={startGoogleLogin}
          disabled={!isAuthConfigured || isAuthenticating}
        >
          {isAuthenticating ? '로그인 처리 중' : 'Google 로그인'}
        </button>
      )}
    </div>
  )

  const renderAnalysisModal = () => {
    const source = analysisModalData
    const emotionText = source?.emotion_text ?? source?.input_text ?? '아직 분석 결과가 없습니다.'
    const requestText = source?.request_text ?? '아직 요청 표현이 없습니다.'
    const requestKeywords = source?.request_keywords?.length ? source.request_keywords.join(', ') : '없음'
    const blockedMoodTags = source?.blocked_mood_tags?.length ? source.blocked_mood_tags.join(', ') : '없음'
    const preferredMoodTags = source?.mood_tags?.length ? source.mood_tags.join(', ') : '없음'
    const searchKeywords = source?.search_keywords?.length ? source.search_keywords.join(', ') : '없음'

    return (
      <div className="analysis-modal-backdrop" role="presentation" onMouseEnter={scheduleAnalysisModalOpen} onMouseLeave={closeAnalysisModal}>
        <div className="analysis-modal" role="dialog" aria-modal="false" aria-label="분석 요약">
          <p className="analysis-modal-eyebrow">Mood based music recommendation</p>
          <h2>{analysisModalTitle}</h2>
          <div className="analysis-modal-grid">
            <div>
              <span>감정 표현</span>
              <strong>{emotionText}</strong>
            </div>
            <div>
              <span>요청 표현</span>
              <strong>{requestText}</strong>
            </div>
            <div>
              <span>선호 태그</span>
              <strong>{preferredMoodTags}</strong>
            </div>
            <div>
              <span>차단 태그</span>
              <strong>{blockedMoodTags}</strong>
            </div>
            <div>
              <span>요청 키워드</span>
              <strong>{requestKeywords}</strong>
            </div>
            <div>
              <span>검색 키워드</span>
              <strong>{searchKeywords}</strong>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderHistorySidebar = () => (
    <aside className="dashboard-sidebar history-sidebar">
      <div className="history-sidebar-top">
        <button type="button" className="sidebar-logo-button" onClick={openSearchMode}>
          Moodify
        </button>
        <button type="button" className="sidebar-history-button" onClick={openSearchMode}>
          검색으로 돌아가기
        </button>
      </div>
      {renderRecommendationTabs('sidebar')}
      <div className="history-rail">
        <h2>최근 기록</h2>
        <div className="history-list-scroll">
          <div className="history-list">
            {filteredSearchRecords.length ? (
              filteredSearchRecords.map((record) => (
                <button
                  type="button"
                  key={record.id}
                  className={record.id === selectedRecord?.id ? 'history-item active' : 'history-item'}
                  onClick={() => setSelectedRecordId(record.id)}
                >
                  <span className="history-item-title">{record.input_text}</span>
                  <span className="history-item-meta">
                    {new Date(record.created_at).toLocaleString('ko-KR')}
                  </span>
                </button>
              ))
            ) : (
              <div className="empty-state compact">
                <h3>아직 기록이 없습니다</h3>
                <p>검색 결과가 없거나 아직 기록이 없습니다.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  )

  const renderPlayerBar = () => (
    <footer className="player-bar" aria-label="YouTube player">
      <div className="player-bar-row">
        <div className="player-controls-shell">
          <button
            type="button"
            onClick={() => (selectedTab === 'playlist' ? stepPlaylistTrack('previous') : selectTrackByOffset(-1))}
            aria-label={selectedTab === 'playlist' ? '플레이리스트 이전 곡' : '이전 추천 곡'}
          >
            <span aria-hidden="true">⏮</span>
          </button>
          <button
            type="button"
            className="player-main-button"
            onClick={togglePlayer}
            disabled={
              (selectedTab === 'track'
                ? !activeVideoId
                : !playlistTrackItems[currentPlaylistTrackIndex]?.video_id) || !isYoutubeApiReady
            }
            aria-label={
              isPlayerActive
                ? '재생 중지'
                : selectedTab === 'track'
                  ? '선택한 곡 재생'
                  : '선택한 플레이리스트 재생'
            }
          >
            <span aria-hidden="true">{isPlayerActive ? '⏸' : '▶'}</span>
          </button>
          <button
            type="button"
            onClick={() => (selectedTab === 'playlist' ? stepPlaylistTrack('next') : selectTrackByOffset(1))}
            aria-label={selectedTab === 'playlist' ? '플레이리스트 다음 곡' : '다음 추천 곡'}
          >
            <span aria-hidden="true">⏭</span>
          </button>
        </div>

        <div id={YOUTUBE_PLAYER_ELEMENT_ID} className="youtube-audio-frame" />

        <div className="player-track-info">
          {selectedTab === 'playlist' ? (
            <>
              {selectedCardImage && <img src={selectedCardImage} alt="" />}
              <div className="player-track-copy">
                <p>{selectedCardTitle}</p>
                <span>{selectedCardSubtitle}</span>
              </div>
            </>
          ) : (
            <>
              {activeRecommendation?.thumbnail_url && <img src={activeRecommendation.thumbnail_url} alt="" />}
              <div>
                <p>{activeRecommendation?.title}</p>
                <span>{activeRecommendation?.channel_title}</span>
              </div>
            </>
          )}
        </div>

        <div
          className="player-progress"
          aria-label="재생 위치 조절"
          role="slider"
          tabIndex={0}
          aria-valuemin={0}
          aria-valuemax={Math.max(duration, 0)}
          aria-valuenow={Math.min(currentTime, duration)}
          onPointerCancel={(event) => stopProgressDrag(event, progressBarRef.current)}
          onPointerDown={(event) => startProgressDrag(event, progressBarRef.current)}
          onPointerLeave={(event) => stopProgressDrag(event, progressBarRef.current)}
          onPointerMove={(event) => moveProgressDrag(event, progressBarRef.current)}
          onPointerUp={(event) => stopProgressDrag(event, progressBarRef.current)}
        >
          <span>{formatTime(currentTime)}</span>
          <div className="player-progress-bar" ref={progressBarRef}>
            <i style={{ width: `${progressPercent}%` }} />
          </div>
          <span>{formatTime(duration)}</span>
        </div>

        <a href={activeRecommendation?.url} target="_blank" rel="noreferrer">
          YouTube
        </a>
      </div>
    </footer>
  )

  const startDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!rail) {
      return
    }

    dragState.current = {
      isDragging: true,
      lastTime: performance.now(),
      lastX: event.clientX,
      startX: event.clientX,
      scrollLeft: rail.scrollLeft,
      velocity: 0,
    }
  }

  const moveDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!dragState.current.isDragging || !rail) {
      return
    }

    event.preventDefault()
    const distance = event.clientX - dragState.current.startX

    const now = performance.now()
    const timeDelta = now - dragState.current.lastTime
    if (timeDelta > 0) {
      dragState.current.velocity = (event.clientX - dragState.current.lastX) / timeDelta
      dragState.current.lastTime = now
      dragState.current.lastX = event.clientX
    }

    rail.scrollLeft = dragState.current.scrollLeft - distance
  }

  const startPlaylistDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!rail) {
      return
    }

    playlistDragState.current = {
      isDragging: true,
      lastTime: performance.now(),
      lastY: event.clientY,
      startY: event.clientY,
      scrollTop: rail.scrollTop,
      velocity: 0,
    }
  }

  const movePlaylistDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!playlistDragState.current.isDragging || !rail) {
      return
    }

    event.preventDefault()
    const distance = event.clientY - playlistDragState.current.startY

    const now = performance.now()
    const timeDelta = now - playlistDragState.current.lastTime
    if (timeDelta > 0) {
      playlistDragState.current.velocity = (event.clientY - playlistDragState.current.lastY) / timeDelta
      playlistDragState.current.lastTime = now
      playlistDragState.current.lastY = event.clientY
    }

    rail.scrollTop = playlistDragState.current.scrollTop - distance
  }

  const stopPlaylistDrag = (
    event?: React.PointerEvent<HTMLDivElement>,
    rail?: HTMLDivElement | null,
  ) => {
    const draggedDistance = Math.abs(
      (event?.clientY ?? playlistDragState.current.lastY) - playlistDragState.current.startY,
    )
    playlistDragState.current.isDragging = false

    if (!rail || draggedDistance < 12) {
      return
    }

    let velocity = playlistDragState.current.velocity * -18
    const glide = () => {
      if (Math.abs(velocity) < 0.2) {
        return
      }

      rail.scrollTop += velocity
      velocity *= 0.88
      requestAnimationFrame(glide)
    }

    requestAnimationFrame(glide)
  }

  const stopDrag = (event?: React.PointerEvent<HTMLDivElement>, rail?: HTMLDivElement | null) => {
    const draggedDistance = Math.abs(
      (event?.clientX ?? dragState.current.lastX) - dragState.current.startX,
    )
    dragState.current.isDragging = false

    if (draggedDistance >= 12) {
      ignoreClickAfterDrag.current = true
      window.setTimeout(() => {
        ignoreClickAfterDrag.current = false
      }, 0)
    }

    if (!rail || draggedDistance < 12) {
      return
    }

    let velocity = dragState.current.velocity * -18
    const glide = () => {
      if (Math.abs(velocity) < 0.2) {
        return
      }

      rail.scrollLeft += velocity
      velocity *= 0.88
      requestAnimationFrame(glide)
    }

    requestAnimationFrame(glide)
  }

  const getSeekTimeFromPointer = (clientX: number, rail: HTMLDivElement | null) => {
    if (!rail || duration <= 0) {
      return null
    }

    const rect = rail.getBoundingClientRect()
    const offsetX = Math.min(Math.max(clientX - rect.left, 0), rect.width)
    const nextTime = (offsetX / rect.width) * duration

    if (!Number.isFinite(nextTime)) {
      return null
    }

    return Math.min(Math.max(nextTime, 0), duration)
  }

  const updateProgressPosition = (clientX: number, rail: HTMLDivElement | null) => {
    const player = youtubePlayerRef.current
    const nextTime = getSeekTimeFromPointer(clientX, rail)

    if (nextTime === null) {
      return
    }

    setCurrentTime(nextTime)

    if (player) {
      player.seekTo(nextTime, true)
    }
  }

  const startProgressDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!rail || duration <= 0) {
      return
    }

    rail.setPointerCapture(event.pointerId)
    progressDragState.current = {
      isDragging: true,
      wasPlaying: isPlayerActive,
    }

    youtubePlayerRef.current?.pauseVideo()
    setIsPlayerActive(false)
    event.preventDefault()
    updateProgressPosition(event.clientX, rail)
  }

  const moveProgressDrag = (event: React.PointerEvent<HTMLDivElement>, rail: HTMLDivElement | null) => {
    if (!progressDragState.current.isDragging || !rail) {
      return
    }

    event.preventDefault()
    updateProgressPosition(event.clientX, rail)
  }

  const stopProgressDrag = (event?: React.PointerEvent<HTMLDivElement>, rail?: HTMLDivElement | null) => {
    if (!progressDragState.current.isDragging) {
      return
    }

    progressDragState.current.isDragging = false

    if (event && rail?.hasPointerCapture(event.pointerId)) {
      rail.releasePointerCapture(event.pointerId)
    }

    if (event && rail) {
      updateProgressPosition(event.clientX, rail)
    }

    if (progressDragState.current.wasPlaying) {
      youtubePlayerRef.current?.playVideo()
      setIsPlayerActive(true)
    }
  }

  const selectTrack = (trackId: string) => {
    setSelectedTrackId(trackId)
    setCurrentTime(0)
    setDuration(0)
  }

  const selectPlaylist = (playlistId: string) => {
    setSelectedPlaylistId(playlistId)
    setCurrentPlaylistTrackIndex(0)
    setCurrentTime(0)
    setDuration(0)
  }

  const playPlaylistTrack = (index: number) => {
    if (!playlistTrackItems.length) {
      return
    }

    const nextIndex = Math.max(0, Math.min(index, playlistTrackItems.length - 1))
    const track = playlistTrackItems[nextIndex]
    if (!track?.video_id) {
      return
    }

    const player = youtubePlayerRef.current

    setSelectedTab('playlist')
    setCurrentPlaylistTrackIndex(nextIndex)
    setCurrentTime(0)
    setDuration(0)

    if (!player) {
      return
    }

    if (loadedVideoIdRef.current !== track.video_id) {
      player.loadVideoById(track.video_id)
      loadedVideoIdRef.current = track.video_id
    }
    player.playVideo()
    setIsPlayerActive(true)
  }

  const rememberCardPressStart = (event: React.PointerEvent<HTMLElement>) => {
    cardPressStartX.current = event.clientX
  }

  const selectTrackOnPointerUp = (event: React.PointerEvent<HTMLElement>, trackId: string) => {
    const movedDistance = Math.abs(event.clientX - cardPressStartX.current)
    if (movedDistance < 12) {
      selectTrack(trackId)
    }
  }

  const selectPlaylistOnPointerUp = (event: React.PointerEvent<HTMLElement>, playlistId: string) => {
    const movedDistance = Math.abs(event.clientX - cardPressStartX.current)
    if (movedDistance < 12) {
      selectPlaylist(playlistId)
    }
  }

  const selectTrackOnClick = (trackId: string) => {
    if (!ignoreClickAfterDrag.current) {
      selectTrack(trackId)
    }
  }

  const selectPlaylistOnClick = (playlistId: string) => {
    if (!ignoreClickAfterDrag.current) {
      selectPlaylist(playlistId)
    }
  }

  const selectTrackByOffset = (offset: number) => {
    if (!currentTracks.length) {
      return
    }

    const currentIndex = activeTrack
      ? currentTracks.findIndex((track) => track.id === activeTrack.id)
      : 0
    const nextIndex = (currentIndex + offset + currentTracks.length) % currentTracks.length

    setSelectedTab('track')
    setSelectedTrackId(currentTracks[nextIndex].id)
    setCurrentTime(0)
    setDuration(0)
  }

  const stepPlaylistTrack = (direction: 'previous' | 'next') => {
    const player = youtubePlayerRef.current
    if (!player || !playlistTrackItems.length) {
      return
    }

    const baseIndex = Math.max(0, Math.min(currentPlaylistTrackIndex, playlistTrackItems.length - 1))
    const nextIndex =
      (baseIndex + (direction === 'previous' ? -1 : 1) + playlistTrackItems.length) %
      playlistTrackItems.length
    const nextTrack = playlistTrackItems[nextIndex]

    if (!nextTrack?.video_id) {
      return
    }

    if (loadedVideoIdRef.current !== nextTrack.video_id) {
      player.loadVideoById(nextTrack.video_id)
      loadedVideoIdRef.current = nextTrack.video_id
    }

    player.playVideo()
    setCurrentPlaylistTrackIndex(nextIndex)
    setSelectedTab('playlist')
    setIsPlayerActive(true)
    setCurrentTime(0)
    setDuration(0)
  }

  const togglePlayer = () => {
    const player = youtubePlayerRef.current
    if (!player) {
      return
    }

    if (isPlayerActive) {
      player.pauseVideo()
      setIsPlayerActive(false)
      return
    }

    const targetVideoId =
      selectedTab === 'playlist'
        ? playlistTrackItems[currentPlaylistTrackIndex]?.video_id ?? null
        : activeVideoId

    if (!targetVideoId) {
      return
    }

    if (loadedVideoIdRef.current !== targetVideoId) {
      player.loadVideoById(targetVideoId)
      loadedVideoIdRef.current = targetVideoId
    }

    if (selectedTab === 'playlist') {
      player.playVideo()
      setIsPlayerActive(true)
      return
    }

    player.playVideo()
    setIsPlayerActive(true)
  }

  if (!authSession) {
    return (
      <main className="app-shell auth-gate-shell">
        <section className="auth-gate-card" aria-labelledby="auth-gate-title">
          <p className="auth-gate-badge">Login required</p>
          <h1 id="auth-gate-title">먼저 로그인한 뒤 음악 추천을 시작하세요</h1>
          <p className="auth-gate-copy">
            이 서비스는 로그인 후 검색 기록 저장과 추천 결과 활용을 지원합니다.
          </p>
          {renderAuthControls()}
          {authError && <p className="auth-error">{authError}</p>}
        </section>
      </main>
    )
  }

  if (isHistoryView) {
    return (
      <main className="app-shell">
        <section className="music-dashboard history-dashboard" aria-labelledby="history-title">
          {renderHistorySidebar()}
          <section className="dashboard-main history-main">
            <div className="screen-toolbar history-toolbar">
              <div>
                <p className="eyebrow">Search records</p>
                <h1 id="history-title">기록 보기</h1>
              </div>
              <div className="toolbar-actions">
                <form className="history-search-form" onSubmit={(event) => event.preventDefault()}>
                  <label htmlFor="history-search-input" className="sr-only">
                    기록 검색
                  </label>
                  <input
                    id="history-search-input"
                    value={historySearchText}
                    onChange={(event) => setHistorySearchText(event.target.value)}
                    placeholder="기록 검색"
                  />
                  {renderSearchScopeSwitch()}
                </form>
                {renderAuthControls()}
                {renderEnvironmentBadge()}
              </div>
            </div>
            <div className="history-summary-card">
              <div className="history-summary-head">
                <span
                  className="record-scope-icon"
                  aria-label={selectedRecord?.search_scope === 'korean' ? '한국어 중심' : '전체'}
                >
                  {selectedRecord?.search_scope === 'korean' ? '🇰🇷' : '🌐'}
                </span>
                <span className="record-meta-time">
                  {selectedRecord ? new Date(selectedRecord.created_at).toLocaleString('ko-KR') : '최근 기록 없음'}
                </span>
                {selectedRecord?.genre && <span className="record-meta-genre">{selectedRecord.genre}</span>}
              </div>
              <p>{selectedRecord?.input_text ?? '기록을 선택해 주세요'}</p>
            </div>
            <section className="recommendation-area" aria-label="기록 추천 결과">
              <h1 id="history-result-title">{selectedTab === 'track' ? 'Explore new' : 'Playlists'}</h1>
              {selectedTab === 'track' ? (
                <div
                  className="track-grid draggable-rail"
                  ref={trackRailRef}
                  onPointerCancel={(event) => stopDrag(event, trackRailRef.current)}
                  onPointerDown={(event) => startDrag(event, trackRailRef.current)}
                  onPointerLeave={(event) => stopDrag(event, trackRailRef.current)}
                  onPointerMove={(event) => moveDrag(event, trackRailRef.current)}
                  onPointerUp={(event) => stopDrag(event, trackRailRef.current)}
                >
                  {currentTracks.map((track) => (
                    <div
                      role="button"
                      tabIndex={0}
                      className={`track-card ${activeTrack?.id === track.id ? 'active' : ''}`}
                      key={track.id}
                      onClick={() => selectTrackOnClick(track.id)}
                      onPointerDown={rememberCardPressStart}
                      onPointerUp={(event) => selectTrackOnPointerUp(event, track.id)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          selectTrack(track.id)
                        }
                      }}
                    >
                      {track.thumbnail_url && <img src={track.thumbnail_url} alt="" />}
                      <h3>{track.title}</h3>
                      <p>{track.channel_title}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  className="playlist-card-grid draggable-rail"
                  ref={playlistRailRef}
                  onPointerCancel={(event) => stopDrag(event, playlistRailRef.current)}
                  onPointerDown={(event) => startDrag(event, playlistRailRef.current)}
                  onPointerLeave={(event) => stopDrag(event, playlistRailRef.current)}
                  onPointerMove={(event) => moveDrag(event, playlistRailRef.current)}
                  onPointerUp={(event) => stopDrag(event, playlistRailRef.current)}
                >
                  {currentPlaylists.map((playlist, index) => (
                    <div
                      role="button"
                      tabIndex={0}
                      className={`playlist-card ${activePlaylist?.id === playlist.id ? 'active' : ''}`}
                      key={playlist.id}
                      onClick={() => selectPlaylistOnClick(playlist.id)}
                      onPointerDown={rememberCardPressStart}
                      onPointerUp={(event) => selectPlaylistOnPointerUp(event, playlist.id)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          selectPlaylist(playlist.id)
                        }
                      }}
                    >
                      {playlist.thumbnail_url ? (
                        <img src={playlist.thumbnail_url} alt="" />
                      ) : (
                        <span className="playlist-fallback">{index + 1}</span>
                      )}
                      <h3>{playlist.title}</h3>
                      <p>{playlist.channel_title}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <div className="detail-grid history-detail-grid">
              <section className="selected-track-section" aria-label="선택한 결과">
                <h2>Popular</h2>
                <article className="selected-track-card">
                  {selectedCardImage && <img src={selectedCardImage} alt="" className="selected-track-image" />}
                  <div>
                    {selectedTab === 'track' && <p className="card-type">Selected track</p>}
                    <a
                      href={selectedCardUrl}
                      className="selected-track-title-link"
                      target="_blank"
                      rel="noreferrer"
                    >
                      <h3>{selectedCardTitle}</h3>
                    </a>
                    <p className="channel-name">{selectedCardSubtitle}</p>
                    {selectedTab === 'playlist' && (
                      <div
                        className="playlist-track-scroll draggable-rail vertical-rail"
                        ref={playlistTrackScrollRef}
                        onPointerCancel={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerDown={(event) => startPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerLeave={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerMove={(event) => movePlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerUp={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                      >
                        <ol className="sample-track-list playlist-track-list">
                          {playlistTrackItems.map((track, index) => (
                            <li
                              key={`${activeRecommendation?.id ?? 'playlist'}-${index}-${track.title}`}
                              className={index === activePlaylistTrackIndex ? 'active' : ''}
                              ref={(node) => {
                                playlistTrackItemRefs.current[index] = node
                              }}
                              role="button"
                              tabIndex={0}
                              onClick={() => playPlaylistTrack(index)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter' || event.key === ' ') {
                                  playPlaylistTrack(index)
                                }
                              }}
                            >
                              {track.thumbnail_url ? (
                                <img className="playlist-track-thumb" src={track.thumbnail_url} alt="" />
                              ) : (
                                <span className="playlist-track-number">{index + 1}</span>
                              )}
                              <span className="playlist-track-title">{track.title}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                </article>
              </section>
              <section className="mood-panel history-keywords-panel" aria-label="기록 키워드">
                <h2>Keywords</h2>
                <div
                  className="mood-card history-keyword-card"
                  onMouseEnter={(event) =>
                    openKeywordTooltip('감정', selectedRecord?.emotions.join(', ') || '없음', event)
                  }
                  onMouseMove={(event) =>
                    moveKeywordTooltip(selectedRecord?.emotions.join(', ') || '없음', event)
                  }
                  onMouseLeave={closeKeywordTooltip}
                >
                  <strong>감정</strong>
                  <p>{selectedRecord?.emotions.join(', ') || '없음'}</p>
                </div>
                <div
                  className="mood-card history-keyword-card"
                  onMouseEnter={(event) =>
                    openKeywordTooltip('분위기', selectedRecord?.mood_tags.join(', ') || '없음', event)
                  }
                  onMouseMove={(event) => moveKeywordTooltip(selectedRecord?.mood_tags.join(', ') || '없음', event)}
                  onMouseLeave={closeKeywordTooltip}
                >
                  <strong>분위기</strong>
                  <p>{selectedRecord?.mood_tags.join(', ') || '없음'}</p>
                </div>
                <div
                  className="mood-card history-keyword-card"
                  onMouseEnter={(event) =>
                    openKeywordTooltip('검색어', selectedRecord?.search_keywords.join(', ') || '없음', event)
                  }
                  onMouseMove={(event) =>
                    moveKeywordTooltip(selectedRecord?.search_keywords.join(', ') || '없음', event)
                  }
                  onMouseLeave={closeKeywordTooltip}
                >
                  <strong>검색어</strong>
                  <p>{selectedRecord?.search_keywords.join(', ') || '없음'}</p>
                </div>
              </section>
            </div>
            {keywordTooltip && (
              <div
                className="keyword-floating-tooltip"
                style={{
                  left: keywordTooltip.left,
                  top: keywordTooltip.top,
                }}
              >
                <span>{keywordTooltip.label}</span>
                <strong>{keywordTooltip.value}</strong>
              </div>
            )}
          </section>
          {renderPlayerBar()}
        </section>
      </main>
    )
  }

  return (


    <main className="app-shell">
      {!isResultView ? (
        <section className="start-screen" aria-labelledby="service-title">
          <div className="start-card">
            <button
              type="button"
              className="eyebrow eyebrow-button"
              onMouseEnter={scheduleAnalysisModalOpen}
              onMouseLeave={closeAnalysisModal}
            >
              Mood based music recommendation
            </button>
            {renderAuthControls()}
            {authError && <p className="auth-error">{authError}</p>}
            {renderEnvironmentBadge()}
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
              {renderSearchScopeSwitch()}
              <button type="submit" disabled={!inputText.trim()}>
                {isLoading ? '분석 중...' : '음악 추천 받기'}
              </button>
              {errorMessage && <p className="error-message">{errorMessage}</p>}
            </form>
          </div>
        </section>
      ) : (
        <section className="music-dashboard search-dashboard" aria-labelledby="result-title">
          <aside className="dashboard-sidebar search-sidebar">
            <div className="history-sidebar-top">
              <button type="button" className="sidebar-logo-button" onClick={openSearchMode}>
                Moodify
              </button>
              <button type="button" className="sidebar-history-button" onClick={openHistoryMode}>
                기록 보기
              </button>
            </div>
            {renderRecommendationTabs('sidebar')}
          </aside>
          <section className="dashboard-main search-main">
            <div className="screen-toolbar">
              <button
                type="button"
                className="eyebrow eyebrow-button"
                onMouseEnter={scheduleAnalysisModalOpen}
                onMouseLeave={closeAnalysisModal}
              >
                Mood based music recommendation
              </button>
              {renderAuthControls()}
              {renderEnvironmentBadge()}
            </div>
            <form className="result-search-form" onSubmit={handleSubmit}>
              <label htmlFor="result-mood-search" onClick={openSearchMode}>
                Search music
              </label>
              <input
                id="result-mood-search"
                value={inputText}
                onChange={(event) => setInputText(event.target.value)}
                placeholder="현재의 기분을 입력해주세요"
              />
              {renderSearchScopeSwitch()}
              <button type="submit" disabled={!inputText.trim() || isLoading}>
                {isLoading ? '분석 중' : 'Search'}
              </button>
            </form>

            <section className="recommendation-area" aria-label="추천 음악 결과">
              <h1 id="result-title">{selectedTab === 'track' ? 'Explore new' : 'Playlists'}</h1>
              {selectedTab === 'track' ? (
                <div
                  className="track-grid draggable-rail"
                  ref={trackRailRef}
                  onPointerCancel={(event) => stopDrag(event, trackRailRef.current)}
                  onPointerDown={(event) => startDrag(event, trackRailRef.current)}
                  onPointerLeave={(event) => stopDrag(event, trackRailRef.current)}
                  onPointerMove={(event) => moveDrag(event, trackRailRef.current)}
                  onPointerUp={(event) => stopDrag(event, trackRailRef.current)}
                >
                  {recommendedTracks.map((track) => (
                    <div
                      role="button"
                      tabIndex={0}
                      className={`track-card ${activeTrack?.id === track.id ? 'active' : ''}`}
                      key={track.id}
                      onClick={() => selectTrackOnClick(track.id)}
                      onPointerDown={rememberCardPressStart}
                      onPointerUp={(event) => selectTrackOnPointerUp(event, track.id)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          selectTrack(track.id)
                        }
                      }}
                    >
                      {track.thumbnail_url && <img src={track.thumbnail_url} alt="" />}
                      <h3>{track.title}</h3>
                      <p>{track.channel_title}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div
                  className="playlist-card-grid draggable-rail"
                  ref={playlistRailRef}
                  onPointerCancel={(event) => stopDrag(event, playlistRailRef.current)}
                  onPointerDown={(event) => startDrag(event, playlistRailRef.current)}
                  onPointerLeave={(event) => stopDrag(event, playlistRailRef.current)}
                  onPointerMove={(event) => moveDrag(event, playlistRailRef.current)}
                  onPointerUp={(event) => stopDrag(event, playlistRailRef.current)}
                >
                  {recommendedPlaylists.map((playlist, index) => (
                    <div
                      role="button"
                      tabIndex={0}
                      className={`playlist-card ${activePlaylist?.id === playlist.id ? 'active' : ''}`}
                      key={playlist.id}
                      onClick={() => selectPlaylistOnClick(playlist.id)}
                      onPointerDown={rememberCardPressStart}
                      onPointerUp={(event) => selectPlaylistOnPointerUp(event, playlist.id)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          selectPlaylist(playlist.id)
                        }
                      }}
                    >
                      {playlist.thumbnail_url ? (
                        <img src={playlist.thumbnail_url} alt="" />
                      ) : (
                        <span className="playlist-fallback">{index + 1}</span>
                      )}
                      <h3>{playlist.title}</h3>
                      <p>{playlist.channel_title}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <div className="detail-grid">
              <section className="selected-track-section" aria-label="선택한 대표곡">
                <h2>Popular</h2>
                <article className="selected-track-card">
                  {selectedCardImage && (
                    <img src={selectedCardImage} alt="" className="selected-track-image" />
                  )}
                  <div>
                    {selectedTab === 'track' && <p className="card-type">Selected track</p>}
                    <a
                      href={selectedCardUrl}
                      className="selected-track-title-link"
                      target="_blank"
                      rel="noreferrer"
                    >
                      <h3>{selectedCardTitle}</h3>
                    </a>
                    <p className="channel-name">{selectedCardSubtitle}</p>
                    {selectedTab === 'playlist' && (
                      <div
                        className="playlist-track-scroll draggable-rail vertical-rail"
                        ref={playlistTrackScrollRef}
                        onPointerCancel={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerDown={(event) => startPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerLeave={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerMove={(event) => movePlaylistDrag(event, playlistTrackScrollRef.current)}
                        onPointerUp={(event) => stopPlaylistDrag(event, playlistTrackScrollRef.current)}
                      >
                        <ol className="sample-track-list playlist-track-list">
                          {playlistTrackItems.map((track, index) => (
                            <li
                              key={`${activeRecommendation?.id ?? 'playlist'}-${index}-${track}`}
                              className={index === activePlaylistTrackIndex ? 'active' : ''}
                              ref={(node) => {
                                playlistTrackItemRefs.current[index] = node
                              }}
                              role="button"
                              tabIndex={0}
                              onClick={() => playPlaylistTrack(index)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter' || event.key === ' ') {
                                  playPlaylistTrack(index)
                                }
                              }}
                            >
                              {track.thumbnail_url ? (
                                <img className="playlist-track-thumb" src={track.thumbnail_url} alt="" />
                              ) : (
                                <span className="playlist-track-number">{index + 1}</span>
                              )}
                              <span className="playlist-track-title">{track.title}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                </article>
              </section>
              <section className="mood-panel" aria-label="추천 키워드">
                <h2>Keywords</h2>
                {moodHighlights.map((tag) => (
                  <div className="mood-card" key={tag}>
                    <strong>{tag}</strong>
                  </div>
                ))}
              </section>
            </div>
          </section>
          {renderPlayerBar()}
        </section>
      )}
      {isAnalysisModalOpen && renderAnalysisModal()}
    </main>
  )
}

export default App




