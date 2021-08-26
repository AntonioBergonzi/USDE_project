import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import Model, load_model
from transformers import AutoTokenizer, pipeline, TFDistilBertModel
from transformers import TFAutoModelForSequenceClassification
import logging
from util import progress_bar

logging.getLogger("tensorflow").setLevel(logging.CRITICAL)
logging.getLogger("keras").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)

class Classifier:
    """
    Class to allow the classification of tweets, it uses a pre-trained model trained on italian words, so to make predictions in english another class similar to this should be created .
    The model is fine-tuned from Bert using italian tweets about football, and since in Italy the difference between football and politics is quite small so we ought to be all right, especially since the objective of the project is not to train a Neural Network.
    """ 
    def __init__(self):
        #download and instantiate the model
        self._model = TFAutoModelForSequenceClassification.from_pretrained("neuraly/bert-base-italian-cased-sentiment") 
        self._tokenizer = AutoTokenizer.from_pretrained("neuraly/bert-base-italian-cased-sentiment")

        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
        optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5,epsilon=1e-08)
        self._model.compile(loss=loss,optimizer=optimizer,metrics=[metric]) 

    def predict(self, tweet_list):
        """
        Expects a list of strings that are the tweet to predict, it's suggested to pre-process the tweets removing mentions, urls and emails.
        Returns a list of integers in which -1 is negative feeling, 0 neutral and 1 is positive
        """
        input_ids = []
        attention_masks = []
        for tweet in tweet_list:
            model_input=self._tokenizer.encode_plus(tweet,add_special_tokens = True,
            max_length =64,pad_to_max_length = True, return_attention_mask = True)
            input_ids.append(model_input['input_ids'])
            attention_masks.append(model_input['attention_mask'])
        input_ids=np.asarray(input_ids)
        attention_masks=np.array(attention_masks)

        predictions = self._model.predict([input_ids, attention_masks])
        predictions = np.argmax(predictions[0], axis=1)
        return list(map(lambda x: x-1, predictions)) #the model returns numbers in ranges (-1, 0, 1)
    
    def predict_batch(self, tweet_list, batch = 10):
        assert len(tweet_list) > 0 and batch > 1
        if len(tweet_list) <= batch:
            return self.predict(self, tweet_list)
        batches = []
        result = []
        last_element = 0
        for i in range(1, len(tweet_list)):
            if i % batch == 0:
                #print("i: {}, batch: {}".format(i, batch)) TODO: remove
                batches.append(tweet_list[i-batch :i])
                last_element = i
        if last_element != len(tweet_list):
            batches.append(tweet_list[last_element:])
        for elem in progress_bar(batches, prefix="Progress", suffix="Complete"):
            result.extend(self.predict(elem))
        return result
            
            
    def analyse_dict(self, tweet_dict):
        tweet_ids = tweet_dict.keys()
        tweet_to_evaluate = []
        for tweet_id in tweet_ids:
            tweet_to_evaluate.append(tweet_dict[tweet_id])
        results = self.predict_batch(tweet_to_evaluate)
        evaluated_dict = {}
        for tweet_id, prediction in zip(tweet_ids, results):
            evaluated_dict[tweet_id] = prediction
        return evaluated_dict











