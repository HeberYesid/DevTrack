import { Link } from "react-router-dom"
import './Index.css'


export default function Index() {
  return (
    <div className="bg-gray-50 min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="flex justify-between items-center px-10 py-5 bg-white shadow-md">
        <h1 className="text-2xl font-bold text-indigo-600">DevTrack</h1>
        <nav className="space-x-6">
          <a href="#features" className="text-gray-700 hover:text-indigo-600">Características</a>
          <a href="#about" className="text-gray-700 hover:text-indigo-600">Acerca</a>
          <a href="#contact" className="text-gray-700 hover:text-indigo-600">Contacto</a>
          <a href="/login" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Iniciar Sesión</a>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-6">
        <h2 className="text-5xl font-extrabold text-gray-800 leading-tight">
          Bienvenido a <span className="text-indigo-600">DevTrack</span>
        </h2>
        <p className="mt-4 text-lg text-gray-600 max-w-2xl">
          Una plataforma para gestionar tus proyectos de software de manera sencilla, rápida y colaborativa.
        </p>
        <div className="mt-6 flex gap-4">
          <a href="/register" className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700">
            ¡Empieza Ahora!
          </a>
          <a href="#features" className="px-6 py-3 border border-gray-400 rounded-xl hover:bg-gray-100">
            Ver más
          </a>
        </div>
      </main>

      {/* Features */}
      <section id="features" className="py-16 px-8 bg-white">
        <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">Características</h3>
        <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
          <div className="p-6 rounded-xl shadow hover:shadow-lg transition">
            <h4 className="text-xl font-semibold text-indigo-600">Gestión de Tareas</h4>
            <p className="text-gray-600 mt-2">Organiza tus tareas con tableros Kanban y listas.</p>
          </div>
          <div className="p-6 rounded-xl shadow hover:shadow-lg transition">
            <h4 className="text-xl font-semibold text-indigo-600">Colaboración en Equipo</h4>
            <p className="text-gray-600 mt-2">Invita a tu equipo y trabaja en tiempo real.</p>
          </div>
          <div className="p-6 rounded-xl shadow hover:shadow-lg transition">
            <h4 className="text-xl font-semibold text-indigo-600">Estadísticas</h4>
            <p className="text-gray-600 mt-2">Visualiza el progreso con reportes y gráficas.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-100 py-6 text-center text-gray-600 mt-auto">
        © {new Date().getFullYear()} DevTrack. Todos los derechos reservados.
      </footer>
    </div>
  );
}
