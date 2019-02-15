from collections import defaultdict
import twitter
import json
import random

excluded_words = ['&amp;', 'rt', '']

class TwitterParser:

    def __init__(self):
        CONSUMER_KEY = 'OjXk0A4iZxQGmG72rcq7SL0sy'
        CONSUMER_KEY_SECRET = 'Uyl92kkj9shxgVGkC7WkYAoskGyAKUbh6r0l25Urqk3GvgcVDH'
        ACCESS_TOKEN = '1059950711696326656-weAUS5qNWvBKtBbsJbY9FsHQIII4hz'
        ACCESS_TOKEN_SECRET = 'cro346WIl4ASb5OqoHCNc1VGkL75fZQFUgLbGQxVPo4e2'

        self.api = twitter.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_KEY_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)


    def write_tweets_to_file(self, username, file):

        total_timeline = []
        count = 2000
        last_selected_id = -1

        # Loop from (1 - 9) * 200 to pull the last 200 tweets
        while count > 0:
            # If this is the first api call, don't use max_id to limit the range of the tweets pulled
            if last_selected_id == -1:
                timeline = self.api.GetUserTimeline(
                    screen_name=username, 
                    count=200, 
                    include_rts=False)
            else:
                timeline = self.api.GetUserTimeline(
                    screen_name=username, 
                    count=200, 
                    include_rts=False, 
                    max_id=(last_selected_id - 1))
                
            count -= len(timeline)

            if not timeline:
                break

            # Assign the last selected ID to be the ID of the oldest status
            last_selected_id = timeline[len(timeline) - 1].id
            # Add the timeline to the total timeline containing all 2000 tweets
            total_timeline.extend(timeline)

        if not total_timeline:
            return ''
        else:
            total_timeline = total_timeline[:2000]

        # Total Timeline now contains all Status objects from a timeline with a max-range of 2000
        all_text = ''

        # Replace all newline characters with a space and lower the case of the string to check for the existence of the keyword with no case sensitivity
        for status in total_timeline:
            all_text += status.text.replace('\n', ' ').lower() + ' '

        # Split on space and remove all empty strings within the list
        all_words = [word for word in all_text.split(' ') if word not in excluded_words]

        count = 0
        for word in all_words:
            count += 1
            # file.write(word + ' ' + ('\n' if count % 10 == 0 else ''))
            if 't.co' not in word:
                file.write(word + ' ')

        file.close()


class Markov:

    def __init__(self):
        self._markov_dict = {}


    def add_word_tuple(self, word, following):
        if word not in self._markov_dict:
            self._markov_dict[word] = defaultdict(int)
        self._markov_dict[word][following] += 1


    def _get_word_counts_dict(self, word):
        return dict(self._markov_dict[word]) if word in self._markov_dict else {}


    def get_markov_chain(self, word):
        if word in self._markov_dict:
            word_counts_dict = self._get_word_counts_dict(word)
            
            if word_counts_dict:
                total_n = sum(word_count for word_count in word_counts_dict.values())
                return dict([(word, word_count / total_n) for word, word_count in word_counts_dict.items()])
            else:
                return {}
        else:
            return {}


    def generate_markov_chain_file(self, file):
        for line in file:
            word_data = line.split(' ')
            line_length = len(word_data)
            for index, word in enumerate(word_data):
                if index + 1 < line_length:
                    self.add_word_tuple(word, word_data[index + 1])


    def _get_random_word(self):
        # print(self._markov_dict.keys())
        return random.choice([key for key in self._markov_dict.keys()])


    def generate_sentence(self, length):
        random_word = self._get_random_word()
        sentence = random_word

        curr = random_word
        for i in range(length):
            if curr in self._markov_dict:
                next_word = random.choice([word for word, length in self._markov_dict[curr].items() for i in range(length)])
            else:
                next_word = self._get_random_word()
            sentence += ' ' + str(next_word)
            curr = next_word
        return sentence


    def __str__(self):
        return str(dict([(key, dict(value)) for key, value in self._markov_dict.items()]))


if __name__ == '__main__':
    test = TwitterParser()
    username = 'ElonMusk'
    filename = username + '.txt'
    test.write_tweets_to_file(username, open(filename, 'w'))

    markov = Markov()
    markov.generate_markov_chain_file(open(filename, 'r'))

    for i in range(100):
        print(markov.generate_sentence(25) + '\n\n')