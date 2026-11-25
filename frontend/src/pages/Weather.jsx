import { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../auth/AuthContext";
import Navbar from "../components/Navbar"
import SearchDropdown from "../components/SearchDropdown"
import CardComponent from "../components/CardComponent";
import '../App.css'


const API_URL = import.meta.env.VITE_API_URL;

export default function Weather(){
    const[fetchData, setFetchData] = useState([]);

    const navigate = useNavigate();
    const auth = useContext(AuthContext);

    const showWeatherData = async (tokenOverride = null) => {
        const token = tokenOverride || auth.accessToken;
        if(!token) return;

        try {
            const response = await fetch(`${API_URL}/api/weather`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                credentials: "include"
            });

            if(response.status === 401 && !tokenOverride){
                const newToken = await auth.refreshAccessToken();
                if(newToken){
                    return showWeatherData(newToken)
                } else {
                    navigate("/login");
                    return;
                }
            }
            const data = await response.json();
            setFetchData(data);

        } catch (error) {
            console.error("Error fetching weather data:", error);
        }
    }

    useEffect(()=>{
        showWeatherData();
    }, []);

    const handleDelete = async (cityId, tokenOverride = null) => {
        const token = tokenOverride || auth.accessToken;

        try {
            const response = await fetch(`${API_URL}/api/${cityId}/delete`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                credentials: "include"
            })

            if(response.status === 401 && !tokenOverride){
                const newToken = await auth.refreshAccessToken();
                if(newToken){
                    return handleDelete(cityId, newToken)
                }
            }
            if(response.ok){
                setFetchData((prevItems) => 
                    Array.isArray(prevItems)
                    ? prevItems.filter((item)=>item.city_id !== cityId)
                    : []
                )
            }
        } catch (error){
            console.error("Error deleting city:", error)
        }
    }

    return(
        <>
            <Navbar/>
            <SearchDropdown onAddCity={showWeatherData} />

            <div className="card_wrapper">
                {fetchData.message ? (
                    <div>{fetchData.message}</div>
                ) : (
                    Array.isArray(fetchData) &&
                    fetchData.map((fetchedCity) => (
                        <CardComponent
                            key={fetchedCity.city_id}
                            {...fetchedCity}
                            handleDelete={handleDelete}
                        />
                    ))
                )}
            </div>
        </>
    )
}
