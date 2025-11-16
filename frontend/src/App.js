import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ResumeUpload from './pages/ResumeUpload';
import JobSearch from './pages/JobSearch';
import Interview from './pages/Interview';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import { AppProvider } from './context/AppContext';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate initial app loading
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce-subtle">🎤</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Mock Interview System</h1>
          <div className="flex items-center justify-center space-x-1">
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <AppProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          
          <main className="pt-16">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<ResumeUpload />} />
              <Route path="/jobs" element={<JobSearch />} />
              <Route path="/interview" element={<Interview />} />
              <Route path="/results" element={<Results />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </main>
          
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#fff',
                color: '#374151',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                border: '1px solid #e5e7eb',
              },
            }}
          />
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;