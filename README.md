# RT_changes

Computes a ranking of authors who receive retweets on specific time intervals.

## Requirements

Twarc-count requires Python 3.7 or greater and pip.

## Installation

You need to clone this repository.

`git clone https://github.com/DataPolitik/rt_changes.git`

And then, move to the folder **rt_changes**. Then, install all modules required by the script:

`pip install -r requirements.txt`

## Usage

`changes.py <INFILE> <OUTFILE> [-f [FIELDS] ]`

* **-a** | **- -alpha**: An alpha value (default = 0.005).
* **-g** | **- -granularity**: The time interval. You can use any offset alias for Pandas time series.
* **-t** | **- -threshold**: Removes users whose sum of scores are below the specific threshold.
* **-i** | **- -interval**: Specify a date period to process.
 
## Interval parameter

The paramenter -i waits for two dates separated by a comma (eg: start_time,end_time) the format should be according
YYYY-MM-DD-HH:MM:SS.

## Granularity

Some allowed values are:

* H: Hours
* M: Minutes
* Y: Years
* W: Weeks
* S: Seconds

A complete description of allowed aliases can be found at: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

## Examples

### Computes a simple ranking

`changes.py examples\results.json output.csv`

### Computes a weekly ranking

`changes.py examples\results.json output.csv -g W`

### Removes all user under 50 points

`changes.py examples\results.json output.csv -t 50`

### Compute data from an specific date interval

`changes.py  examples/results.json output -i 2021-10-18,2022-10-18`
