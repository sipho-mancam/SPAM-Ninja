from .data_cleaning import *


class NBClassifier:
    def __init__(self, train_data,**kwargs)->None:
        self.train_data = train_data
        self.p_spam = self.train_data['Label'].value_counts()['spam'] / self.train_data.shape[0]
        self.p_ham = self.train_data['Label'].value_counts()[
            'ham'] / self.train_data.shape[0]
        self.num_spam = self.train_data.loc[self.train_data['Label'] == 'spam',
                                       'SMS'].apply(len).sum()

        self.num_ham = self.train_data.loc[self.train_data['Label'] == 'ham',
                                      'SMS'].apply(len).sum()
        self.num_voc = len(self.train_data.columns) - 3
        self.alpha = 1

    def __p_w_spam(self, word)->float:
        if word in self.train_data.columns:
            return (self.train_data.loc[self.train_data['Label'] == 'spam', word].sum() + self.alpha) /\
                    (self.num_spam + self.alpha*self.num_voc)
        else:
            return 1

    def __p_w_ham(self, word)->float:
        if word in self.train_data.columns:
            return (self.train_data.loc[self.train_data['Label'] == 'ham', word].sum() + self.alpha) /\
                 (self.num_ham + self.alpha*self.num_voc)
        else:
            return 1
        
    
    def classify(self, message)->bool:
        p_spam_given_message = self.p_spam
        p_ham_given_message = self.p_ham
        for word in message:
            p_spam_given_message *= self.__p_w_spam(word)
            p_ham_given_message *= self.__p_w_ham(word)
        if p_ham_given_message > p_spam_given_message:
            return False
        elif p_ham_given_message <= p_spam_given_message:
            return True
    
nb_classifier = NBClassifier(train_data)