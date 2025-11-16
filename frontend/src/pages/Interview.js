import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  MessageCircle, 
  Clock, 
  ChevronLeft, 
  ChevronRight, 
  CheckCircle,
  Loader2,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { generateInterviewQuestions, startInterview, submitInterviewAnswer } from '../services/api';

const Interview = () => {
  const navigate = useNavigate();
  const { state, setInterview, setResults } = useApp();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interviewId, setInterviewId] = useState(null);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes per question
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!state.resume) {
      toast.error('Please upload your resume first');
      navigate('/upload');
      return;
    }
    
    if (!state.selectedJob) {
      toast.error('Please select a job first');
      navigate('/jobs');
      return;
    }
    
    // If we already have questions, don't reinitialize
    if (questions.length > 0) {
      setIsLoading(false);
      return;
    }
    
    initializeInterview();
  }, [state.resume, state.selectedJob]);

  useEffect(() => {
    // Timer logic
    let interval = null;
    if (isTimerActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(time => time - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handleNextQuestion();
    }
    
    return () => clearInterval(interval);
  }, [isTimerActive, timeLeft]);

  const initializeInterview = async () => {
    setIsLoading(true);
    
    try {
      // Generate questions
      const questionsResponse = await generateInterviewQuestions(
        state.resume.resume_id,
        state.selectedJob.id,
        5
      );
      
      setQuestions(questionsResponse.questions);
      
      // Start interview session
      const interviewResponse = await startInterview(
        state.resume.resume_id,
        state.selectedJob.id,
        questionsResponse.questions
      );
      
      setInterviewId(interviewResponse.interview_id);
      setInterview(interviewResponse);
      
      // Start timer for first question
      setTimeLeft(300);
      setIsTimerActive(true);
      
      toast.success('Interview started! Good luck!');
      
    } catch (error) {
      toast.error(error.message || 'Failed to start interview');
      navigate('/jobs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (value) => {
    setCurrentAnswer(value);
    setAnswers({
      ...answers,
      [currentQuestionIndex]: value
    });
  };

  const handleNextQuestion = async () => {
    if (!currentAnswer.trim() && timeLeft > 0) {
      toast.error('Please provide an answer before proceeding');
      return;
    }

    setIsSubmitting(true);
    setIsTimerActive(false);

    try {
      const response = await submitInterviewAnswer(
        interviewId,
        currentQuestionIndex,
        currentAnswer || 'No answer provided (time expired)'
      );

      if (currentQuestionIndex < questions.length - 1) {
        // Move to next question
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setCurrentAnswer(answers[currentQuestionIndex + 1] || '');
        setTimeLeft(300);
        setIsTimerActive(true);
        toast.success('Answer saved!');
      } else {
        // Interview completed
        setResults(response);
        toast.success('Interview completed! Redirecting to results...');
        setTimeout(() => navigate('/results'), 1500);
      }
      
    } catch (error) {
      toast.error(error.message || 'Failed to submit answer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setIsTimerActive(false);
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setCurrentAnswer(answers[currentQuestionIndex - 1] || '');
      setTimeLeft(300);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return ((currentQuestionIndex + 1) / questions.length) * 100;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce-subtle">🤖</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Preparing Your Interview
          </h2>
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
            <span className="text-gray-600">Generating personalized questions...</span>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="text-6xl mb-4">💬</div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            Mock Interview
          </h1>
          <p className="text-lg text-gray-600">
            {state.selectedJob?.title} at {state.selectedJob?.company}
          </p>
        </motion.div>

        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6 mb-8"
        >
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-medium text-gray-600">
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className={`text-sm font-medium ${timeLeft < 60 ? 'text-red-600' : 'text-gray-600'}`}>
                {formatTime(timeLeft)}
              </span>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3">
            <motion.div
              className="bg-gradient-to-r from-primary-500 to-accent-500 h-3 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${getProgressPercentage()}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestionIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="card p-8 mb-8"
          >
            {/* Question Info */}
            <div className="flex flex-wrap gap-3 mb-6">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {currentQuestion?.type || 'General'}
              </span>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                {currentQuestion?.difficulty || 'Medium'}
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                {currentQuestion?.time_limit || 5} min
              </span>
            </div>

            {/* Question Text */}
            <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-6 leading-relaxed">
              {currentQuestion?.question}
            </h2>

            {/* Keywords Hint */}
            {currentQuestion?.expected_keywords && currentQuestion.expected_keywords.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-yellow-800 mb-2">Keywords to consider:</h4>
                    <div className="flex flex-wrap gap-2">
                      {currentQuestion.expected_keywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-yellow-100 text-yellow-800 text-sm rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Answer Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Your Answer
              </label>
              <textarea
                value={currentAnswer}
                onChange={(e) => handleAnswerChange(e.target.value)}
                className="w-full h-48 input-field resize-none"
                placeholder="Type your answer here... Be specific and provide examples when possible."
                disabled={isSubmitting}
              />
              <div className="mt-2 flex justify-between text-sm text-gray-500">
                <span>{currentAnswer.length} characters</span>
                <span>Aim for 100-300 words</span>
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handlePreviousQuestion}
                disabled={currentQuestionIndex === 0 || isSubmitting}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleNextQuestion}
                disabled={isSubmitting}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Submitting...</span>
                  </>
                ) : currentQuestionIndex === questions.length - 1 ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Finish Interview</span>
                  </>
                ) : (
                  <>
                    <span>Next Question</span>
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Interview Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6 bg-blue-50 border-blue-200"
        >
          <div className="flex items-start space-x-3">
            <MessageCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Interview Tips</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Be specific and provide concrete examples</li>
                <li>• Structure your answers using the STAR method (Situation, Task, Action, Result)</li>
                <li>• Take your time to think before answering</li>
                <li>• Show your problem-solving process</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Interview;