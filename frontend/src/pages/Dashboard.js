import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Award,
  Users,
  Clock
} from 'lucide-react';

const Dashboard = () => {
  // Mock data for dashboard
  const stats = {
    totalInterviews: 12,
    averageScore: 76,
    improvementRate: 15,
    timeSpent: 180 // minutes
  };

  const recentInterviews = [
    { id: 1, job: 'Frontend Developer', company: 'TechCorp', score: 82, date: '2024-01-15' },
    { id: 2, job: 'Full Stack Engineer', company: 'StartupXYZ', score: 75, date: '2024-01-12' },
    { id: 3, job: 'React Developer', company: 'BigTech', score: 78, date: '2024-01-10' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <p className="text-xl text-gray-600">Track your interview performance and progress</p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { 
              icon: BarChart3, 
              label: 'Total Interviews', 
              value: stats.totalInterviews, 
              color: 'from-blue-500 to-blue-600' 
            },
            { 
              icon: TrendingUp, 
              label: 'Average Score', 
              value: `${stats.averageScore}%`, 
              color: 'from-green-500 to-green-600' 
            },
            { 
              icon: Award, 
              label: 'Improvement', 
              value: `+${stats.improvementRate}%`, 
              color: 'from-purple-500 to-purple-600' 
            },
            { 
              icon: Clock, 
              label: 'Time Practiced', 
              value: `${stats.timeSpent}min`, 
              color: 'from-orange-500 to-orange-600' 
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6"
            >
              <div className="flex items-center">
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Recent Interviews */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Interviews</h2>
          
          <div className="space-y-4">
            {recentInterviews.map((interview, index) => (
              <motion.div
                key={interview.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div>
                  <h3 className="font-semibold text-gray-900">{interview.job}</h3>
                  <p className="text-sm text-gray-600">{interview.company}</p>
                  <p className="text-xs text-gray-500">{interview.date}</p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 text-sm rounded-full font-medium ${
                    interview.score >= 80 ? 'bg-green-100 text-green-800' :
                    interview.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {interview.score}%
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;