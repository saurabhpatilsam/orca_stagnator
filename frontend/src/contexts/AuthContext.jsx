import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../config/supabase';
import toast from 'react-hot-toast';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session) {
          setUser(session.user);
          setSession(session);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) throw error;
      
      setUser(data.user);
      setSession(data.session);
      
      toast.success('Successfully signed in!');
      return { data, error: null };
    } catch (error) {
      toast.error(error.message || 'Sign in failed');
      return { data: null, error };
    }
  };

  const signUp = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: window.location.origin + '/dashboard',
        }
      });
      
      if (error) throw error;
      
      // Check if email confirmation is required
      if (data.user && !data.session) {
        toast.success('Please check your email to confirm your account!');
        return { data, error: null };
      }
      
      setUser(data.user);
      setSession(data.session);
      
      toast.success('Account created successfully!');
      return { data, error: null };
    } catch (error) {
      toast.error(error.message || 'Sign up failed');
      return { data: null, error };
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
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
