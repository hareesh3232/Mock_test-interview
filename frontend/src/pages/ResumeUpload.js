import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  User, 
  Mail,
  Loader2,
  ArrowRight
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { uploadResume } from '../services/api';

const ResumeUpload = () => {
  const navigate = useNavigate();
  const { setResume } = useApp();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: ''
  });

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const validTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      
      if (!validTypes.includes(file.type)) {
        toast.error('Please upload a PDF or DOCX file');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB
        toast.error('File size must be less than 10MB');
        return;
      }
      
      setUploadedFile(file);
      toast.success('File selected successfully!');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!uploadedFile) {
      toast.error('Please select a file first');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      if (userInfo.name) formData.append('user_name', userInfo.name);
      if (userInfo.email) formData.append('user_email', userInfo.email);

      const response = await uploadResume(formData);
      
      setResume(response);
      toast.success('Resume uploaded and analyzed successfully!');
      
      setTimeout(() => {
        // If job is already selected, go to interview page
        if (state.selectedJob) {
          navigate('/interview');
        } else {
          navigate('/jobs');
        }
      }, 1500);
      
    } catch (error) {
      toast.error(error.message || 'Failed to upload resume');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="text-6xl mb-6">📄</div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Upload Your Resume
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your PDF or DOCX resume to get started with AI-powered analysis
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="space-y-6"
          >
            {/* File Upload */}
            <div className="card p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Resume File</h3>
              
              <div
                {...getRootProps()}
                className={`
                  relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
                  ${isDragActive 
                    ? 'border-primary-500 bg-primary-50' 
                    : uploadedFile
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 hover:border-primary-400 hover:bg-primary-25'
                  }
                `}
              >
                <input {...getInputProps()} />
                
                {uploadedFile ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="space-y-4"
                  >
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                    <div>
                      <p className="text-lg font-semibold text-gray-900">
                        {uploadedFile.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setUploadedFile(null);
                      }}
                      className="text-sm text-primary-600 hover:text-primary-700"
                    >
                      Choose different file
                    </button>
                  </motion.div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                    <div>
                      <p className="text-lg font-semibold text-gray-900 mb-2">
                        {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        or click to browse files
                      </p>
                      <p className="text-xs text-gray-400">
                        Supports PDF, DOC, DOCX (max 10MB)
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* User Information */}
            <div className="card p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Personal Information (Optional)</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4 inline mr-2" />
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={userInfo.name}
                    onChange={(e) => setUserInfo({ ...userInfo, name: e.target.value })}
                    className="input-field"
                    placeholder="Enter your full name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Mail className="w-4 h-4 inline mr-2" />
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={userInfo.email}
                    onChange={(e) => setUserInfo({ ...userInfo, email: e.target.value })}
                    className="input-field"
                    placeholder="Enter your email address"
                  />
                </div>
              </div>
            </div>

            {/* Upload Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleUpload}
              disabled={!uploadedFile || isUploading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing Resume...</span>
                </>
              ) : (
                <>
                  <span>Upload & Analyze Resume</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </motion.div>

          {/* Info Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="space-y-6"
          >
            {/* What Happens Next */}
            <div className="card p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">What Happens Next?</h3>
              
              <div className="space-y-4">
                {[
                  {
                    step: 1,
                    title: "AI Analysis",
                    description: "Our AI extracts skills, experience, and key information from your resume"
                  },
                  {
                    step: 2,
                    title: "Job Matching",
                    description: "We find relevant job opportunities that match your profile"
                  },
                  {
                    step: 3,
                    title: "Question Generation",
                    description: "Personalized interview questions are created based on your background"
                  }
                ].map((item) => (
                  <div key={item.step} className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {item.step}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{item.title}</h4>
                      <p className="text-sm text-gray-600">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="card p-8 bg-blue-50 border-blue-200">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">Privacy & Security</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Your resume is processed securely and encrypted</li>
                    <li>• We don't share your data with third parties</li>
                    <li>• You can delete your data anytime</li>
                    <li>• All processing happens on secure servers</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Supported Formats */}
            <div className="card p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Supported Formats</h3>
              
              <div className="grid grid-cols-3 gap-4">
                {[
                  { icon: FileText, label: 'PDF', color: 'text-red-500' },
                  { icon: FileText, label: 'DOC', color: 'text-blue-500' },
                  { icon: FileText, label: 'DOCX', color: 'text-green-500' }
                ].map((format) => (
                  <div key={format.label} className="text-center p-4 border border-gray-200 rounded-lg">
                    <format.icon className={`w-8 h-8 ${format.color} mx-auto mb-2`} />
                    <p className="text-sm font-medium text-gray-900">{format.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default ResumeUpload;