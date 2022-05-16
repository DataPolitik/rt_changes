import csv
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


def generate_random_file_name():
    return '.' + str(random.randint(0, 20000)) + '_' + TEMPORAL_CSV_PATH


def set_score_value(username, score, dictionary):
    dictionary[username] = score


def get_score_value(username, dictionary):
    return dictionary[username]


def compute_score(username, count, alpha, dictionary):
    score = count + alpha * get_score_value(username, dictionary) if alpha > 0 else count
    set_score_value(username, score, dictionary)
    return score


@click.command()
@click.option('-a', '--alpha', type=click.FLOAT, required=False, default='0.005')
@click.option('-g', '--granularity', required=False, default='M', type=click.STRING)
@click.option('-t', '--threshold', required=False, default='2.0', type=click.FLOAT)
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.STRING, default='-')
def main(infile: TextIOWrapper,
         outfile: str,
         alpha: float,
         threshold: float,
         granularity: str):

    first_temporal_csv = generate_random_file_name()

    f_temp_output = open(first_temporal_csv, 'w', encoding="utf-8")
    f_temp_output.write("created_at,author_name,author_profile\n")

    profile_image_dictionary = dict()
    logging.info('Generating temporal output file: ' + first_temporal_csv)
    for line in infile:
        for tweet in ensure_flattened(json.loads(line)):
            if 'referenced_tweets' in tweet:
                for x in tweet['referenced_tweets']:
                    if 'retweeted' in x['type']:
                        author_name = x['author']['username']
                        author_profile = x['author']['profile_image_url']
                        created_at = tweet['created_at']
                        profile_image_dictionary[author_name] = author_profile
                        f_temp_output.write("{},{},{}\n".format(created_at, author_name, author_profile))
    f_temp_output.close()

    logging.info('Temporal file generated.')
    df = pd.read_csv(first_temporal_csv)
    df = df.dropna()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.to_period(granularity)
    unique_dates = list(df.created_at.unique())
    unique_dates.sort()
    unique_usernames = set(df.author_name.unique())

    dictionary_periods = dict()
    for username in unique_usernames:
        dictionary_periods[username] = 0

    os.remove(first_temporal_csv)
    second_temporal_csv = generate_random_file_name()
    f_temp_output = open(second_temporal_csv, 'w', encoding="utf-8")
    f_temp_output.write("profile_image_url,author_name")
    for unique_date in unique_dates:
        unique_date_str: str = str(unique_date).split('/')[0]
        f_temp_output.write(',' + str(unique_date_str).replace(' ', '_'))
    f_temp_output.write("\n")

    logging.info('Computing user scores')
    user_count: int = 1
    total_users: int = len(unique_usernames)
    for user in unique_usernames:
        period: int = 0
        f_temp_output.write(profile_image_dictionary[user])
        f_temp_output.write(","+user)
        df_filtered_user = df[df['author_name'] == user]
        for date_period in unique_dates:
            df_filtered = df_filtered_user[df_filtered_user['created_at'] == date_period]
            number_of_rts = len(df_filtered.index)
            score = compute_score(user, number_of_rts, alpha, dictionary_periods)
            f_temp_output.write("," + str(score))
            period = period + 1
        f_temp_output.write("\n")
        logging.info('{}/{}'.format(user_count, total_users))
        user_count = user_count + 1
    f_temp_output.close()

    logging.info('User scores computed. Matrix file generated:' + outfile)
    logging.info('Filtering users...')

    f_temp_input = open(second_temporal_csv, 'r', encoding="utf-8")
    f_output = open(outfile, 'w', encoding='utf-8')
    csv_file = csv.reader(f_temp_input)
    number_of_line = 0
    for line in csv_file:
        if number_of_line > 0:
            sum_score = sum([float(x) for x in line[3:]])
            if sum_score > threshold:
                line_to_write = ','.join(line)
                f_output.write(line_to_write+"\n")
        else:
            f_output.write(','.join(line)+"\n")
        number_of_line = number_of_line + 1

    f_temp_input.close()
    f_output.close()

    logging.info('Finished.')
    os.remove(second_temporal_csv)


if __name__ == '__main__':
    main()
