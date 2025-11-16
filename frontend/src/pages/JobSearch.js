import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  Search, 
  MapPin, 
  DollarSign, 
  Clock, 
  Building, 
  Loader2,
  ArrowRight,
  Star,
  ExternalLink,
  Filter
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { searchJobs } from '../services/api';

const JobSearch = () => {
  const navigate = useNavigate();
  const { state, setSelectedJob } = useApp();
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams, setSearchParams] = useState({
    skills: '',
    location: 'us',
    experience: '',
    salary: '',
  });
  const [filters, setFilters] = useState({
    remoteOnly: false,
    salaryRange: '',
    experienceLevel: '',
  });

  useEffect(() => {
    // Pre-populate skills from resume if available
    if (state.resume?.skills) {
      setSearchParams(prev => ({
        ...prev,
        skills: state.resume.skills.join(', ')
      }));
      // Auto-search with resume skills
      handleSearch(state.resume.skills.join(', '));
    }
  }, [state.resume]);

  const handleSearch = async (skillsOverride = null) => {
    const skills = skillsOverride || searchParams.skills;
    
    if (!skills.trim()) {
      toast.error('Please enter some skills to search for jobs');
      return;
    }

    setIsLoading(true);

    try {
      const response = await searchJobs(skills, searchParams.location, 20);
      
      let filteredJobs = response.jobs || [];
      
      // Apply filters
      if (filters.remoteOnly) {
        filteredJobs = filteredJobs.filter(job => job.remote_work);
      }
      
      if (filters.experienceLevel) {
        filteredJobs = filteredJobs.filter(job => 
          job.title.toLowerCase().includes(filters.experienceLevel.toLowerCase())
        );
      }
      
      setJobs(filteredJobs);
      
      if (filteredJobs.length === 0) {
        toast('No jobs found. Try different keywords or filters.', { icon: '🔍' });
      } else {
        toast.success(`Found ${filteredJobs.length} job opportunities!`);
      }
      
    } catch (error) {
      toast.error(error.message || 'Failed to search jobs');
      setJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobSelect = (job) => {
    setSelectedJob(job);
    toast.success(`Selected: ${job.title}`);
    navigate('/interview');
  };

  const formatSalary = (min, max, currency = 'USD') => {
    if (!min && !max) return 'Salary not specified';
    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    }
    return min ? `From $${min.toLocaleString()}` : `Up to $${max.toLocaleString()}`;
  };

  const getExperienceLevel = (title) => {
    const lower = title.toLowerCase();
    if (lower.includes('senior') || lower.includes('lead') || lower.includes('principal')) {
      return { level: 'Senior', color: 'bg-purple-100 text-purple-800' };
    }
    if (lower.includes('junior') || lower.includes('entry') || lower.includes('associate')) {
      return { level: 'Junior', color: 'bg-green-100 text-green-800' };
    }
    return { level: 'Mid-level', color: 'bg-blue-100 text-blue-800' };
  };

  const locationOptions = [
    { value: 'us', label: 'United States' },
    { value: 'uk', label: 'United Kingdom' },
    { value: 'ca', label: 'Canada' },
    { value: 'au', label: 'Australia' },
    { value: 'de', label: 'Germany' },
    { value: 'remote', label: 'Remote Only' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="text-6xl mb-6">🔍</div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Find Your Dream Job
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover opportunities that match your skills and experience
          </p>
        </motion.div>

        {/* Search Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="card p-8 mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skills & Keywords
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchParams.skills}
                  onChange={(e) => setSearchParams({ ...searchParams, skills: e.target.value })}
                  className="input-field pl-10"
                  placeholder="Python, React, Machine Learning..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <select
                  value={searchParams.location}
                  onChange={(e) => setSearchParams({ ...searchParams, location: e.target.value })}
                  className="input-field pl-10"
                >
                  {locationOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex items-end">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleSearch()}
                disabled={isLoading}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Search Jobs</span>
                  </>
                )}
              </motion.button>
            </div>
          </div>

          {/* Filters */}
          <div className="border-t pt-6">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filters:</span>
              </div>
              
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.remoteOnly}
                  onChange={(e) => setFilters({ ...filters, remoteOnly: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Remote only</span>
              </label>
              
              <select
                value={filters.experienceLevel}
                onChange={(e) => setFilters({ ...filters, experienceLevel: e.target.value })}
                className="text-sm border border-gray-300 rounded-lg px-3 py-1"
              >
                <option value="">All levels</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid-level</option>
                <option value="senior">Senior</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Resume Skills Suggestion */}
        {state.resume?.skills && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="card p-6 mb-8 bg-blue-50 border-blue-200"
          >
            <div className="flex items-start space-x-3">
              <Star className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  Skills from your resume
                </h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  {state.resume.skills.slice(0, 8).map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                  {state.resume.skills.length > 8 && (
                    <span className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
                      +{state.resume.skills.length - 8} more
                    </span>
                  )}
                </div>
                <p className="text-sm text-blue-800">
                  We've automatically searched for jobs matching your skills!
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Job Results */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="card p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6 mb-4"></div>
                  <div className="flex space-x-2">
                    <div className="h-6 bg-gray-200 rounded w-16"></div>
                    <div className="h-6 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {jobs.length} Job{jobs.length !== 1 ? 's' : ''} Found
              </h2>
              <div className="text-sm text-gray-600">
                Sorted by relevance
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map((job, index) => {
                const experienceLevel = getExperienceLevel(job.title);
                
                return (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.6 }}
                    className="card p-6 group hover:shadow-2xl transition-all duration-300"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                          {job.title}
                        </h3>
                        <div className="flex items-center space-x-2 text-gray-600 mb-2">
                          <Building className="w-4 h-4" />
                          <span className="text-sm font-medium">{job.company}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-gray-600 mb-3">
                          <MapPin className="w-4 h-4" />
                          <span className="text-sm">{job.location}</span>
                          {job.remote_work && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              Remote
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <span className={`px-2 py-1 text-xs rounded-full ${experienceLevel.color}`}>
                        {experienceLevel.level}
                      </span>
                    </div>

                    {job.salary_min || job.salary_max ? (
                      <div className="flex items-center space-x-2 text-gray-600 mb-4">
                        <DollarSign className="w-4 h-4" />
                        <span className="text-sm font-medium">
                          {formatSalary(job.salary_min, job.salary_max)}
                        </span>
                      </div>
                    ) : null}

                    <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                      {job.description}
                    </p>

                    {job.skills_required && job.skills_required.length > 0 && (
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-1">
                          {job.skills_required.slice(0, 3).map((skill, skillIndex) => (
                            <span
                              key={skillIndex}
                              className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded"
                            >
                              {skill}
                            </span>
                          ))}
                          {job.skills_required.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                              +{job.skills_required.length - 3}
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleJobSelect(job)}
                        className="btn-primary flex-1 flex items-center justify-center space-x-2"
                      >
                        <span>Start Interview</span>
                        <ArrowRight className="w-4 h-4" />
                      </motion.button>
                      
                      {job.url && (
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => window.open(job.url, '_blank')}
                          className="btn-secondary p-3"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </motion.button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        ) : !isLoading && searchParams.skills && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No jobs found
            </h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search terms or filters
            </p>
            <button
              onClick={() => setSearchParams({ ...searchParams, skills: '' })}
              className="btn-secondary"
            >
              Clear Search
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default JobSearch;