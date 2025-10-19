import { createClient } from '@supabase/supabase-js';

// Using the cloud Supabase instance for authentication
const supabaseUrl = 'https://aaxiaqzrlzqypmxrlqsy.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFheGlhcXpybHpxeXBteHJscXN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg1NjIxMTQsImV4cCI6MjA0NDEzODExNH0.vfxw6W_Bd0wLNsQKDYcg_xdM1TL8-0BbyF8ikJWxnSE';

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
