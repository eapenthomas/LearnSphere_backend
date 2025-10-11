import React, { createContext, useContext, useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const AuthContext = createContext();

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Warn if environment variables are not set
if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('⚠️ Supabase environment variables not found. Please create a .env file with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY');
}

const supabase = createClient(
    supabaseUrl || 'https://placeholder.supabase.co',
    supabaseAnonKey || 'placeholder_key'
);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [initialized, setInitialized] = useState(false);
    const [session, setSession] = useState(null);
    const [authToken, setAuthToken] = useState(localStorage.getItem('auth_token'));

    // Function to fetch user profile from Supabase
    const fetchUserProfile = async (userId) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            if (error) {
                console.error('Error fetching user profile:', error);
                return null;
            }

            return data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return null;
        }
    };

    // Function to validate stored session and refresh tokens
    const validateStoredSession = async () => {
        try {
            const storedUser = localStorage.getItem('learnsphere_user');
            const storedAccessToken = localStorage.getItem('learnsphere_access_token');
            const storedRefreshToken = localStorage.getItem('learnsphere_refresh_token');

            if (!storedUser || !storedAccessToken) {
                return null;
            }

            const userData = JSON.parse(storedUser);

            // Basic validation
            if (!userData.id || !userData.email) {
                console.log('Invalid stored user data, clearing session');
                clearAuthData();
                return null;
            }

            // First, validate the stored access token by checking its expiration
            try {
                // Decode JWT token to check expiration (without verification for client-side check)
                const tokenParts = storedAccessToken.split('.');
                if (tokenParts.length === 3) {
                    const payload = JSON.parse(atob(tokenParts[1]));
                    const currentTime = Math.floor(Date.now() / 1000);
                    
                    if (payload.exp && payload.exp > currentTime) {
                        console.log('Stored access token is still valid');
                        return { userData, token: storedAccessToken };
                    } else {
                        console.log('Stored access token has expired');
                    }
                }
            } catch (error) {
                console.log('Access token validation failed:', error);
            }

            // If access token is invalid, try to refresh if we have a refresh token
            if (storedRefreshToken) {
                try {
                    const refreshResponse = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        credentials: 'include',
                        body: JSON.stringify({ refresh_token: storedRefreshToken })
                    });

                    if (refreshResponse.ok) {
                        const refreshData = await refreshResponse.json();
                        console.log('Token refreshed successfully');
                        
                        // Update stored tokens
                        localStorage.setItem('learnsphere_access_token', refreshData.access_token);
                        
                        // Update stored user data with new token
                        const updatedUserData = { ...userData, accessToken: refreshData.access_token };
                        localStorage.setItem('learnsphere_user', JSON.stringify(updatedUserData));
                        
                        return { userData: updatedUserData, token: refreshData.access_token };
                    } else {
                        console.log('Token refresh failed, clearing session');
                        clearAuthData();
                        return null;
                    }
                } catch (error) {
                    console.error('Error refreshing token:', error);
                    clearAuthData();
                    return null;
                }
            }

            // If no refresh token or refresh failed, clear session
            console.log('No valid session found, clearing auth data');
            clearAuthData();
            return null;

        } catch (error) {
            console.error('Error validating stored session:', error);
            clearAuthData();
            return null;
        }
    };

    // Helper function to handle Supabase session
    const handleSupabaseSession = async (supabaseSession) => {
        setSession(supabaseSession);

        // Fetch user profile from database
        const profile = await fetchUserProfile(supabaseSession.user.id);
        if (profile) {
            const finalRole = profile.email === 'eapentkadamapuzha@gmail.com' ? 'admin' : (profile.role || 'student');

            const userData = {
                id: profile.id,
                email: profile.email,
                accessToken: supabaseSession.access_token,
                fullName: profile.full_name || 'User',
                role: finalRole,
                approvalStatus: profile.approval_status || 'approved',
                isActive: profile.is_active !== undefined ? profile.is_active : true,
                profile_picture: profile.profile_picture || null
            };

            setUser(userData);
            setAuthToken(supabaseSession.access_token);

            // Store in localStorage with timestamp for persistence
            localStorage.setItem('learnsphere_user', JSON.stringify(userData));
            localStorage.setItem('learnsphere_token', supabaseSession.access_token);
            localStorage.setItem('learnsphere_session_timestamp', Date.now().toString());

            console.log('AuthContext - Session established for:', profile.full_name, 'Role:', finalRole);
            setLoading(false);
            setInitialized(true);
        }
    };

    // Helper function to clear auth data
    const clearAuthData = () => {
        localStorage.removeItem('learnsphere_user');
        localStorage.removeItem('learnsphere_access_token');
        localStorage.removeItem('learnsphere_refresh_token');
        localStorage.removeItem('learnsphere_session_timestamp');
        localStorage.removeItem('auth_token'); // Legacy key
        setUser(null);
        setSession(null);
        setAuthToken(null);
    };

    useEffect(() => {
        // Enhanced authentication initialization with better session persistence
        const initializeAuth = async () => {
            console.log('AuthContext - Initializing enhanced authentication...');
            setLoading(true);

            try {
                // Step 1: Check for existing Supabase session
                const { data: { session: supabaseSession }, error } = await supabase.auth.getSession();

                if (supabaseSession && !error) {
                    console.log('AuthContext - Active Supabase session found');
                    await handleSupabaseSession(supabaseSession);
                    return;
                }

                // Step 2: Check localStorage for persistent session and validate tokens
                const sessionValidation = await validateStoredSession();
                
                if (sessionValidation) {
                    console.log('AuthContext - Valid session restored from localStorage');
                    const { userData, token } = sessionValidation;
                    
                    // Validate and set user data
                    if (userData.id && userData.email) {
                        const finalRole = userData.email === 'eapentkadamapuzha@gmail.com' ? 'admin' : (userData.role || 'student');
                        const restoredUser = { ...userData, role: finalRole, accessToken: token };
                        setUser(restoredUser);
                        setAuthToken(token);
                        
                        // Update localStorage with the restored user data
                        localStorage.setItem('learnsphere_user', JSON.stringify(restoredUser));
                        
                        console.log('AuthContext - Session restored for:', userData.fullName, 'Role:', finalRole);
                    }
                } else {
                    console.log('AuthContext - No valid stored session found, user will need to login');
                }
            } catch (error) {
                console.error('AuthContext - Error during initialization:', error);
                // Clear corrupted data
                clearAuthData();
            } finally {
                console.log('AuthContext - Initialization complete');
                setInitialized(true);
                setLoading(false);
            }
        };

        // Run initialization immediately
        initializeAuth();

        // Listen for Supabase auth state changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, supabaseSession) => {
                console.log('AuthContext - Auth state change:', event, 'Session exists:', !!supabaseSession);

                if (event === 'SIGNED_IN' && supabaseSession) {
                    console.log('AuthContext - Processing new sign in');
                    await handleSupabaseSession(supabaseSession);
                } else if (event === 'SIGNED_OUT') {
                    console.log('AuthContext - User signed out');
                    clearAuthData();
                } else if (event === 'TOKEN_REFRESHED' && supabaseSession) {
                    console.log('AuthContext - Token refreshed');
                    setSession(supabaseSession);

                    // Update stored token
                    localStorage.setItem('learnsphere_token', supabaseSession.access_token);

                    // Update user access token
                    if (user) {
                        setUser(prev => ({
                            ...prev,
                            accessToken: supabaseSession.access_token
                        }));
                    }
                }
            }
        );

        return () => subscription.unsubscribe();
    }, []);

    // Set up real-time subscription for profile updates
    useEffect(() => {
        if (!user?.id) return;

        console.log('AuthContext - Setting up profile subscription for user:', user.id);

        const profileSubscription = supabase
            .channel(`profile-${user.id}`)
            .on('postgres_changes',
                {
                    event: 'UPDATE',
                    schema: 'public',
                    table: 'profiles',
                    filter: `id=eq.${user.id}`
                },
                (payload) => {
                    console.log('AuthContext - Profile updated, refreshing user data:', payload);
                    // Refresh user data when profile is updated
                    refreshUserData();
                }
            )
            .subscribe();

        return () => {
            console.log('AuthContext - Cleaning up profile subscription');
            profileSubscription.unsubscribe();
        };
    }, [user?.id]);

    const register = async (userData) => {
        console.log('AuthContext - Starting registration for:', userData.email);
        try {
            const response = await axios.post(`${API_BASE_URL}/api/auth/register`, userData);
            const { access_token, user_id, role, full_name } = response.data;
            console.log('AuthContext - Registration successful, setting user data');

            // Force admin role for specific email
            const finalRole = userData.email === 'eapentkadamapuzha@gmail.com' ? 'admin' : role;

            const userObj = {
                id: user_id,
                email: userData.email,
                accessToken: access_token,
                role: finalRole,
                fullName: full_name,
                approvalStatus: response.data.approval_status,
                isActive: response.data.is_active
            };

            setUser(userObj);

            // Store session in localStorage for persistence
            localStorage.setItem('learnsphere_user', JSON.stringify({
                id: user_id,
                email: userData.email,
                accessToken: access_token,
                fullName: full_name,
                role: finalRole,
                approvalStatus: response.data.approval_status,
                isActive: response.data.is_active
            }));
            localStorage.setItem('learnsphere_token', access_token);

            // Ensure loading is set to false after successful registration
            console.log('AuthContext - Setting loading to false after registration');
            setLoading(false);

            return { success: true, data: response.data };
        } catch (error) {
            console.error('AuthContext - Registration error:', error);
            // Also set loading to false on error
            setLoading(false);
            return {
                success: false,
                error: error.response?.data?.detail || 'Registration failed'
            };
        }
    };

    const login = async (credentials) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/api/auth/login`, credentials);
            const { access_token, refresh_token, user_id, role, full_name } = response.data;

            // Force admin role for specific email
            const finalRole = credentials.email === 'eapentkadamapuzha@gmail.com' ? 'admin' : role;

            const userObj = {
                id: user_id,
                email: credentials.email,
                accessToken: access_token,
                role: finalRole,
                fullName: full_name,
                approvalStatus: response.data.approval_status,
                isActive: response.data.is_active
            };

            setUser(userObj);
            setAuthToken(access_token);

            // Store session in localStorage for persistence
            localStorage.setItem('learnsphere_user', JSON.stringify({
                id: user_id,
                email: credentials.email,
                accessToken: access_token,
                fullName: full_name,
                role: finalRole,
                approvalStatus: response.data.approval_status,
                isActive: response.data.is_active
            }));
            
            // Store both tokens
            localStorage.setItem('learnsphere_access_token', access_token);
            if (refresh_token) {
                localStorage.setItem('learnsphere_refresh_token', refresh_token);
            }
            localStorage.setItem('learnsphere_session_timestamp', Date.now().toString());

            // Ensure loading is set to false after successful login
            setLoading(false);

            return { success: true, data: response.data };
        } catch (error) {
            // Also set loading to false on error
            setLoading(false);
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed'
            };
        }
    };

    const loginWithGoogle = async () => {
        try {
            // Check if Supabase is properly configured
            if (!supabaseUrl || supabaseUrl === 'https://placeholder.supabase.co') {
                return {
                    success: false,
                    error: 'Supabase not configured. Please set up your VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in the .env file.'
                };
            }

            const { data: { url } } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback`
                }
            });

            window.location.href = url;
        } catch (error) {
            console.error('Google login error:', error);
            return { success: false, error: 'Google login failed' };
        }
    };

    const logout = async () => {
        console.log('AuthContext - Starting logout process...');
        try {
            // Clear user state immediately for better UX
            setUser(null);
            setLoading(false);

            // Try to sign out from Supabase (in case there's a session)
            try {
                await supabase.auth.signOut();
                console.log('AuthContext - Supabase signout successful');
            } catch (supabaseError) {
                console.log('AuthContext - No Supabase session to sign out from:', supabaseError.message);
                // This is expected for backend API users, so we don't treat it as an error
            }

            // Clear any stored tokens or session data
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
            localStorage.removeItem('learnsphere_user');
            localStorage.removeItem('learnsphere_token');
            localStorage.removeItem('learnsphere_access_token');
            localStorage.removeItem('learnsphere_refresh_token');
            localStorage.removeItem('learnsphere_session_timestamp');
            sessionStorage.clear();

            console.log('AuthContext - Logout completed successfully');
            return { success: true };
        } catch (error) {
            console.error('AuthContext - Logout error:', error);
            // Even if there's an error, we still want to clear the user state
            setUser(null);
            setLoading(false);
            return { success: false, error: 'Logout completed with warnings' };
        }
    };

    const refreshUserData = async () => {
        if (!user?.id) return;

        try {
            console.log('AuthContext - Refreshing user data for:', user.id);

            // Fetch fresh user profile from database
            const { data: profile, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', user.id)
                .single();

            if (error) {
                console.error('AuthContext - Error refreshing user data:', error);
                return;
            }

            console.log('AuthContext - Fresh profile data:', profile);

            // Update user object with fresh data
            const updatedUser = {
                ...user,
                role: profile.role,
                fullName: profile.full_name,
                approvalStatus: profile.approval_status,
                isActive: profile.is_active
            };

            setUser(updatedUser);

            // Update localStorage with fresh data
            localStorage.setItem('learnsphere_user', JSON.stringify({
                id: updatedUser.id,
                email: updatedUser.email,
                fullName: updatedUser.fullName,
                role: updatedUser.role,
                approvalStatus: updatedUser.approvalStatus,
                isActive: updatedUser.isActive
            }));

            console.log('AuthContext - User data refreshed successfully');
            return updatedUser;
        } catch (error) {
            console.error('AuthContext - Exception refreshing user data:', error);
        }
    };

    const value = {
        user,
        loading,
        register,
        login,
        loginWithGoogle,
        logout,
        refreshUserData
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}; 