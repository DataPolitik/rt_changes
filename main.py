import json
import click
from io import TextIOWrapper
from twarc import ensure_flattened
import pandas as pd

@click.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
def twarc_filter(infile: TextIOWrapper,
                 outfile: TextIOWrapper):

    f_output = open('output.csv', 'w')
    f_output.write("created_at,author_name,author_profile\n")

    for line in infile:
        for tweet in ensure_flattened(json.loads(line)):
            if 'referenced_tweets' in tweet:
                for x in tweet['referenced_tweets']:
                    if 'retweeted' in x['type']:
                        author_name = x['author']['name']
                        author_profile = x['author']['profile_image_url']
                        created_at = tweet['created_at']
                        f_output.write("{},{},{}\n".format(created_at, author_name, author_profile))
    f_output.close()




if __name__ == '__main__':
    twarc_filter()
