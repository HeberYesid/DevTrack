import { useState, useEffect } from "react"
import { useAuth } from "../state/AuthContext"
import { useNavigate, useLocation, Link } from "react-router-dom"
import TurnstileCaptcha from "./TurnstileCaptcha"

export default function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [message, setMessage] = useState("")
  const [showVerifyLink, setShowVerifyLink] = useState(false)
  const [turnstileToken, setTurnstileToken] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || "/"

  useEffect(() => {
    if (location.state?.message) {
      setMessage(location.state.message)
    }
    if (location.state?.email) {
      setEmail(location.state.email)
    }
  }, [location.state])

  async function onSubmit(e) {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    if (!turnstileToken) {
      setError("Por favor completa la verificación de seguridad.")
      setIsLoading(false)
      return
    }

    try {
      await login(email, password, turnstileToken)
      navigate(from)
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail || "Error al iniciar sesión"
      setError(errorMessage)

      if (errorMessage.includes("verificar tu correo")) {
        setShowVerifyLink(true)
      }

      setTurnstileToken("")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <img
          src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
          alt="DevTrack"
          className="mx-auto h-10 w-auto"
        />
        <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-white">
          Ingresa a tu cuenta
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <form onSubmit={onSubmit} className="space-y-6">
          {/* Input correo */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-100"
            >
              Correo
            </label>
            <div className="mt-2">
              <input
                id="email"
                type="email"
                name="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white 
                           outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 
                           focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 
                           sm:text-sm"
              />
            </div>
          </div>

          {/* Input contraseña */}
          <div>
            <div className="flex items-center justify-between">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-100"
              >
                Contraseña
              </label>
              <div className="text-sm">
                <a
                  href="#"
                  className="font-semibold text-indigo-400 hover:text-indigo-300"
                >
                  ¿Olvidaste la contraseña?
                </a>
              </div>
            </div>
            <div className="mt-2">
              <input
                id="password"
                type="password"
                name="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white 
                           outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 
                           focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 
                           sm:text-sm"
              />
            </div>
          </div>

          {/* Captcha */}
          <div>
            <TurnstileCaptcha
              onVerify={setTurnstileToken}
              onError={() => setTurnstileToken("")}
              onExpire={() => setTurnstileToken("")}
            />
          </div>

          {/* Botón */}
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 
                         text-sm font-semibold text-white hover:bg-indigo-400 
                         focus-visible:outline focus-visible:outline-2 
                         focus-visible:outline-offset-2 focus-visible:outline-indigo-500
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Iniciando sesión..." : "Ingresar"}
            </button>
          </div>

          {/* Mensajes */}
          {message && (
            <div className="rounded-md bg-green-500/10 p-3 text-sm text-green-400">
              ✅ {message}
            </div>
          )}

          {error && (
            <div className="rounded-md bg-red-500/10 p-3 text-sm text-red-400">
              ❌ {error}
              {showVerifyLink && (
                <div className="mt-2">
                  <Link
                    to="/verify-code"
                    state={{ email }}
                    className="font-semibold text-indigo-400 hover:text-indigo-300"
                  >
                    📧 Verificar mi correo con código
                  </Link>
                </div>
              )}
            </div>
          )}
        </form>

        <p className="mt-10 text-center text-sm text-gray-400">
          ¿No tienes cuenta?{" "}
          <Link
            to="/register"
            className="font-semibold text-indigo-400 hover:text-indigo-300"
          >
            Regístrate aquí
          </Link>
        </p>
      </div>
    </div>
  )
}

