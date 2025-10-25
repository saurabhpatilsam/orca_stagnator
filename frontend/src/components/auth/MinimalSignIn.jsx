import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, LogIn } from 'lucide-react';

const MinimalSignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { data, error } = await signIn(email, password);
      
      if (!error && data) {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Sign in error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">ORCA TRADING</h1>
          <p className="text-gray-500 text-sm">Professional Trading Platform</p>
        </div>

        {/* Sign In Form */}
        <div className="bg-gray-950 border border-gray-900 rounded-lg p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Sign In</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label className="block text-gray-400 text-sm mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 bg-black border border-gray-800 text-white rounded-md focus:border-white focus:outline-none"
                  placeholder="trader@example.com"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-gray-400 text-sm mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-black border border-gray-800 text-white rounded-md focus:border-white focus:outline-none"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-500 hover:text-white"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center text-gray-400 text-sm">
                <input type="checkbox" className="mr-2 rounded border-gray-800 bg-black" />
                Remember me
              </label>
              <Link to="/forgot-password" className="text-gray-400 text-sm hover:text-white">
                Forgot password?
              </Link>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-white text-black font-medium rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black mx-auto" />
              ) : (
                <span className="flex items-center justify-center space-x-2">
                  <LogIn className="h-4 w-4" />
                  <span>Sign In</span>
                </span>
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 pt-6 border-t border-gray-900">
            <p className="text-center text-gray-400 text-sm">
              Don't have an account?{' '}
              <Link to="/signup" className="text-white hover:underline">
                Create Account
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-gray-600 text-xs">
            © 2025 ORCA Trading Platform. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MinimalSignIn;
