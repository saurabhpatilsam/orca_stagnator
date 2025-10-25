import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../config/api';
import toast from 'react-hot-toast';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = () => {
      try {
        const currentUser = authAPI.getCurrentUser();
        const token = authAPI.getToken();
        
        if (currentUser && token) {
          setUser(currentUser);
          setSession({ user: currentUser, access_token: token });
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authAPI.signOut();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const signIn = async (email, password) => {
    try {
      const response = await authAPI.signIn(email, password);
      
      setUser(response.user);
      setSession({ user: response.user, access_token: response.access_token });
      
      toast.success('Successfully signed in!');
      return { data: response, error: null };
    } catch (error) {
      toast.error(error.message || 'Sign in failed');
      return { data: null, error };
    }
  };

  const signUp = async (email, password) => {
    try {
      const response = await authAPI.signUp(email, password);
      
      setUser(response.user);
      setSession({ user: response.user, access_token: response.access_token });
      
      toast.success('Account created successfully!');
      return { data: response, error: null };
    } catch (error) {
      toast.error(error.message || 'Sign up failed');
      return { data: null, error };
    }
  };

  const signOut = async () => {
    try {
      authAPI.signOut();
      setUser(null);
      setSession(null);
      
      toast.success('Successfully signed out!');
      window.location.href = '/';
    } catch (error) {
      toast.error(error.message || 'Sign out failed');
    }
  };

  const value = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
