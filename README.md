# RT_changes

Computes a ranking of authors who receive tweets on specific time intervals

## Usage

`main.py <INFILE> <OUTFILE> [-f [FIELDS] ] [ -e [EXTENSION]]`

* **-a** | **- -alpha**: An alpha value (default = 0.005).
* **-g** | **- -granularity**: The time interval. You can use any offset alias for Pandas time series.
 
## Time series

Some allowed values are:

* H: Hours
* M: Minutes
* Y: Years
* W: Weeks
* S: Seconds

A complete description of allowed aliases can be found at: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
