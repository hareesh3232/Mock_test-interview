import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mic, Home, Upload, Search, MessageCircle, BarChart3 } from 'lucide-react';
import { useApp } from '../context/AppContext';

const Header = () => {
  const location = useLocation();
  const { state } = useApp();

  const navItems = [
    { name: 'Home', path: '/', icon: Home },
    { name: 'Upload', path: '/upload', icon: Upload, step: 1 },
    { name: 'Jobs', path: '/jobs', icon: Search, step: 2 },
    { name: 'Interview', path: '/interview', icon: MessageCircle, step: 3 },
    { name: 'Results', path: '/results', icon: BarChart3, step: 4 },
  ];

  const isActive = (path) => location.pathname === path;
  const isAccessible = (step) => !step || state.currentStep >= step;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center">
              <Mic className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Mock Interview</h1>
              <p className="text-xs text-gray-500 -mt-1">AI-Powered System</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const accessible = isAccessible(item.step);
              
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`
                    relative flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200
                    ${isActive(item.path)
                      ? 'bg-primary-100 text-primary-700'
                      : accessible
                        ? 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        : 'text-gray-400 cursor-not-allowed'
                    }
                    ${!accessible && 'pointer-events-none'}
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{item.name}</span>
                  
                  {/* Step indicator */}
                  {item.step && (
                    <div className={`
                      absolute -top-1 -right-1 w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold
                      ${state.currentStep >= item.step
                        ? 'bg-green-500 text-white'
                        : state.currentStep === item.step - 1
                          ? 'bg-primary-500 text-white animate-pulse'
                          : 'bg-gray-300 text-gray-600'
                      }
                    `}>
                      {state.currentStep > item.step ? '✓' : item.step}
                    </div>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-gray-200">
        <div 
          className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500 ease-out"
          style={{ width: `${(state.currentStep / 4) * 100}%` }}
        />
      </div>
    </header>
  );
};

export default Header;