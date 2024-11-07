async function getWeather(cityInputValue) {
  var apiKey = "VK8AZQ82WD8X8RZKZ9DBJEGVQ"; // Ensure this is your correct API key
  var unit = "metric";
  var apiUrl = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${city}?unitGroup=${unit}&key=${apiKey}&contentType=json`;

  try {
    var response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    var data = await response.json();
    console.log(data);
  } catch (error) {
    console.error("Error fetching weather data:", error);
  }
}

// Example usage
var city = "Delhi";
getWeather(city);
