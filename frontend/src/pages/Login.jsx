import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../auth/AuthContext";
import Navbar from "../components/Navbar";
import "../assets/styles/login.css"

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const navigate = useNavigate();
    const auth = useContext(AuthContext);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setIsSubmitting(true)

        try {
            await auth.login(email, password);
            navigate("/weather")
        } catch (err) {
            setError(err.message || "Login failed.")
        } finally {
            setIsSubmitting(false);
        }
    }

    return(
        <>
            <Navbar />
            <form onSubmit={handleLogin} className="login_form">
                <h2 className="login_text">Log in to get access to your weather list</h2>

                {error && <p className="error_message">{error}</p>}

                <input 
                    type="email"
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
                    {isSubmitting ? "Logging in..." : "Login"}
                </button>

                <p>
                    Don&apos;t have an account? <Link to="/register">Register</Link>
                </p>
            </form>
        </>
    )

}