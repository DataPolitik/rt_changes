import json
import click
import os
import pandas as pd
from twarc import ensure_flattened
from io import TextIOWrapper

TEMPORAL_CSV_PATH = '.output.csv'


def process_dataframe(df):
    result_dictionary = dict()
    value_counts_result = df.author_name.value_counts()
    author_list = list(value_counts_result.index)

    for author in author_list:
        result_dictionary[author] = value_counts_result[author]

    return result_dictionary


@click.command()
@click.option('-a', '--alpha', type=click.FLOAT, required=False, default='0.005')
@click.option('-g', '--granularity', required=False, default='M', type=click.STRING)
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.STRING, default='-')
def main(infile: TextIOWrapper,
         outfile: str,
         alpha: float,
         granularity: str):

    f_output = open(TEMPORAL_CSV_PATH, 'w', encoding="utf-8")
    f_output.write("created_at,author_name,author_profile\n")
    profile_image_dictionary = dict()

    for line in infile:
        for tweet in ensure_flattened(json.loads(line)):
            if 'referenced_tweets' in tweet:
                for x in tweet['referenced_tweets']:
                    if 'retweeted' in x['type']:
                        author_name = x['author']['name']
                        author_profile = x['author']['profile_image_url']
                        created_at = tweet['created_at']
                        profile_image_dictionary[author_name] = author_profile
                        f_output.write("{},{},{}\n".format(created_at, author_name, author_profile))
    f_output.close()

    df = pd.read_csv(TEMPORAL_CSV_PATH)
    os.remove(TEMPORAL_CSV_PATH)
    df = df.dropna()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.to_period(granularity)
    unique_dates = list(df.created_at.unique())
    unique_dates.sort()
    unique_usernames = set(df.author_name.unique())
    dictionary_periods = dict()
    for username in unique_usernames:
        dictionary_periods[username] = []

    f_output = open(outfile, 'w', encoding="utf-8")
    f_output.write("datetime,author_name,count,profile_image_url\n")
    period = 0
    for date_period in unique_dates:
        df_filtered = df[df['created_at'] == date_period]
        result_dictionary = process_dataframe(df_filtered)
        ready_users = set()
        for username, count in result_dictionary.items():
            process_user(alpha, count, date_period, dictionary_periods,
                         f_output, period, username, profile_image_dictionary)
            ready_users.add(username)
        pending_users = unique_usernames.difference(ready_users)
        for pending_user in pending_users:
            process_user(alpha, 0, date_period, dictionary_periods,
                         f_output, period, pending_user, profile_image_dictionary)
        period = period + 1

    f_output.close()


def compute_score(username, period, alpha, dictionary):
    if period == -1:
        return 0
    return dictionary[username][period] + alpha * compute_score(username, period - 1, alpha, dictionary)


def process_user(alpha, count, date_period, dictionary_periods, f_output, period, username, profile_image_dict):
    value_period = count + alpha * compute_score(username, period - 1, alpha, dictionary_periods)
    dictionary_periods[username].append(value_period)
    profile_image = profile_image_dict[username]
    f_output.write("{},{},{},{}\n".format(date_period, username, value_period, profile_image))


if __name__ == '__main__':
    main()
