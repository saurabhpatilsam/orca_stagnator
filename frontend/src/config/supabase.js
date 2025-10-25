import { createClient } from '@supabase/supabase-js';

// Using environment variables for Supabase configuration
// Production Supabase instance: dcoukhtfcloqpfmijock
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://dcoukhtfcloqpfmijock.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3MDE4MDMsImV4cCI6MjA2OTI3NzgwM30.2gF_vRzqJ5v8_9YJMxN8kZQd1aYN0_X7yVQJQ3YzXm0';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    storageKey: 'orca-auth',
    storage: window.localStorage,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
});

// Helper functions for authentication
export const signUp = async (email, password) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: window.location.origin,
    }
  });
  return { data, error };
};

export const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const getSession = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
};

export const setupMFA = async () => {
  const { data, error } = await supabase.auth.mfa.enroll({
    factorType: 'totp'
  });
  return { data, error };
};

export const verifyMFA = async (code, factorId) => {
  const { data, error } = await supabase.auth.mfa.verify({
    factorType: 'totp',
    code,
    factorId
  });
  return { data, error };
};
