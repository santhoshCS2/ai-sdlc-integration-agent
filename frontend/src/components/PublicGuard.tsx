import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

import { ROUTES } from '../constants/routes';

interface PublicGuardProps {
    children: ReactNode;
}

const PublicGuard = ({ children }: PublicGuardProps) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center">
                {/* Optional: Show loader or just null to prevent flash */}
                <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (user) {
        return <Navigate to={ROUTES.HOME} replace />;
    }

    return <>{children}</>;
};

export default PublicGuard;
