"""
AuthFlowFixerAgent - Fixes authentication flow and routing issues in frontend
"""

from typing import Dict, Any, List
from pathlib import Path
import re
from app.agents.coding.utils.logger import StreamlitLogger

class AuthFlowFixerAgent:
    """Agent that fixes authentication flow and routing in frontend applications"""
    
    def __init__(self, llm, logger: StreamlitLogger):
        self.llm = llm
        self.logger = logger
    
    def fix_authentication_flow(self, frontend_path: Path) -> Dict[str, Any]:
        """Fix authentication flow and routing issues"""
        
        self.logger.log("🔐 Fixing authentication flow and routing...")
        
        results = {
            "files_modified": 0,
            "auth_issues_fixed": [],
            "routing_issues_fixed": [],
            "new_files_created": []
        }
        
        # 1. Find and analyze main app files
        app_files = self._find_app_files(frontend_path)
        
        # 2. Check for authentication bypass issues
        for app_file in app_files:
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                auth_issues = self._detect_auth_bypass_issues(content, app_file.name)
                
                if auth_issues:
                    self.logger.log(f"🚨 {app_file.name}: Found {len(auth_issues)} auth bypass issues")
                    for issue in auth_issues:
                        self.logger.log(f"  ❌ {issue}")
                    
                    # Fix authentication issues
                    fixed_content = self._fix_auth_bypass(content, app_file.name)
                    
                    if fixed_content != content:
                        with open(app_file, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        results["files_modified"] += 1
                        results["auth_issues_fixed"].extend(auth_issues)
                        self.logger.log(f"✅ Fixed authentication flow in {app_file.name}")
            
            except Exception as e:
                self.logger.log(f"⚠️ Error processing {app_file.name}: {str(e)}", level="warning")
        
        # 3. Create missing authentication components
        auth_components = self._create_auth_components(frontend_path)
        results["new_files_created"].extend(auth_components)
        
        # 4. Fix routing configuration
        routing_fixes = self._fix_routing_config(frontend_path)
        results["routing_issues_fixed"].extend(routing_fixes)
        
        self.logger.log(f"🔐 Authentication Flow Fix Summary:")
        self.logger.log(f"  📁 Files modified: {results['files_modified']}")
        self.logger.log(f"  🚨 Auth issues fixed: {len(results['auth_issues_fixed'])}")
        self.logger.log(f"  🛣️ Routing issues fixed: {len(results['routing_issues_fixed'])}")
        self.logger.log(f"  📄 New files created: {len(results['new_files_created'])}")
        
        return results
    
    def _find_app_files(self, frontend_path: Path) -> List[Path]:
        """Find main application files"""
        app_files = []
        src_path = frontend_path / "src"
        
        if not src_path.exists():
            return app_files
        
        # Look for main app files
        patterns = [
            "App.jsx", "App.js", "App.tsx", "App.ts",
            "main.jsx", "main.js", "main.tsx", "main.ts",
            "index.jsx", "index.js", "index.tsx", "index.ts"
        ]
        
        for pattern in patterns:
            matches = list(src_path.rglob(pattern))
            app_files.extend(matches)
        
        return app_files
    
    def _detect_auth_bypass_issues(self, content: str, filename: str) -> List[str]:
        """Detect authentication bypass issues"""
        issues = []
        
        # Check for direct routing without auth check
        if re.search(r'<Route.*path.*element.*>', content) and 'ProtectedRoute' not in content:
            issues.append("Routes not protected with authentication")
        
        # Check for missing login/register routes
        if '<Route' in content:
            if not re.search(r'path.*["\'/]login["\']', content):
                issues.append("Missing login route")
            if not re.search(r'path.*["\'/]register["\']', content):
                issues.append("Missing register route")
        
        # Check for hardcoded authentication bypass
        bypass_patterns = [
            r'isAuthenticated\s*=\s*true',
            r'loggedIn\s*=\s*true',
            r'authenticated\s*=\s*true',
            r'user\s*=\s*\{[^}]*\}',  # Hardcoded user object
        ]
        
        for pattern in bypass_patterns:
            if re.search(pattern, content):
                issues.append(f"Hardcoded authentication bypass: {pattern}")
        
        # Check for missing authentication state management
        if 'useState' in content and not any(auth_term in content.lower() for auth_term in ['auth', 'login', 'token', 'user']):
            if 'Route' in content or 'router' in content.lower():
                issues.append("Missing authentication state management")
        
        return issues
    
    def _fix_auth_bypass(self, content: str, filename: str) -> str:
        """Fix authentication bypass issues"""
        
        # Add authentication imports if missing
        if 'useState' in content and 'useEffect' in content:
            if 'AuthContext' not in content and 'createContext' not in content:
                # Add auth context import
                import_pattern = r'(import.*from ["\']react["\'];?)'
                if re.search(import_pattern, content):
                    content = re.sub(
                        import_pattern,
                        r'\1\nimport { AuthProvider, useAuth } from "./contexts/AuthContext";',
                        content
                    )
        
        # Fix hardcoded authentication bypass
        content = re.sub(r'isAuthenticated\s*=\s*true', 'isAuthenticated = useAuth().isAuthenticated', content)
        content = re.sub(r'loggedIn\s*=\s*true', 'loggedIn = useAuth().isAuthenticated', content)
        content = re.sub(r'authenticated\s*=\s*true', 'authenticated = useAuth().isAuthenticated', content)
        
        # Remove hardcoded user objects
        content = re.sub(r'const\s+user\s*=\s*\{[^}]*\};?', 'const { user } = useAuth();', content)
        
        # Add authentication wrapper to App component
        if 'function App' in content or 'const App' in content:
            if 'AuthProvider' not in content:
                # Wrap the return statement with AuthProvider
                return_pattern = r'(return\s*\(?\s*<[^>]*>)'
                if re.search(return_pattern, content):
                    content = re.sub(
                        return_pattern,
                        r'return (\n    <AuthProvider>\1',
                        content
                    )
                    
                    # Close AuthProvider before the last closing tag
                    content = re.sub(r'(\s*</[^>]*>\s*\);?\s*$)', r'\1\n    </AuthProvider>\n  );', content)
        
        # Add protected routes
        if '<Route' in content and 'ProtectedRoute' not in content:
            # Replace unprotected routes with protected ones
            route_pattern = r'<Route\s+path="([^"]*)"[^>]*element=\{<([^>}]+)[^}]*\}[^>]*/?>'
            
            def replace_route(match):
                path = match.group(1)
                component = match.group(2)
                
                # Don't protect login/register routes
                if path in ['/login', '/register', '/']:
                    return match.group(0)
                
                return f'<Route path="{path}" element={{<ProtectedRoute><{component} /></ProtectedRoute>}} />'
            
            content = re.sub(route_pattern, replace_route, content)
        
        return content
    
    def _create_auth_components(self, frontend_path: Path) -> List[str]:
        """Create missing authentication components"""
        created_files = []
        src_path = frontend_path / "src"
        
        # Create contexts directory
        contexts_dir = src_path / "contexts"
        contexts_dir.mkdir(exist_ok=True)
        
        # Create AuthContext
        auth_context_path = contexts_dir / "AuthContext.jsx"
        if not auth_context_path.exists():
            auth_context_content = '''import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on app load
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token with backend
      setIsAuthenticated(true);
      // You can add user info fetching here
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await apiLogin(email, password);
      localStorage.setItem('token', response.access_token);
      setUser(response.user || { email });
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const register = async (email, username, password) => {
    try {
      const response = await apiRegister(email, username, password);
      localStorage.setItem('token', response.access_token);
      setUser(response.user || { email, username });
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
'''
            with open(auth_context_path, 'w', encoding='utf-8') as f:
                f.write(auth_context_content)
            created_files.append(str(auth_context_path))
            self.logger.log("✅ Created AuthContext.jsx")
        
        # Create components directory
        components_dir = src_path / "components"
        components_dir.mkdir(exist_ok=True)
        
        # Create ProtectedRoute component
        protected_route_path = components_dir / "ProtectedRoute.jsx"
        if not protected_route_path.exists():
            protected_route_content = '''import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
'''
            with open(protected_route_path, 'w', encoding='utf-8') as f:
                f.write(protected_route_content)
            created_files.append(str(protected_route_path))
            self.logger.log("✅ Created ProtectedRoute.jsx")
        
        # Create Login component
        login_path = components_dir / "Login.jsx"
        if not login_path.exists():
            login_content = '''import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error || 'Login failed');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div>
            <input
              type="email"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <input
              type="password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          <div className="text-center">
            <Link to="/register" className="text-indigo-600 hover:text-indigo-500">
              Don't have an account? Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
'''
            with open(login_path, 'w', encoding='utf-8') as f:
                f.write(login_content)
            created_files.append(str(login_path))
            self.logger.log("✅ Created Login.jsx")
        
        # Create Register component
        register_path = components_dir / "Register.jsx"
        if not register_path.exists():
            register_content = '''import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register(email, username, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error || 'Registration failed');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div>
            <input
              type="email"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <input
              type="text"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <input
              type="password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div>
            <input
              type="password"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
          <div className="text-center">
            <Link to="/login" className="text-indigo-600 hover:text-indigo-500">
              Already have an account? Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
'''
            with open(register_path, 'w', encoding='utf-8') as f:
                f.write(register_content)
            created_files.append(str(register_path))
            self.logger.log("✅ Created Register.jsx")
        
        return created_files
    
    def _fix_routing_config(self, frontend_path: Path) -> List[str]:
        """Fix routing configuration to include authentication"""
        fixes = []
        src_path = frontend_path / "src"
        
        # Find and fix App.jsx/App.js
        app_files = list(src_path.rglob("App.jsx")) + list(src_path.rglob("App.js"))
        
        for app_file in app_files:
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if routing needs to be added/fixed
                needs_routing_fix = False
                
                if 'BrowserRouter' not in content and 'Router' not in content:
                    needs_routing_fix = True
                
                if needs_routing_fix or not re.search(r'path.*["\'/]login["\']', content):
                    # Create proper routing structure
                    new_content = self._create_proper_routing(content, app_file.name)
                    
                    if new_content != content:
                        with open(app_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        fixes.append(f"Fixed routing in {app_file.name}")
                        self.logger.log(f"✅ Fixed routing configuration in {app_file.name}")
            
            except Exception as e:
                self.logger.log(f"⚠️ Error fixing routing in {app_file.name}: {str(e)}", level="warning")
        
        return fixes
    
    def _create_proper_routing(self, content: str, filename: str) -> str:
        """Create proper routing structure with authentication"""
        
        # Add necessary imports
        imports_to_add = []
        
        if 'BrowserRouter' not in content:
            imports_to_add.append('BrowserRouter as Router')
        if 'Routes' not in content:
            imports_to_add.append('Routes')
        if 'Route' not in content:
            imports_to_add.append('Route')
        if 'Navigate' not in content:
            imports_to_add.append('Navigate')
        
        if imports_to_add:
            router_import = f"import {{ {', '.join(imports_to_add)} }} from 'react-router-dom';"
            
            # Add router import after React import
            react_import_pattern = r'(import.*from ["\']react["\'];?)'
            if re.search(react_import_pattern, content):
                content = re.sub(react_import_pattern, r'\1\n' + router_import, content)
            else:
                content = router_import + '\n' + content
        
        # Add component imports
        component_imports = '''import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';'''
        
        # Add after router import
        if 'react-router-dom' in content:
            content = content.replace(
                "import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';",
                "import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';\n" + component_imports
            )
        
        # Replace the App component content with proper routing
        app_function_pattern = r'(function App\(\)[^{]*\{)(.*?)(\s*return[^;]*;?\s*\})'
        
        def replace_app_content(match):
            function_start = match.group(1)
            function_end = match.group(3)
            
            new_content = '''
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="*" 
            element={
              <ProtectedRoute>
                <div>Page not found</div>
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
'''
            return function_start + new_content + '\n}'
        
        if re.search(app_function_pattern, content, re.DOTALL):
            content = re.sub(app_function_pattern, replace_app_content, content, flags=re.DOTALL)
        
        return content