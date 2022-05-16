import json
import click
import os
import logging
import random
import pandas as pd
from twarc import ensure_flattened
from io import TextIOWrapper

logging.getLogger().setLevel(logging.INFO)
TEMPORAL_CSV_PATH = 'output.csv'

@click.command()
@click.option('-a', '--alpha', type=click.FLOAT, required=False, default='0.005')
@click.option('-g', '--granularity', required=False, default='M', type=click.STRING)
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.STRING, default='-')
def main(infile: TextIOWrapper,
         outfile: str,
         alpha: float,
         granularity: str):

    temporal_file_name = '.' + str(random.randint(0, 400)) + '_' + TEMPORAL_CSV_PATH
    f_output = open(temporal_file_name, 'w', encoding="utf-8")
    f_output.write("created_at,author_name,author_profile\n")
    profile_image_dictionary = dict()
    logging.info('Generating temporal output file: ' + temporal_file_name)
    for line in infile:
        for tweet in ensure_flattened(json.loads(line)):
            if 'referenced_tweets' in tweet:
                for x in tweet['referenced_tweets']:
                    if 'retweeted' in x['type']:
                        author_name = x['author']['username']
                        author_profile = x['author']['profile_image_url']
                        created_at = tweet['created_at']
                        profile_image_dictionary[author_name] = author_profile
                        f_output.write("{},{},{}\n".format(created_at, author_name, author_profile))
    f_output.close()

    logging.info('Temporal file generated.')

    df = pd.read_csv(temporal_file_name)
    df = df.dropna()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.to_period(granularity)
    unique_dates = list(df.created_at.unique())
    unique_dates.sort()
    unique_usernames = set(df.author_name.unique())
    dictionary_periods = dict()
    for username in unique_usernames:
        dictionary_periods[username] = []

    f_output = open(outfile, 'w', encoding="utf-8")
    f_output.write("profile_image_url,author_name")
    for unique_date in unique_dates:
        unique_date_str: str = str(unique_date).split('/')[0]
        f_output.write(',' + str(unique_date_str).replace(' ','_'))
    f_output.write("\n")

    logging.info('Computing user scores')
    user_count: int = 1
    total_users: int = len(unique_usernames)
    for user in unique_usernames:
        period: int = 0
        f_output.write(profile_image_dictionary[user])
        f_output.write(","+user)
        for date_period in unique_dates:
            df_filtered = df[df['author_name'] == user]
            df_filtered = df_filtered[df_filtered['created_at'] == date_period]
            number_of_rts = len(df_filtered.index)
            score = process_user(alpha, number_of_rts, dictionary_periods, period, user)
            f_output.write("," + str(score))
            period = period + 1
        f_output.write("\n")
        user_count = user_count + 1
        if user_count % 10 == 0:
            logging.info('{}/{}'.format(user_count, total_users))
    f_output.close()
    logging.info('User scores computed. Matrix file generated:' + outfile)
    os.remove(temporal_file_name)
    logging.info('Finished.')


def compute_score(username, period, alpha, dictionary):
    if period == -1:
        return 0
    return dictionary[username][period] + alpha * compute_score(username, period - 1, alpha, dictionary)


def process_user(alpha, count, dictionary_periods, period, username):
    value_period = count + alpha * compute_score(username, period - 1, alpha, dictionary_periods)
    dictionary_periods[username].append(value_period)
    return value_period


if __name__ == '__main__':
    main()
