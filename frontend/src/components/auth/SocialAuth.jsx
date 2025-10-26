import React, { useState } from 'react';
import { supabase } from '../../config/supabase';
import toast from 'react-hot-toast';
import { FcGoogle } from 'react-icons/fc';
import { FaApple, FaGithub, FaMicrosoft } from 'react-icons/fa';

const SocialAuth = () => {
  const [loading, setLoading] = useState({
    google: false,
    apple: false,
    github: false,
    azure: false
  });

  const handleSocialLogin = async (provider) => {
    setLoading({ ...loading, [provider]: true });
    
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: provider,
        options: {
          redirectTo: `${window.location.origin}/dashboard`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      });

      if (error) {
        toast.error(`${provider} sign in failed: ${error.message}`);
        console.error('Social auth error:', error);
      }
      // If successful, Supabase will redirect automatically
    } catch (error) {
      toast.error(`An error occurred during ${provider} sign in`);
      console.error('Social auth error:', error);
    } finally {
      setLoading({ ...loading, [provider]: false });
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">Or continue with</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Google Sign In */}
        <button
          onClick={() => handleSocialLogin('google')}
          disabled={loading.google}
          className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading.google ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
          ) : (
            <>
              <FcGoogle className="h-5 w-5" />
              <span className="ml-2">Google</span>
            </>
          )}
        </button>

        {/* Apple Sign In */}
        <button
          onClick={() => handleSocialLogin('apple')}
          disabled={loading.apple}
          className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading.apple ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
          ) : (
            <>
              <FaApple className="h-5 w-5 text-black" />
              <span className="ml-2">Apple</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* GitHub Sign In */}
        <button
          onClick={() => handleSocialLogin('github')}
          disabled={loading.github}
          className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading.github ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
          ) : (
            <>
              <FaGithub className="h-5 w-5 text-black" />
              <span className="ml-2">GitHub</span>
            </>
          )}
        </button>

        {/* Microsoft/Azure Sign In */}
        <button
          onClick={() => handleSocialLogin('azure')}
          disabled={loading.azure}
          className="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading.azure ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
          ) : (
            <>
              <FaMicrosoft className="h-5 w-5 text-blue-600" />
              <span className="ml-2">Microsoft</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default SocialAuth;
