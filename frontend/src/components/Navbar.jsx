import { useContext } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AuthContext } from "../auth/AuthContext";
import "../assets/styles/navbar_style.css"
import { faCloudSun } from '@fortawesome/free-solid-svg-icons'
import  { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

export default function Navbar(){
    const auth = useContext(AuthContext);
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = async() => {
        await auth.logout();
        navigate("/")
    }

    return (
        <div className="navbar_wrapper">
            <div className="logo_wrapper">
                <Link to={auth.isAuthenticated ?  "/weather" : "/"}>
                    <FontAwesomeIcon icon={faCloudSun} className="logo-icon"/>
                </Link>
            </div>

            <div className="buttons">
                {auth.isAuthenticated ? (
                    <>
                        {auth.user?.firstName && (
                            <div>Hey, {auth.user.firstName}! &nbsp;</div>
                        )}
                        <button className="button logOut_button" onClick={handleLogout}>
                            Log Out
                        </button>
                    </>
                ) : (
                    location.pathname === "/" && (
                        <>
                            <Link to="/login" className="link">
                                <div className="button login_button">Log in</div>
                            </Link>
                            <Link to="/register" className="link">
                                <div className="button reg_button">Sign up</div>
                            </Link>
                        </>
                    )
                )
            }
            </div>
        </div>

    );
}