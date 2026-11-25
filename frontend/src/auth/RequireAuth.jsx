import { useContext } from "react";
import { Navigate, useLocation } from 'react-router-dom'
import { AuthContext } from "./AuthContext";

export const RequireAuth = (props) => {
    const { children } = props;
    const auth = useContext(AuthContext);

    const location = useLocation()

    if(auth.loading){
        return(
            <div>Loading...</div>
        )
    }
    if(!auth.isAuthenticated){
        return(
            <Navigate to="/login" replace={true} state={{ from: location }}/>
        )
    }
    return children;

}