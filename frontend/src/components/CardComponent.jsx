// import '../App.css'
import  { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTrash } from '@fortawesome/free-solid-svg-icons'
import '../App.css'



function CardComponent( {city_id, city_name, temp, cond, humid, w_speed, day1_dt, day1_i, day1_t, day2_dt, day2_i, day2_t, day3_dt, day3_i, day3_t, day4_dt, day4_i, day4_t, day5_dt, day5_i, day5_t, handleDelete} ) {

    return (
              <div className='wrapper' key={city_id}>
              <div className='header'>
                <h2>{city_name}</h2>
                <p>{temp}°C</p>
                <p>{cond}</p>
              </div>

              <div className='weather-details'>
                <div>
                  <p>Humidity</p>
                  <p>{humid}%</p>
                </div>
                <div>
                  <p>Wind Speed</p>
                  <p>{w_speed}mph</p>
                </div>
              </div>

              <div className='forecast'>
                <h2 className='forecast-header'>5-Day Forecast</h2>
                <div className='forecast-days'>
                  <div className='forecast-day'>
                    <p>{day1_dt}</p>
                    <img
                        src={`http://openweathermap.org/img/wn/${day1_i}.png`}
                        alt='weather_icon'
                    />
                    <p>{day1_t}°C</p>
                  </div>
                  <div className='forecast-day'>
                    <p>{day2_dt}</p>
                    <img
                        src={`http://openweathermap.org/img/wn/${day2_i}.png`}
                        alt='weather_icon'
                    />
                    <p>{day2_t}°C</p>
                  </div>
                  <div className='forecast-day'>
                    <p>{day3_dt}</p>
                    <img
                        src={`http://openweathermap.org/img/wn/${day3_i}.png`}
                        alt='weather_icon'
                    />
                    <p>{day3_t}°C</p>
                  </div>
                  <div className='forecast-day'>
                    <p>{day4_dt}</p>
                    <img
                        src={`http://openweathermap.org/img/wn/${day4_i}.png`}
                        alt='weather_icon'
                    />
                    <p>{day4_t}°C</p>
                  </div>
                  <div className='forecast-day'>
                    <p>{day5_dt}</p>
                    <img
                        src={`http://openweathermap.org/img/wn/${day5_i}.png`}
                        alt='weather_icon'
                    />
                    <p>{day5_t}°C</p>
                  </div>
                  
                </div>
                <div className='analysis'>
                {
                  (temp < day5_t) ? 
                  (<p>It'll get warmer by {(day5_t - temp).toFixed(1)}°C</p>)
                  :
                  (<p>It'll get colder by {(temp - day5_t).toFixed(1)}°C</p>)
                }

              </div>
              </div>
              
              <div className='delete_button_wrapper'>

                <button className='delete_button' onClick={() => handleDelete(city_id)}><FontAwesomeIcon icon={faTrash}/></button>
              </div>
            </div>              
    )
}

export default CardComponent
