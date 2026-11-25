import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../assets/styles/login.css"

const API_URL = import.meta.env.VITE_API_URL;

export default function Register(){
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const navigate = useNavigate();

    const handleReg = async(event) => {
        event.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            const response = await fetch(`${API_URL}/api/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ firstName, lastName, email, password })
            });

            const data = await response.json();

            if(!response.ok) {
                throw new Error(data.message || "Error when signing up")
            }

            navigate("/login", { replace: true })
        } catch (err) {
            setError(err.message || "Please try again");
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <>
          <Navbar />
          <form onSubmit={handleReg} className="login_form">
            <h2 className="login_text">
                Sign up for free to create your custom weather list!
            </h2>

            {error && <p className="error_message">{error}</p>}

            <input
                type="text"
                value={firstName}
                onChange={(event) => setFirstName(event.target.value)}
                placeholder="First name"
                required
            />
            <input 
                type="text" 
                value={lastName}
                onChange={(event) => setLastName(event.target.value)}
                placeholder="Last name"
                required
            />
            <input 
                type="text"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="Email"
                required
            />
            <input 
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Password"
                required
            />
            <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Signing up..." : "Sign up"}
            </button>

            <p>
                Already have an account? <Link to="/login">Log in</Link>
            </p>
          </form>  
        </>
    );
};