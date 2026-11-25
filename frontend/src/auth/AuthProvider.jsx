import { useState, useEffect} from "react";
import { AuthContext } from "./AuthContext.jsx"

const API_URL = import.meta.env.VITE_API_URL;

export const AuthProvider = (props) => {
    const { children } = props

    const[accessToken, setAccessToken] = useState(null);
    const[user, setUser] = useState(null);
    const[loading, setLoading] = useState(true)

    // fetching a new access token using a refresh token
    const refreshAccessToken = async() => {
        try {
            const response = await fetch(`${API_URL}/api/refresh`, {
                method: "POST",
                credentials: "include"
            });

            if (!response.ok){
                setAccessToken(null);
                setUser(null);
                return null;
            }

            const data = await response.json();
            setAccessToken(data.access_token);
            if(data.user_info){
                setUser(data.user_info);
            }
            return data.access_token;

        } catch (error) {
            console.error(error)
            setAccessToken(null);
            setUser(null);
            return null;
        }
    };

    // Restoring session on initial page load or reload
    useEffect(()=>{
        const startUp = async () => {
            await refreshAccessToken()
            setLoading(false);
        };
        startUp();
    }, []);

    // Login
    const login = async(email, password) => {
        const response = await fetch(`${API_URL}/api/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include",
            body: JSON.stringify({ email, password })
        });

        const data = await response.json()

        if(!response.ok){
            throw new Error(data.message || "Invalid user credentials")
        }
        setAccessToken(data.access_token)
        setUser(data.user_info)
    }

    // logout
    const logout = async() => {
        try{
            await fetch(`${API_URL}/api/logout`, {
                method: "POST",
                headers: { Authorization: `Bearer ${accessToken}`},
                credentials: "include"
            })
        } catch (error) {
            console.error("Logout error", error);
        } finally {
            setAccessToken(null)
            setUser(null)
        }
    }

    const auth = {
        accessToken,
        user,
        loading,
        isAuthenticated: Boolean(accessToken),
        login,
        logout,
        refreshAccessToken,
    }

    return (
        <AuthContext.Provider value={auth}>
            {children}
        </AuthContext.Provider>
    )

}

