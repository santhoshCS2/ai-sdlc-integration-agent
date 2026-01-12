import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ROUTES } from './constants/routes';
import { AuthProvider } from './hooks/useAuth';
import { ThemeProvider } from './contexts/ThemeContext';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';

import Services from './pages/Services';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AuthGuard from './components/AuthGuard';
import PublicGuard from './components/PublicGuard';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="min-h-screen flex flex-col bg-black text-white transition-colors duration-300">
            <Header />
            <main className="flex-grow">
              <Routes>
                <Route path={ROUTES.HOME} element={<Home />} />
                <Route path={ROUTES.DASHBOARD} element={
                  <AuthGuard>
                    <Dashboard />
                  </AuthGuard>
                } />
                <Route path={ROUTES.SERVICES} element={<Services />} />
                <Route path={ROUTES.LOGIN} element={
                  <PublicGuard>
                    <Login />
                  </PublicGuard>
                } />
                <Route path={ROUTES.REGISTER} element={
                  <PublicGuard>
                    <Register />
                  </PublicGuard>
                } />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;