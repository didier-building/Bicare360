import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>('light');
  const [isLoaded, setIsLoaded] = useState(false);

  const applyTheme = (newTheme: Theme) => {
    console.log('Applying theme:', newTheme, 'to document.documentElement');
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
      console.log('Added dark class. Current classes:', document.documentElement.className);
    } else {
      document.documentElement.classList.remove('dark');
      console.log('Removed dark class. Current classes:', document.documentElement.className);
    }
  };

  // Load theme from localStorage on mount
  useEffect(() => {
    console.log('ThemeProvider mounting, initializing theme...');
    // First, clear the dark class to ensure clean state
    document.documentElement.classList.remove('dark');
    
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    // Default to light mode, only use dark if explicitly saved
    const initialTheme = savedTheme === 'dark' ? 'dark' : 'light';
    
    console.log('Initial theme:', initialTheme, 'saved:', savedTheme, 'prefersDark:', prefersDark);
    
    // Set initial theme to light if no saved preference
    if (!savedTheme) {
      localStorage.setItem('theme', 'light');
    }
    
    applyTheme(initialTheme);
    setThemeState(initialTheme);
    setIsLoaded(true);
  }, []);

  const setTheme = (newTheme: Theme) => {
    console.log('setTheme called with:', newTheme);
    console.log('Previous theme state:', theme);
    // Update state first
    setThemeState(newTheme);
    // Then apply to DOM immediately for visual feedback
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  const toggleTheme = () => {
    setThemeState((prevTheme) => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      console.log('toggleTheme:', prevTheme, '->', newTheme);
      localStorage.setItem('theme', newTheme);
      applyTheme(newTheme);
      return newTheme;
    });
  };

  // Don't render until theme is loaded to prevent flashing
  if (!isLoaded) {
    return <>{children}</>;
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export { useTheme };
