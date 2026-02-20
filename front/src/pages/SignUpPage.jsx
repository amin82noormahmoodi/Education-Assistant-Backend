import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import logo from '../icons/iust_logo.png'
import eyeOpen from '../icons/eye-open.svg'
import eyeClosed from '../icons/eye-closed.svg'
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
  return 'ثبت نام انجام نشد. لطفا دوباره تلاش کنید.'
}

function SignUpPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState('form')
  const [studentId, setStudentId] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
  const [otpCode, setOtpCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [toastMessage, setToastMessage] = useState('')

  const showToast = (message) => {
    setToastMessage(message)
    setTimeout(() => {
      setToastMessage('')
    }, 5000)
  }

  const handleStart = async (event) => {
    event.preventDefault()
    if (!studentId.trim() || !email.trim() || !password || !passwordConfirm) {
      showToast('همه فیلدها الزامی است.')
      return
    }
    if (password !== passwordConfirm) {
      showToast('رمز عبور و تکرار آن یکسان نیست.')
      return
    }

    setIsLoading(true)
    setSuccessMessage('')

    try {
      const response = await fetch('/auth/signup/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId.trim(),
          email: email.trim(),
          password,
          password_confirm: passwordConfirm,
        }),
      })

      if (!response.ok) {
        throw new Error(await getErrorMessage(response))
      }

      setStep('otp')
      showToast('کد تایید برای ایمیل شما ارسال شد.')
    } catch (error) {
      showToast(error?.message ?? 'ثبت نام انجام نشد.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerify = async (event) => {
    event.preventDefault()
    if (!otpCode.trim()) {
      showToast('کد تایید الزامی است.')
      return
    }

    setIsLoading(true)
    setSuccessMessage('')

    try {
      const response = await fetch('/auth/signup/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId.trim(),
          otp_code: otpCode.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error(await getErrorMessage(response))
      }

      await response.json()
      navigate('/signin', { replace: true })
    } catch (error) {
      showToast(error?.message ?? 'تایید انجام نشد.')
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

        {step === 'form' ? (
          <form className="auth-form" onSubmit={handleStart} dir="rtl">
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
              ایمیل
              <input
                className="auth-input"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="email@example.com"
              />
            </label>
            <label className="auth-label">
              رمز عبور
              <div className="auth-input-group">
                <input
                  className="auth-input auth-input-with-icon"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="حداقل ۶ کاراکتر"
                />
                <button
                  className="auth-input-toggle"
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? 'پنهان کردن رمز عبور' : 'نمایش رمز عبور'}
                >
                  <img
                    src={showPassword ? eyeClosed : eyeOpen}
                    alt=""
                    aria-hidden="true"
                  />
                </button>
              </div>
            </label>
            <label className="auth-label">
              تکرار رمز عبور
              <div className="auth-input-group">
                <input
                  className="auth-input auth-input-with-icon"
                  type={showPasswordConfirm ? 'text' : 'password'}
                  value={passwordConfirm}
                  onChange={(event) => setPasswordConfirm(event.target.value)}
                  placeholder="تکرار رمز عبور"
                />
                <button
                  className="auth-input-toggle"
                  type="button"
                  onClick={() => setShowPasswordConfirm((prev) => !prev)}
                  aria-label={
                    showPasswordConfirm
                      ? 'پنهان کردن تکرار رمز عبور'
                      : 'نمایش تکرار رمز عبور'
                  }
                >
                  <img
                    src={showPasswordConfirm ? eyeClosed : eyeOpen}
                    alt=""
                    aria-hidden="true"
                  />
                </button>
              </div>
            </label>

            <button className="auth-submit" type="submit" disabled={isLoading}>
              {isLoading ? 'در حال ارسال...' : 'مرحله بعدی'}
            </button>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleVerify} dir="rtl">
            <label className="auth-label">
              کد تایید
              <input
                className="auth-input auth-otp"
                type="text"
                value={otpCode}
                onChange={(event) => setOtpCode(event.target.value)}
                placeholder="کد ۶ رقمی"
              />
            </label>

            <button className="auth-submit" type="submit" disabled={isLoading}>
              {isLoading ? 'در حال تایید...' : 'تایید'}
            </button>
            <button
              className="auth-secondary"
              type="button"
              onClick={() => setStep('form')}
            >
              بازگشت
            </button>
          </form>
        )}

        <p className="auth-footer" dir="rtl">
          حساب دارید؟ <Link to="/signin">وارد شوید</Link>
        </p>
      </div>
    </div>
  )
}

export default SignUpPage


