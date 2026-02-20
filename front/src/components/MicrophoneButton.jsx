import { useRef, useState } from 'react'
import activeMicIcon from '../icons/active-microphone.svg'
import inactiveMicIcon from '../icons/deactive-microphone.svg'
import './MicrophoneButton.css'

const DEFAULT_MAX_DURATION_MS = 30000
const DEFAULT_LANGUAGE = 'fa-IR'

const MicrophoneButton = ({
  isDisabled = false,
  maxDurationMs = DEFAULT_MAX_DURATION_MS,
  language = DEFAULT_LANGUAGE,
  onTranscription,
  onError,
  onLimitReached,
}) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const recordingTimerRef = useRef(null)

  const requestTranscription = async (audioBlob) => {
    setIsTranscribing(true)
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'recording.webm')
      const response = await fetch(`/chat/asr?language=${encodeURIComponent(language)}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('ASR request failed')
      }

      const data = await response.json()
      const transcription = data?.transcription?.trim()
      if (transcription && onTranscription) {
        onTranscription(transcription)
      }
    } catch (error) {
      if (onError) {
        onError('خطا در تبدیل گفتار به متن. لطفا دوباره تلاش کنید.')
      }
    } finally {
      setIsTranscribing(false)
    }
  }

  const stopRecording = () => {
    if (recordingTimerRef.current) {
      clearTimeout(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
    const recorder = mediaRecorderRef.current
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop()
    }
  }

  const startRecording = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('Media devices not supported')
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunksRef.current = []

      recorder.addEventListener('dataavailable', (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      })

      recorder.addEventListener('stop', async () => {
        setIsRecording(false)
        if (recordingTimerRef.current) {
          clearTimeout(recordingTimerRef.current)
          recordingTimerRef.current = null
        }
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        chunksRef.current = []
        stream.getTracks().forEach((track) => track.stop())
        await requestTranscription(audioBlob)
      })

      recorder.start()
      mediaRecorderRef.current = recorder
      setIsRecording(true)
      recordingTimerRef.current = setTimeout(() => {
        stopRecording()
        if (onLimitReached) {
          onLimitReached()
        }
      }, maxDurationMs)
    } catch (error) {
      setIsRecording(false)
      if (onError) {
        onError('دسترسی به میکروفون ممکن نیست. لطفا مجوز را بررسی کنید.')
      }
    }
  }

  const handleMicClick = () => {
    if (isDisabled || isTranscribing) {
      return
    }
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <button
      className={`chat-mic${isRecording ? ' chat-mic-recording' : ''}`}
      type="button"
      onClick={handleMicClick}
      disabled={isDisabled || isTranscribing}
      aria-label={isRecording ? 'توقف ضبط صدا' : 'شروع ضبط صدا'}
    >
      {isTranscribing ? (
        <span className="mic-spinner" aria-hidden="true" />
      ) : (
        <img
          className="mic-icon"
          src={isRecording ? inactiveMicIcon : activeMicIcon}
          alt=""
          aria-hidden="true"
        />
      )}
    </button>
  )
}

export default MicrophoneButton

