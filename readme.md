# Significance Web App
The app empowers you to run straigthfoward A/B testing.

## Features
- Import a csv file with your test data
- Select the variable you'd like to test
- Choose the type of variable (proportion or continuous) and the level of significance and power
- Perform sanity checks (SMR and Power Analysis) to be aware of the robutness of the results
- Check if a metric is significant or not through simulation of the experiment
- Visualize the distribution of the chosen metric and how it differs between variants
- Go further than the mean and visualize if indeed there are significant differences at percentiles using bootstrapp

## How to use
The data ideally should be a csv. For the app to work properly, one of the column should be name "variant" that serves to split the data into control and variation. The rest of the columns can be wathever KPI you'd like to test. 

## Installation
Copy the repo and install dependencies using pipenv

```
pipenv shell
pipenv install
```

Run the app...

```
streamlit run app.py
```

## Next steps
- Dockerize
- Calculate significance in batch of multiple metrics
- Support for A/B/n

## References
- Recreating Netflix’s quantile bootstrapping in R [https://towardsdatascience.com/recreating-netflixs-quantile-bootstrapping-in-r-a4739a69adb6]
- Elements of Data Science Book [https://allendowney.github.io/ElementsOfDataScience/13_hypothesis.html]