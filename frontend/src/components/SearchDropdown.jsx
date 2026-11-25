import { useState, useEffect, useContext } from "react";
import Select from "react-select";
import { AuthContext } from "../auth/AuthContext";
import "../assets/styles/search.css"

const API_URL = import.meta.env.VITE_API_URL;

const SearchDropdown = ({ onAddCity }) => {
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);
  const [error, setError] = useState("");
  const auth = useContext(AuthContext);

  useEffect(() => {
    const fetchOptions = async (tokenOverride = null) => {
      const token = tokenOverride || auth.accessToken;
      if (!token) return;

      try {
        const response = await fetch(`${API_URL}/api/search`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        });

        if (response.status === 401 && !tokenOverride) {
          const newToken = await auth.refreshAccessToken();
          if (newToken) return fetchOptions(newToken);
          return;
        }

        const data = await response.json();
        const formattedOptions = data.map((city) => ({
          value: city.id,
          label: city.name,
        }));
        setOptions(formattedOptions);
      } catch (err) {
        console.error("Error fetching city options:", err);
      }
    };

    fetchOptions();
  }, []);

  const handleChange = (option) => {
    setSelectedOption(option);
    setError("");
  };

  const handleSubmit = async (tokenOverride = null) => {
    setError("");
    const token = tokenOverride || auth.accessToken;

    if (!selectedOption) {
      setError("Please select a city first.");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/add`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
        body: JSON.stringify({ itemName: selectedOption.label }),
      });

      if (response.status === 401 && !tokenOverride) {
        const newToken = await auth.refreshAccessToken();
        if (newToken) return handleSubmit(newToken);
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Could not add city.");
        return;
      }

      if (onAddCity) {
        onAddCity();
      }
      setSelectedOption(null);
    } catch (err) {
      console.error("Error adding city:", err);
      setError("Network error. Please try again.");
    }
  };

  return (
    <div className="search_component">
      <div className="search_field">
        <Select
          options={options}
          value={selectedOption}
          onChange={handleChange}
          placeholder="Search..."
          isClearable
        />
      </div>

      <div className="search_button_div">
        <button className="search_btn" onClick={() => handleSubmit()}>
          Submit
        </button>
      </div>

      {error && <p className="error_message">{error}</p>}
    </div>
  );
};

export default SearchDropdown;
