import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Award, 
  CheckCircle, 
  AlertTriangle,
  Download,
  Share2,
  RefreshCw
} from 'lucide-react';
import { useApp } from '../context/AppContext';

const Results = () => {
  const { state, resetState } = useApp();
  const [results, setResults] = useState(null);

  useEffect(() => {
    // In a real app, fetch results from API
    // For demo, create mock results
    const mockResults = {
      scores: {
        overall: 78,
        technical: 82,
        communication: 75,
        problem_solving: 80,
        cultural_fit: 73
      },
      feedback: {
        strengths: [
          'Clear communication skills',
          'Strong technical knowledge',
          'Good problem-solving approach',
          'Relevant experience examples'
        ],
        improvements: [
          'Provide more specific metrics',
          'Practice behavioral questions',
          'Be more concise in explanations',
          'Show more enthusiasm'
        ],
        overall: 'Great performance! You demonstrated solid technical skills and clear communication. Focus on providing more specific examples with quantifiable results to strengthen your answers.'
      },
      performance_by_question: [
        { question: 1, score: 85, feedback: 'Excellent technical explanation' },
        { question: 2, score: 72, feedback: 'Good approach, could be more specific' },
        { question: 3, score: 78, feedback: 'Clear communication, good examples' },
        { question: 4, score: 80, feedback: 'Strong problem-solving skills shown' },
        { question: 5, score: 75, feedback: 'Good answer, could show more enthusiasm' }
      ]
    };
    
    setResults(mockResults);
  }, []);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  const handleStartNewInterview = () => {
    resetState();
  };

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce-subtle">📊</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Calculating Your Results
          </h2>
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="text-6xl mb-6">🎉</div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Interview Complete!
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Here's your detailed performance analysis and feedback
          </p>
        </motion.div>

        {/* Overall Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-8 mb-8 text-center"
        >
          <div className="flex items-center justify-center mb-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  className="text-gray-200"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 40}`}
                  strokeDashoffset={`${2 * Math.PI * 40 * (1 - results.scores.overall / 100)}`}
                  className="text-primary-600 transition-all duration-1000 ease-out"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-bold text-gray-900">
                  {results.scores.overall}%
                </span>
              </div>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Overall Score: {getScoreLabel(results.scores.overall)}
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            {results.feedback.overall}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Detailed Scores */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-8"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2" />
              Performance Breakdown
            </h3>
            
            <div className="space-y-6">
              {Object.entries(results.scores).filter(([key]) => key !== 'overall').map(([category, score]) => (
                <div key={category}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {category.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${getScoreColor(score)}`}>
                      {score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${score}%` }}
                      transition={{ delay: 0.5, duration: 1 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Question Performance */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-8"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2" />
              Question by Question
            </h3>
            
            <div className="space-y-4">
              {results.performance_by_question.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <span className="font-medium text-gray-900">Question {item.question}</span>
                    <p className="text-sm text-gray-600">{item.feedback}</p>
                  </div>
                  <span className={`px-3 py-1 text-sm rounded-full font-medium ${getScoreColor(item.score)}`}>
                    {item.score}%
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Strengths */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-8 bg-green-50 border-green-200"
          >
            <h3 className="text-xl font-bold text-green-800 mb-6 flex items-center">
              <CheckCircle className="w-6 h-6 mr-2" />
              Your Strengths
            </h3>
            
            <ul className="space-y-3">
              {results.feedback.strengths.map((strength, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="flex items-start space-x-3"
                >
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-green-800">{strength}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* Areas for Improvement */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="card p-8 bg-orange-50 border-orange-200"
          >
            <h3 className="text-xl font-bold text-orange-800 mb-6 flex items-center">
              <AlertTriangle className="w-6 h-6 mr-2" />
              Areas for Improvement
            </h3>
            
            <ul className="space-y-3">
              {results.feedback.improvements.map((improvement, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  className="flex items-start space-x-3"
                >
                  <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                  <span className="text-orange-800">{improvement}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card p-8 text-center"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6">What's Next?</h3>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/upload">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleStartNewInterview}
                className="btn-primary flex items-center space-x-2"
              >
                <RefreshCw className="w-5 h-5" />
                <span>Practice Again</span>
              </motion.button>
            </Link>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="btn-secondary flex items-center space-x-2"
            >
              <Download className="w-5 h-5" />
              <span>Download Report</span>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="btn-secondary flex items-center space-x-2"
            >
              <Share2 className="w-5 h-5" />
              <span>Share Results</span>
            </motion.button>
          </div>
          
          <div className="mt-8 p-6 bg-primary-50 rounded-lg">
            <Award className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Keep Practicing!
            </h4>
            <p className="text-gray-600">
              Regular practice leads to improvement. Try interviewing for different roles to expand your skills.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Results;