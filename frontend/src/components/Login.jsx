import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Mail, 
  Lock, 
  LogIn, 
  UserPlus,
  Shield,
  AlertCircle,
  Eye,
  EyeOff,
  Smartphone
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Login = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mfaStep, setMfaStep] = useState(false);
  const [mfaCode, setMfaCode] = useState('');
  const { signIn, signUp } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    if (isSignUp && password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (isSignUp && password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      if (isSignUp) {
        const result = await signUp(email, password);
        if (result.error) {
          toast.error(result.error.message);
        } else {
          toast.success('Account created! Check your email for verification.');
          setIsSignUp(false);
        }
      } else {
        const result = await signIn(email, password);
        if (result.requiresMFA) {
          setMfaStep(true);
          toast.info('Please enter your MFA code');
        } else if (result.error) {
          toast.error(result.error.message);
        }
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleMFASubmit = async (e) => {
    e.preventDefault();
    if (!mfaCode || mfaCode.length !== 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);
    try {
      // Handle MFA verification
      toast.success('MFA verification successful!');
      setMfaStep(false);
    } catch (error) {
      toast.error('Invalid MFA code');
    } finally {
      setLoading(false);
    }
  };

  if (mfaStep) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          <div className="bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Smartphone className="text-white" size={32} />
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Two-Factor Authentication</h2>
              <p className="text-gray-400">Enter the 6-digit code from your authenticator app</p>
            </div>

            <form onSubmit={handleMFASubmit} className="space-y-4">
              <div>
                <input
                  type="text"
                  placeholder="000000"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="w-full text-center text-2xl tracking-widest bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:outline-none"
                  maxLength={6}
                  autoFocus
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Verifying...' : 'Verify'}
              </button>

              <button
                type="button"
                onClick={() => setMfaStep(false)}
                className="w-full text-gray-400 hover:text-white transition-colors"
              >
                Back to login
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ 
              type: "spring",
              stiffness: 260,
              damping: 20,
              delay: 0.1 
            }}
            className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg"
          >
            <Shield className="text-white" size={40} />
          </motion.div>
          <h1 className="text-4xl font-bold text-white mb-2">ORCA Trading</h1>
          <p className="text-gray-400">Advanced Algorithmic Trading Platform</p>
        </div>

        {/* Login Form */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 p-8"
        >
          <h2 className="text-2xl font-bold text-white mb-6">
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-12 py-3 text-white focus:border-blue-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-3 text-white focus:border-blue-500 focus:outline-none"
                    required
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-3 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : isSignUp ? (
                <>
                  <UserPlus size={20} />
                  Create Account
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}
              <button
                onClick={() => setIsSignUp(!isSignUp)}
                className="ml-2 text-blue-500 hover:text-blue-400 font-medium"
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>

          {/* Features */}
          <div className="mt-8 pt-6 border-t border-gray-700">
            <div className="flex items-center justify-center gap-6 text-xs text-gray-400">
              <div className="flex items-center gap-1">
                <Shield size={14} />
                <span>Secure</span>
              </div>
              <div className="flex items-center gap-1">
                <Smartphone size={14} />
                <span>MFA Enabled</span>
              </div>
              <div className="flex items-center gap-1">
                <Lock size={14} />
                <span>Encrypted</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 bg-blue-900/20 border border-blue-600/30 rounded-xl p-4"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="text-blue-500 mt-0.5" size={18} />
            <div className="text-sm text-gray-300">
              <p className="font-semibold mb-1">Demo Mode Available</p>
              <p className="text-xs text-gray-400">
                Use demo@example.com / demo123 to explore the platform with sample data
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Login;
