import React, { createContext, useContext, useEffect, useState } from 'react';

type ThemeContextType = {
    accentColor: string;
    setAccentColor: (color: string) => void;
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [accentColor, setAccentColor] = useState(() => {
        return localStorage.getItem('theme-accent') || '#6366f1';
    });

    useEffect(() => {
        const root = document.documentElement;
        root.style.setProperty('--color-accent', accentColor);

        // Convert hex to rgb for tailwind opacity support
        const hex = accentColor.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        root.style.setProperty('--color-accent-rgb', `${r}, ${g}, ${b}`);
        localStorage.setItem('theme-accent', accentColor);
    }, [accentColor]);

    return (
        <ThemeContext.Provider value={{ accentColor, setAccentColor }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
