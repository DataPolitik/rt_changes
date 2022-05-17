# RT_changes

Computes a ranking of authors who receive tweets on specific time intervals

## Usage

`main.py <INFILE> <OUTFILE> [-f [FIELDS] ] [ -e [EXTENSION]]`

* **-a** | **- -alpha**: An alpha value (default = 0.005).
* **-g** | **- -granularity**: The time interval. You can use any offset alias for Pandas time series.
* **-t** | **- -threshold**: Removes users whose sum of scores are below the specific threshold.
* **-i** | **- -interval**: Specify a time interval to process.
 
## Interval

The paramenter -i waits for two dates separated by a comma (eg: start_time,end_time) the format should be according
YYYY-MM-DD-HH:MM:SS.

## Time series

Some allowed values are:

* H: Hours
* M: Minutes
* Y: Years
* W: Weeks
* S: Seconds

A complete description of allowed aliases can be found at: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
