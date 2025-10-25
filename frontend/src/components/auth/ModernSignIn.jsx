import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  LogIn,
  Sparkles,
  TrendingUp,
  Shield,
  Zap,
  ChevronRight
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';

const ModernSignIn = () => {
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

  const features = [
    { icon: <TrendingUp className="w-5 h-5" />, text: "Real-time Trading" },
    { icon: <Shield className="w-5 h-5" />, text: "Secure Platform" },
    { icon: <Zap className="w-5 h-5" />, text: "Lightning Fast" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex">
      {/* Left Side - Sign In Form */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full lg:w-1/2 flex items-center justify-center p-8"
      >
        <div className="w-full max-w-md space-y-8">
          {/* Logo and Title */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gradient-to-r from-purple-600 to-pink-600">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-gray-300">Sign in to access your trading dashboard</p>
          </motion.div>

          {/* Sign In Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-white/10 backdrop-blur-xl border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Sign In</CardTitle>
                <CardDescription className="text-gray-300">
                  Enter your credentials to continue
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-white">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="name@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10 bg-white/10 text-white placeholder:text-gray-400"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-white">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10 bg-white/10 text-white placeholder:text-gray-400"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="flex items-center text-sm text-gray-300">
                      <input type="checkbox" className="mr-2 rounded" />
                      Remember me
                    </label>
                    <Link to="/forgot-password" className="text-sm text-purple-400 hover:text-purple-300">
                      Forgot password?
                    </Link>
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                    disabled={loading}
                    size="lg"
                  >
                    {loading ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      />
                    ) : (
                      <>
                        Sign In
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
              <CardFooter className="flex flex-col space-y-4">
                <div className="relative w-full">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-gray-600" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-gray-900 px-2 text-gray-400">Or continue with</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 w-full">
                  <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                    Google
                  </Button>
                  <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                    GitHub
                  </Button>
                </div>

                <p className="text-center text-sm text-gray-300">
                  Don't have an account?{' '}
                  <Link to="/signup" className="text-purple-400 hover:text-purple-300 font-medium">
                    Sign up
                  </Link>
                </p>
              </CardFooter>
            </Card>
          </motion.div>
        </div>
      </motion.div>

      {/* Right Side - Feature Showcase */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="hidden lg:flex lg:w-1/2 items-center justify-center p-8 relative"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-3xl" />
        
        <div className="relative z-10 max-w-md space-y-8">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.6 }}
            className="text-center"
          >
            <h2 className="text-5xl font-bold text-white mb-4">
              ORCA Trading Platform
            </h2>
            <p className="text-xl text-gray-200 mb-8">
              Advanced algorithmic trading at your fingertips
            </p>
          </motion.div>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                className="flex items-center space-x-4 p-4 bg-white/10 backdrop-blur-md rounded-lg border border-white/20"
              >
                <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-gradient-to-r from-purple-600 to-pink-600">
                  {feature.icon}
                </div>
                <span className="text-white font-medium">{feature.text}</span>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="pt-8"
          >
            <div className="flex items-center justify-center space-x-2 text-gray-300">
              <Shield className="w-4 h-4" />
              <span className="text-sm">Bank-level encryption</span>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default ModernSignIn;
