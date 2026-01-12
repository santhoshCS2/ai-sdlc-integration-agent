import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../hooks/useAuth';
import { RegisterData } from '../types';

const registerSchema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

const Register = () => {
  const [error, setError] = useState('');
  const { register: registerUser, login } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterData>({
    resolver: zodResolver(registerSchema),
  });

  const [success, setSuccess] = useState('');

  const onSubmit = async (data: RegisterData) => {
    try {
      setError('');
      await registerUser(data);
      setSuccess('Account created successfully! Logging you in...');

      // Auto-login after successful registration
      await login({ username: data.email, password: data.password });

      // Short delay to show success message before redirect
      setTimeout(() => {
        navigate('/');
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-purple-900/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-md w-full space-y-8 glass-panel p-8 relative z-10 animate-fade-in">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-white">
            Create Account
          </h2>
          <p className="mt-2 text-center text-sm text-zinc-400">
            Join SDLC Agent and manage your projects
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {success && (
            <div className="bg-green-900/50 border border-green-800 text-green-200 px-4 py-3 rounded-lg text-sm animate-fade-in">
              {success}
            </div>
          )}
          {error && (
            <div className="bg-red-900/50 border border-red-800 text-red-200 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-zinc-300 mb-1">
                  First Name
                </label>
                <input
                  {...register('first_name')}
                  type="text"
                  className="input-field"
                  placeholder="First name"
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-400">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-zinc-300 mb-1">
                  Last Name
                </label>
                <input
                  {...register('last_name')}
                  type="text"
                  className="input-field"
                  placeholder="Last name"
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-400">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-1">
                Email address
              </label>
              <input
                {...register('email')}
                type="email"
                className="input-field"
                placeholder="john@company.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-zinc-300 mb-1">
                Password
              </label>
              <input
                {...register('password')}
                type="password"
                className="input-field"
                placeholder="Create a password"
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
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          <div className="text-center mt-4">
            <p className="text-sm text-zinc-500">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-accent hover:text-accent/80 transition-colors">
                Sign in instead
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;