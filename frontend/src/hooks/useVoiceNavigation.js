import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';

/**
 * Voice-Assisted Navigation Hook
 * Provides speech recognition for navigation commands and optional voice feedback
 */
const useVoiceNavigation = (options = {}) => {
  const {
    enableVoiceFeedback = true,
    language = 'en-US',
    continuous = false,
    interimResults = true,
    maxAlternatives = 1
  } = options;

  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  // State management
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState(null);
  const [lastCommand, setLastCommand] = useState('');

  // Refs for speech APIs
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  // Voice command mappings based on user role
  const getCommandMappings = useCallback(() => {
    const baseCommands = {
      // Navigation commands
      'dashboard': '/dashboard',
      'home': '/dashboard',
      'profile': '/profile',
      'settings': '/profile',

      // Authentication
      'logout': () => logout(),
      'sign out': () => logout(),
      'log out': () => logout(),

      // Wake word activation - simplified to just "hey"
      'hey': () => {
        speak("Yes, I'm listening. What would you like to do?");
        return null; // Don't navigate, just acknowledge
      },
      'hey lumo': () => {
        speak("Yes, I'm listening. What would you like to do?");
        return null; // Don't navigate, just acknowledge
      },
      'lumo': () => {
        speak("How can I help you navigate?");
        return null;
      },
    };

    if (user?.role === 'student') {
      return {
        ...baseCommands,
        'courses': '/mycourses',
        'my courses': '/mycourses',
        'all courses': '/allcourses',
        'assignments': '/assignments',
        'quizzes': '/student/quizzes',
        'kisses': '/student/quizzes',
        'quiz': '/student/quizzes',
        'notes summarizer': '/student/notes-summarizer',
        'progress': '/student/progress',
        'calendar': '/calendar',
        'forum': '/forum',
        'doubt forum': '/forum',

        'profile': '/profile',
        'settings': '/profile',
      };
    } else if (user?.role === 'teacher') {
      return {
        ...baseCommands,
        'courses': '/teacher/mycourses',
        'my courses': '/teacher/mycourses',
        'assignments': '/teacher/assignments',
        'quizzes': '/teacher/quizzes',
        'quiz': '/teacher/quizzes',
        'students': '/teacher/progress',
        'calendar': '/teacher/calendar',
        'forum': '/teacher/forum',
        'analytics': '/teacher/reports',
        'reports': '/teacher/reports',
      };
    } else if (user?.role === 'admin') {
      return {
        ...baseCommands,
        'users': '/admin/user-management',
        'user management': '/admin/user-management',
        'teachers': '/admin/teacher-approvals',
        'teacher approvals': '/admin/teacher-approvals',
        'activity logs': '/admin/activity-logs',
        'logs': '/admin/activity-logs',
        'email notifications': '/admin/email-notifications',
        'notifications': '/admin/email-notifications',
        'quiz results': '/admin/quiz-results',
        'ai usage': '/admin/ai-usage',
        'settings': '/admin/system-settings',
        'system settings': '/admin/system-settings',
      };
    }

    return baseCommands;
  }, [user, logout]);

  // Voice feedback function
  const speak = useCallback((text) => {
    if (!enableVoiceFeedback || !synthRef.current) return;

    // Cancel any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;

    synthRef.current.speak(utterance);
  }, [enableVoiceFeedback, language]);

  // Process voice command
  const processCommand = useCallback((command) => {
    const normalizedCommand = command.toLowerCase().trim();
    const commandMappings = getCommandMappings();

    setLastCommand(normalizedCommand);

    // Check for wake words first - simplified to just "hey"
    if (normalizedCommand.includes('hey')) {
      const action = commandMappings['hey'] || commandMappings['hey lumo'] || commandMappings['lumo'];
      if (action) {
        action();
        window.lastVoiceCommandTime = Date.now(); // Track command execution
      }
      return true;
    }

    // Find matching command
    const matchedCommand = Object.keys(commandMappings).find(cmd =>
      normalizedCommand.includes(cmd)
    );

    if (matchedCommand) {
      const action = commandMappings[matchedCommand];
      window.lastVoiceCommandTime = Date.now(); // Track command execution

      if (typeof action === 'function') {
        // Execute function (like logout) - no voice feedback to avoid interference
        action();
      } else if (action) {
        // Navigate to route - no voice feedback to avoid interference
        navigate(action);
      }

      return true;
    } else {
      // Command not recognized - only speak if it's not a wake word attempt
      if (!normalizedCommand.includes('hey')) {
        speak("Sorry, I didn't understand that command. Try saying 'hey' first, then your command.");
        setError('Command not recognized');
      }
      return false;
    }
  }, [getCommandMappings, navigate, speak]);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const SpeechSynthesis = window.speechSynthesis;

      if (SpeechRecognition && SpeechSynthesis) {
        setIsSupported(true);
        
        // Initialize recognition
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.lang = language;
        recognitionRef.current.continuous = continuous;
        recognitionRef.current.interimResults = interimResults;
        recognitionRef.current.maxAlternatives = maxAlternatives;

        // Initialize synthesis
        synthRef.current = SpeechSynthesis;

        // Event handlers
        recognitionRef.current.onstart = () => {
          setIsListening(true);
          setError(null);
          setTranscript('');
        };

        recognitionRef.current.onresult = (event) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
              finalTranscript += result[0].transcript;
              setConfidence(result[0].confidence);
            } else {
              interimTranscript += result[0].transcript;
            }
          }

          setTranscript(finalTranscript || interimTranscript);

          // Process final transcript
          if (finalTranscript) {
            const processed = processCommand(finalTranscript);
            // If it was a wake word, clear transcript and continue listening
            if (processed && finalTranscript.toLowerCase().includes('hey')) {
              setTimeout(() => {
                setTranscript('');
              }, 1000);
            }
          }
        };

        recognitionRef.current.onerror = (event) => {
          setError(event.error);
          setIsListening(false);

          if (event.error === 'not-allowed') {
            speak("Microphone access denied. Please allow microphone access to use voice navigation.");
          } else if (event.error === 'no-speech') {
            // No auto-restart on no speech - manual control only
            console.log('No speech detected - click microphone to try again');
          }
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
          // No auto-restart - manual control only to prevent cycling
          console.log('Voice recognition ended - click microphone to restart');
        };
        // Manual start only - removed auto-start to prevent cycling issues
        // Users can click the voice button to start listening
      } else {
        setIsSupported(false);
        setError('Speech recognition not supported in this browser');
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, [language, continuous, interimResults, maxAlternatives, processCommand]);

  // Start listening
  const startListening = useCallback(() => {
    if (!isSupported || !recognitionRef.current) {
      setError('Speech recognition not available');
      return;
    }

    if (isListening) {
      return; // Already listening
    }

    try {
      // Check if recognition is already started
      if (recognitionRef.current.state === 'started') {
        console.log('Recognition already started');
        return;
      }

      recognitionRef.current.start();
      // Removed voice feedback to prevent interference
    } catch (err) {
      if (err.name === 'InvalidStateError') {
        console.log('Recognition already started (InvalidStateError)');
        return;
      }
      setError('Failed to start speech recognition');
      console.error('Speech recognition error:', err);
    }
  }, [isSupported, isListening, speak]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Get available commands for current user
  const getAvailableCommands = useCallback(() => {
    return Object.keys(getCommandMappings());
  }, [getCommandMappings]);

  return {
    // State
    isListening,
    isSupported,
    transcript,
    confidence,
    error,
    lastCommand,
    
    // Actions
    startListening,
    stopListening,
    toggleListening,
    speak,
    processCommand,
    
    // Utilities
    getAvailableCommands,
  };
};

export default useVoiceNavigation;
