import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  user: null,
  resume: null,
  selectedJob: null,
  interview: null,
  results: null,
  currentStep: 1, // 1: Upload, 2: Jobs, 3: Interview, 4: Results
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_RESUME':
      return { ...state, resume: action.payload, currentStep: 2 };
    case 'SET_SELECTED_JOB':
      return { ...state, selectedJob: action.payload, currentStep: 3 };
    case 'SET_INTERVIEW':
      return { ...state, interview: action.payload };
    case 'SET_RESULTS':
      return { ...state, results: action.payload, currentStep: 4 };
    case 'RESET_STATE':
      return initialState;
    case 'SET_STEP':
      return { ...state, currentStep: action.payload };
    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const value = {
    state,
    dispatch,
    setUser: (user) => dispatch({ type: 'SET_USER', payload: user }),
    setResume: (resume) => dispatch({ type: 'SET_RESUME', payload: resume }),
    setSelectedJob: (job) => dispatch({ type: 'SET_SELECTED_JOB', payload: job }),
    setInterview: (interview) => dispatch({ type: 'SET_INTERVIEW', payload: interview }),
    setResults: (results) => dispatch({ type: 'SET_RESULTS', payload: results }),
    resetState: () => dispatch({ type: 'RESET_STATE' }),
    setStep: (step) => dispatch({ type: 'SET_STEP', payload: step }),
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
