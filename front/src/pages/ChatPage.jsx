import { useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import logo from '../icons/iust_logo.png'
import newChatIcon from '../icons/new-chat.svg'
import sendIcon from '../icons/send.png'
import MicrophoneButton from '../components/MicrophoneButton'
import '../App.css'

const WELCOME_MESSAGE =
  'به دستیار هوشمند آموزش دانشگاه علم و صنعت ایران خوش آمدید، لطفا سوال خود را بپرسید'

const getDirection = (text) => {
  const rtlMatches = text.match(
    /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g,
  )
  const ltrMatches = text.match(/[A-Za-z]/g)
  const rtlCount = rtlMatches ? rtlMatches.length : 0
  const ltrCount = ltrMatches ? ltrMatches.length : 0

  if (rtlCount === 0 && ltrCount === 0) {
    return 'rtl'
  }
  if (rtlCount === ltrCount) {
    return rtlCount > 0 ? 'rtl' : 'ltr'
  }
  return rtlCount > ltrCount ? 'rtl' : 'ltr'
}

const normalizeAnswer = (text) => {
  if (!text) {
    return text
  }

  return text
    .replace(/&lt;\s*br\s*\/?&gt;/gi, '\n')
    .replace(/<\s*br\s*\/?>/gi, '\n')
    .replace(/\n{3,}/g, '\n\n')
}

function ChatPage() {
  const [inputValue, setInputValue] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [toastMessage, setToastMessage] = useState('')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [chatSessions, setChatSessions] = useState([])

  const inputDirection = useMemo(() => getDirection(inputValue), [inputValue])
  const showWelcome = messages.length === 0

  const fetchSessions = async (userUuid) => {
    try {
      const response = await fetch(`/chat/sessions/${userUuid}/details`)
      if (!response.ok) {
        throw new Error('Failed to load sessions')
      }
      const data = await response.json()
      setChatSessions(Array.isArray(data?.sessions) ? data.sessions : [])
    } catch (error) {
      setChatSessions([])
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed || isLoading) {
      return
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: trimmed,
      dir: getDirection(trimmed),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    const userUuid = localStorage.getItem('user_uuid')
    if (!userUuid) {
      showToast('ابتدا وارد حساب کاربری شوید.')
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch('/chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_uuid: userUuid,
          message: trimmed,
        }),
      })

      if (!response.ok) {
        throw new Error('Request failed')
      }

      const data = await response.json()
      const answerText = normalizeAnswer(data?.answer ?? 'پاسخی دریافت نشد.')
      const assistantMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: answerText,
        dir: getDirection(answerText),
      }

      setMessages((prev) => [...prev, assistantMessage])
      await fetchSessions(userUuid)
    } catch (error) {
      const errorMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'خطا در دریافت پاسخ. لطفا دوباره تلاش کنید.',
        dir: 'rtl',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const showToast = (message) => {
    setToastMessage(message)
    setTimeout(() => {
      setToastMessage('')
    }, 3000)
  }

  const handleTranscription = (transcription) => {
    setInputValue(transcription)
  }

  const handleAsrError = (message) => {
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: message,
        dir: 'rtl',
      },
    ])
  }

  const handleLimitReached = () => {
    showToast('شما حداکثر میتوانید 30 ثانیه صدای خود را ضبط کنید.')
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit(event)
    }
  }

  useEffect(() => {
    const userUuid = localStorage.getItem('user_uuid')
    if (!userUuid) {
      return
    }

    fetchSessions(userUuid)
  }, [])

  return (
    <div className={`app chat-app${isSidebarOpen ? ' sidebar-open' : ''}`}>
      {toastMessage && (
        <div className="toast" role="status" aria-live="polite" dir="rtl">
          {toastMessage}
        </div>
      )}
      <button
        className="sidebar-toggle"
        type="button"
        onClick={() => setIsSidebarOpen((prev) => !prev)}
        aria-label={isSidebarOpen ? 'بستن سایدبار' : 'باز کردن سایدبار'}
      >
        {isSidebarOpen ? '<' : '>'}
      </button>
      {!showWelcome && (
        <img className="corner-logo" src={logo} alt="IUST logo" />
      )}
      <div className="chat-layout">
        <aside className="chat-sidebar" aria-hidden={!isSidebarOpen}>
          <div className="chat-sidebar-inner">
            <button className="sidebar-new-chat" type="button">
              <img src={newChatIcon} alt="" aria-hidden="true" />
              گفتگوی جدید
            </button>
            <div className="sidebar-chats">
              {chatSessions.map((session) => (
                <button
                  key={session.chat_id}
                  className="sidebar-chat-item"
                  type="button"
                >
                  {session.title || 'گفتگوی بدون عنوان'}
                </button>
              ))}
            </div>
          </div>
        </aside>
        <main className="chat chat-content">
          <div
            className={`chat-messages${showWelcome ? ' chat-messages-empty' : ''}`}
          >
            {showWelcome && (
              <div className="welcome-title" dir="rtl">
                <img
                  className="welcome-logo-large"
                  src={logo}
                  alt="IUST logo"
                />
                <p className="welcome-text">{WELCOME_MESSAGE}</p>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message message-${message.role}`}
                dir={message.dir}
              >
                <div className="message-text">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ node, ...props }) => (
                        <a {...props} target="_blank" rel="noopener noreferrer" />
                      ),
                    }}
                  >
                    {message.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message message-assistant" dir="rtl">
                <div className="typing-indicator" aria-label="در حال تایپ">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
          </div>

          <form className="chat-input" onSubmit={handleSubmit}>
            <MicrophoneButton
              isDisabled={isLoading}
              onTranscription={handleTranscription}
              onError={handleAsrError}
              onLimitReached={handleLimitReached}
            />
            <input
              className="chat-textarea"
              type="text"
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="سوال خود را اینجا بنویسید یا به انگلیسی تایپ کنید..."
              dir={inputDirection}
            />
            <button
              className="chat-submit"
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              aria-label="ارسال"
            >
              {isLoading ? (
                '...'
              ) : (
                <img
                  className="chat-submit-icon"
                  src={sendIcon}
                  alt=""
                  aria-hidden="true"
                />
              )}
            </button>
          </form>
        </main>
      </div>
    </div>
  )
}

export default ChatPage


