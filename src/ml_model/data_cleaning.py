import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__+'../../').resolve().as_posix()

sms_data = pd.read_table(BASE_DIR+'/SMSSpamCollection', sep='\t', names=['Label', 'SMS'])

sms_data['SMS'] = sms_data['SMS'].str.replace('\W', ' ').str.replace('\s+', ' ').str.strip()
sms_data['SMS'] = sms_data['SMS'].str.lower()
sms_data['SMS'] = sms_data['SMS'].str.split()

train_data = sms_data.sample(frac=0.8, random_state=1).reset_index(drop=True)
test_data = sms_data.drop(train_data.index).reset_index(drop=True)
train_data = train_data.reset_index(drop=True)


vocabulary = list(set(train_data['SMS'].sum()))

word_counts_per_sms = pd.DataFrame([
    [row[1].count(word) for word in vocabulary] 
    for _ , row in train_data.iterrows()], columns=vocabulary)

train_data = pd.concat([train_data.reset_index(), word_counts_per_sms], axis=1).iloc[:,1:]

