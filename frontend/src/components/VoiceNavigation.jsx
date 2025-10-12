import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  HelpCircle,
  X,
  Bot,
  CheckCircle,
  AlertCircle,
  Headphones,
  Radio,
  Zap
} from 'lucide-react';
import useVoiceNavigation from '../hooks/useVoiceNavigation.js';

/**
 * Voice Navigation Component
 * Provides a floating voice assistant interface for navigation
 */
const VoiceNavigation = ({ className = '' }) => {
  const [showHelp, setShowHelp] = useState(false);
  const [enableVoiceFeedback, setEnableVoiceFeedback] = useState(true);

  const {
    isListening,
    isSupported,
    transcript,
    confidence,
    error,
    lastCommand,
    startListening,
    stopListening,
    toggleListening,
    getAvailableCommands
  } = useVoiceNavigation({
    enableVoiceFeedback,
    continuous: false,
    interimResults: true
  });

  if (!isSupported) {
    return null; // Don't render if not supported
  }

  const availableCommands = getAvailableCommands();

  return (
    <>
      {/* Floating Voice Button */}
      <motion.div
        className={`fixed bottom-6 right-6 z-50 ${className}`}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <div className="relative">
          {/* Main Voice Button */}
          <motion.button
            onClick={toggleListening}
            className={`
              w-16 h-16 rounded-full shadow-xl flex items-center justify-center
              transition-all duration-300 transform hover:scale-110
              ${isListening
                ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 animate-pulse'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
              }
              border-2 border-white
            `}
            whileTap={{ scale: 0.95 }}
            title={isListening ? 'Stop listening' : 'Say "Hey Lumo" to start'}
          >
            {isListening ? (
              <Radio className="w-8 h-8 text-white" />
            ) : (
              <Headphones className="w-8 h-8 text-white" />
            )}
          </motion.button>

          {/* Listening Animation */}
          {isListening && (
            <motion.div
              className="absolute inset-0 rounded-full border-4 border-red-300"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 0.3, 0.7]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          )}

          {/* Status Indicator */}
          {error && (
            <motion.div
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <AlertCircle className="w-4 h-4 text-white" />
            </motion.div>
          )}

          {lastCommand && !error && (
            <motion.div
              className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <CheckCircle className="w-4 h-4 text-white" />
            </motion.div>
          )}
        </div>

        {/* Secondary Controls */}
        <div className="absolute bottom-20 right-0 flex flex-col space-y-2">
          {/* Voice Feedback Toggle */}
          <motion.button
            onClick={() => setEnableVoiceFeedback(!enableVoiceFeedback)}
            className={`
              w-12 h-12 rounded-full shadow-md flex items-center justify-center
              transition-all duration-200 hover:scale-105
              ${enableVoiceFeedback 
                ? 'bg-green-500 hover:bg-green-600' 
                : 'bg-gray-400 hover:bg-gray-500'
              }
            `}
            title={enableVoiceFeedback ? 'Disable voice feedback' : 'Enable voice feedback'}
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {enableVoiceFeedback ? (
              <Volume2 className="w-5 h-5 text-white" />
            ) : (
              <VolumeX className="w-5 h-5 text-white" />
            )}
          </motion.button>

          {/* Help Button */}
          <motion.button
            onClick={() => setShowHelp(true)}
            className="w-12 h-12 rounded-full bg-purple-500 hover:bg-purple-600 shadow-md flex items-center justify-center transition-all duration-200 hover:scale-105"
            title="Voice commands help"
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <HelpCircle className="w-5 h-5 text-white" />
          </motion.button>
        </div>
      </motion.div>

      {/* Transcript Display */}
      <AnimatePresence>
        {(isListening || transcript) && (
          <motion.div
            className="fixed bottom-24 right-6 z-40 max-w-sm"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
          >
            <div className="bg-white rounded-lg shadow-lg border p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Zap className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">
                  {isListening ? 'Listening...' : 'Voice Command'}
                </span>
              </div>
              
              {transcript && (
                <div className="text-sm text-gray-600 mb-2">
                  "{transcript}"
                </div>
              )}
              
              {confidence > 0 && (
                <div className="text-xs text-gray-500">
                  Confidence: {Math.round(confidence * 100)}%
                </div>
              )}
              
              {error && (
                <div className="text-xs text-red-500 mt-1">
                  {error}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Help Modal */}
      <AnimatePresence>
        {showHelp && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[80vh] overflow-hidden"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 text-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Bot className="w-6 h-6" />
                    <h2 className="text-xl font-bold">Lumo Voice Assistant</h2>
                  </div>
                  <button
                    onClick={() => setShowHelp(false)}
                    className="p-1 hover:bg-white/20 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <p className="text-blue-100 mt-2 text-sm">
                  Say "Hey Lumo" followed by any command to navigate quickly
                </p>
              </div>

              {/* Commands List */}
              <div className="p-6 max-h-96 overflow-y-auto">
                <div className="space-y-3">
                  {availableCommands.map((command, index) => (
                    <motion.div
                      key={command}
                      className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-gray-700 font-medium">"Hey Lumo, {command}"</span>
                    </motion.div>
                  ))}
                </div>

                {/* Usage Tips */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">💡 Tips</h3>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Start with "Hey Lumo" to activate</li>
                    <li>• Speak clearly and at normal pace</li>
                    <li>• Optimized for Indian accents</li>
                    <li>• Use the microphone button to start/stop</li>
                    <li>• No voice feedback to avoid interference</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

export default VoiceNavigation;
