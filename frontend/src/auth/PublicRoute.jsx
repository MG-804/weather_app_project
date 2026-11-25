import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";

export const PublicRoute = (props) => {
    const { children } = props;
    const auth = useContext(AuthContext);

    if(auth.loading){
        return(
            <div>Loading...</div>
        )
    }

    if(auth.isAuthenticated){
        return(
            <Navigate to="/weather" replace={true}/>
        )
    }
    return children;

}