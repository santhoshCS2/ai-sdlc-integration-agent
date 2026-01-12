import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { MESSAGES } from '../constants/messages';
import { useAuth } from '../hooks/useAuth';
import { ROUTES } from '../constants/routes';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string(),
});

const Login = () => {
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<{ email: string, password: string }>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: { email: string, password: string }) => {
    try {
      setError('');
      await login({ username: data.email, password: data.password });
      navigate(ROUTES.HOME);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg).join(', '));
      } else {
        setError(MESSAGES.AUTH.LOGIN_FAILED);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-900/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-md w-full space-y-8 glass-panel p-8 relative z-10 animate-fade-in">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-white">
            Welcome Back
          </h2>
          <p className="mt-2 text-center text-sm text-zinc-400">
            Sign in to access Coastal Seven
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="bg-red-900/50 border border-red-800 text-red-200 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-1">
                Email address
              </label>
              <input
                {...register('email')}
                type="email"
                className="input-field"
                placeholder="Ex. john@company.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
              )}
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="password" className="block text-sm font-medium text-zinc-300">
                  Password
                </label>
                <a href="#" className="text-sm font-medium text-accent hover:text-accent/80 transition-colors">
                  Forgot password?
                </a>
              </div>
              <input
                {...register('password')}
                type="password"
                className="input-field"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full btn-primary"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-center mt-4">
            <p className="text-sm text-zinc-500">
              Don't have an account?{' '}
              <Link to={ROUTES.REGISTER} className="font-medium text-accent hover:text-accent/80 transition-colors">
                Create one now
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;