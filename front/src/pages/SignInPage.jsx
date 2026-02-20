import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import logo from '../icons/iust_logo.png'
import './Auth.css'

const getErrorMessage = async (response) => {
  try {
    const data = await response.json()
    if (data?.detail) {
      return data.detail
    }
  } catch (error) {
    return 'خطا در ارتباط با سرور.'
  }
  return 'ورود انجام نشد. لطفا دوباره تلاش کنید.'
}

function SignInPage() {
  const navigate = useNavigate()
  const [studentId, setStudentId] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [toastMessage, setToastMessage] = useState('')

  const showToast = (message) => {
    setToastMessage(message)
    setTimeout(() => {
      setToastMessage('')
    }, 5000)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!studentId.trim() || !password) {
      showToast('شماره دانشجویی و رمز عبور الزامی است.')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId.trim(),
          password,
        }),
      })

      if (!response.ok) {
        throw new Error(await getErrorMessage(response))
      }

      const data = await response.json()
      if (data?.access_token) {
        localStorage.setItem('access_token', data.access_token)
      }
      if (data?.user_uuid) {
        localStorage.setItem('user_uuid', data.user_uuid)
      }
      navigate('/chat', { replace: true })
    } catch (error) {
      showToast(error?.message ?? 'ورود انجام نشد.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {toastMessage && (
        <div className="auth-toast" role="status" aria-live="polite" dir="rtl">
          <span>{toastMessage}</span>
          <button
            className="auth-toast-close"
            type="button"
            onClick={() => setToastMessage('')}
            aria-label="بستن پیام"
          >
            ×
          </button>
        </div>
      )}
      <div className="auth-card">
        <img className="auth-logo" src={logo} alt="IUST logo" />
        <h1 className="auth-title" dir="rtl">
          ورود به حساب
        </h1>
        <p className="auth-subtitle" dir="rtl">
          شماره دانشجویی و رمز عبور را وارد کنید.
        </p>

        <form className="auth-form" onSubmit={handleSubmit} dir="rtl">
          <label className="auth-label">
            شماره دانشجویی
            <input
              className="auth-input"
              type="text"
              value={studentId}
              onChange={(event) => setStudentId(event.target.value)}
              placeholder="مثال: 40123456"
            />
          </label>
          <label className="auth-label">
            رمز عبور
            <input
              className="auth-input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="رمز عبور"
            />
          </label>

          <button className="auth-submit" type="submit" disabled={isLoading}>
            {isLoading ? 'در حال ورود...' : 'ورود'}
          </button>
        </form>

        <p className="auth-footer" dir="rtl">
          حساب ندارید؟ <Link to="/signup">ثبت نام کنید</Link>
        </p>
      </div>
    </div>
  )
}

export default SignInPage


