import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import DashboardLayout from '../components/DashboardLayout.jsx';
import useVoiceNavigation from '../hooks/useVoiceNavigation.js';
import {
  Mic,
  Volume2,
  HelpCircle,
  CheckCircle,
  AlertCircle,
  Zap,
  ArrowRight
} from 'lucide-react';

/**
 * Voice Navigation Demo Page
 * Demonstrates the voice navigation capabilities
 */
const VoiceNavigationDemo = () => {
  const { user } = useAuth();
  const {
    isListening,
    isSupported,
    transcript,
    confidence,
    error,
    lastCommand,
    startListening,
    stopListening,
    getAvailableCommands
  } = useVoiceNavigation({
    enableVoiceFeedback: true
  });

  const availableCommands = getAvailableCommands();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-3xl font-extrabold text-gray-800 mb-4">
            🎤 Voice Navigation Demo
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Experience hands-free navigation with our cutting-edge voice assistant. 
            Click the microphone and say any command to navigate instantly.
          </p>
        </motion.div>

        {/* Browser Support Check */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`p-4 rounded-lg border ${
            isSupported 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}
        >
          <div className="flex items-center space-x-3">
            {isSupported ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-600" />
            )}
            <div>
              <h3 className={`font-semibold ${
                isSupported ? 'text-green-800' : 'text-red-800'
              }`}>
                {isSupported ? 'Voice Navigation Supported' : 'Voice Navigation Not Supported'}
              </h3>
              <p className={`text-sm ${
                isSupported ? 'text-green-600' : 'text-red-600'
              }`}>
                {isSupported 
                  ? 'Your browser supports voice navigation. You can use voice commands!'
                  : 'Your browser does not support voice navigation. Please use Chrome or Edge.'
                }
              </p>
            </div>
          </div>
        </motion.div>

        {isSupported && (
          <>
            {/* Voice Controls */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <Mic className="w-6 h-6 text-blue-500" />
                <span>Voice Controls</span>
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Listening Status */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-700">Status:</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      isListening 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {isListening ? 'Listening...' : 'Ready'}
                    </span>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={startListening}
                      disabled={isListening}
                      className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                        isListening
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-blue-500 hover:bg-blue-600 text-white'
                      }`}
                    >
                      Start Listening
                    </button>
                    <button
                      onClick={stopListening}
                      disabled={!isListening}
                      className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                        !isListening
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-red-500 hover:bg-red-600 text-white'
                      }`}
                    >
                      Stop Listening
                    </button>
                  </div>
                </div>

                {/* Transcript Display */}
                <div className="space-y-4">
                  <div>
                    <span className="font-medium text-gray-700">Last Transcript:</span>
                    <div className="mt-2 p-3 bg-gray-50 rounded-lg min-h-[60px] flex items-center">
                      {transcript ? (
                        <span className="text-gray-800">"{transcript}"</span>
                      ) : (
                        <span className="text-gray-400 italic">No speech detected yet</span>
                      )}
                    </div>
                  </div>

                  {confidence > 0 && (
                    <div>
                      <span className="font-medium text-gray-700">Confidence:</span>
                      <div className="mt-2 flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          {Math.round(confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Error Display */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <span className="text-red-700 font-medium">Error: {error}</span>
                  </div>
                </motion.div>
              )}

              {/* Last Command */}
              {lastCommand && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-green-700 font-medium">
                      Last Command: "{lastCommand}"
                    </span>
                  </div>
                </motion.div>
              )}
            </motion.div>

            {/* Available Commands */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <HelpCircle className="w-6 h-6 text-purple-500" />
                <span>Available Commands for {user?.role || 'User'}</span>
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {availableCommands.map((command, index) => (
                  <motion.div
                    key={command}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <Zap className="w-4 h-4 text-blue-500" />
                    <span className="text-gray-700 font-medium">"{command}"</span>
                  </motion.div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">💡 Usage Tips</h3>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Click "Start Listening" and wait for the confirmation</li>
                  <li>• Speak clearly and at a normal pace</li>
                  <li>• Commands are case-insensitive and flexible</li>
                  <li>• You can also use the floating microphone button</li>
                  <li>• Voice feedback will confirm your actions</li>
                </ul>
              </div>
            </motion.div>

            {/* Quick Test Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-6 text-white"
            >
              <h2 className="text-xl font-bold mb-4 flex items-center space-x-2">
                <Volume2 className="w-6 h-6" />
                <span>Quick Test</span>
              </h2>
              
              <p className="mb-4">
                Try saying one of these commands to test the voice navigation:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white/10 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Navigation Commands:</h3>
                  <ul className="space-y-1 text-sm">
                    <li>• "Dashboard"</li>
                    <li>• "Courses"</li>
                    <li>• "Profile"</li>
                  </ul>
                </div>
                
                <div className="bg-white/10 rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Action Commands:</h3>
                  <ul className="space-y-1 text-sm">
                    <li>• "Assignments"</li>
                    <li>• "Calendar"</li>
                    <li>• "Logout"</li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-4 flex items-center space-x-2 text-blue-100">
                <ArrowRight className="w-4 h-4" />
                <span className="text-sm">
                  The floating microphone button is always available on all pages!
                </span>
              </div>
            </motion.div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
};

export default VoiceNavigationDemo;
