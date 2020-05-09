# Spotify Sentiment *by Ollie Hooper*  
  
The aim of this project is to map and analyse the sentiments of different countries based on their music tastes over time.  
The data is presented in a web app coded in Python using the [Plotly Dash](https://github.com/plotly/dash) package.  
You can find a live version of the project [here]() and the source code is [here](https://github.com/Ollie-Hooper/SpotifySentiment).
  
## How it works  
  
**Spotify Charts**  
The track constituents of the Spotify Top 200 charts are scraped for every week and every country. You can find the charts [here](spotifycharts.com).

**Spotify Web API and Track Audio Features**  
The track audio features for all the tracks in the charts are retrieved via the Spotify Web API. You can find documentation describing the different [audio features](https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/).

**Data analysis**  
Raw scores for each audio feature are calculated by the mean value of all the tracks in the chart of a country for each point in time. These scores are then also standardised for each country over time to allow for comparison between countries and points in time.

**Data Visualisation**  
The data is visualised in 5 different ways:
* **Map** - A choropleth map visualises the z-scores for a singular audio feature at one point in time (default latest). The audio feature that is mapped can be selected from the dropdown and the week can be changed using the slider. Countries can be selected by clicking on them.
* **Country specific**  
  * **Description** - A dynamic description of the current sentiment of the country relative to their history is displayed below the country name.
  * **Profile** - A polar histogram plots the mean raw score normalised against every other country for every audio feature. Therefore a 1 indicates it has the highest audio feature score and 0 the lowest.
  * **Distribution** - A chart plots the distributions of the audio feature raw scores for a country.
  * **Time series** - A time series chart plots the z-scores of the audio features over time for the selected country. The series that are plotted on the chart can be altered by clicking the legend labels (double clicking singles out a feature).