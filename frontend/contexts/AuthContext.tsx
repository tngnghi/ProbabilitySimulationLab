'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { getToken, setToken, clearToken, decodeToken } from '@/lib/auth';

interface User {
    email: string;
    userId: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoggedIn: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setTokenState] = useState<string | null>(null);
    const router = useRouter();

    // Initialize from localStorage on mount
    useEffect(() => {
        const storedToken = getToken();
        if (storedToken) {
            const payload = decodeToken(storedToken);
            if (payload && payload.exp * 1000 > Date.now()) {
                setTokenState(storedToken);
                setUser({ email: payload.email, userId: payload.user_id });
            } else {
                // Expired token
                clearToken();
            }
        }
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({}));
            throw new Error(error.detail || 'Invalid email or password');
        }

        const data = await res.json();
        const jwt = data.access_token;
        setToken(jwt);
        const payload = decodeToken(jwt);
        setTokenState(jwt);
        setUser({ email: payload.email, userId: payload.user_id });
        router.push('/dashboard');
    }, [router]);

    const register = useCallback(async (email: string, password: string) => {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({}));
            throw new Error(error.detail || 'Registration failed');
        }
        router.push('/login');
    }, [router]);

    const logout = useCallback(() => {
        clearToken();
        setTokenState(null);
        setUser(null);
        router.push('/');
    }, [router]);

    return (
        <AuthContext.Provider
            value={{ user, token, isLoggedIn: !!user, login, register, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}