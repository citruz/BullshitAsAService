from __future__ import absolute_import, division, print_function

import os
from six.moves import urllib

import tflearn
from tflearn.data_utils import *

path = "inputv1.txt"

maxlen = 25

X, Y, char_idx = textfile_to_semi_redundant_sequences(path, seq_maxlen=maxlen, redun_step=3)

g = tflearn.input_data([None, maxlen, len(char_idx)])
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 512)
g = tflearn.dropout(g, 0.5)
g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                       learning_rate=0.001)

m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                              seq_maxlen=maxlen,
                              clip_gradients=5.0,
                              checkpoint_path='model_chdddeckpoints')
m.load('model.tflearn')

for i in range(0,1, 0.1):
    seed = random_sequence_from_textfile(path, maxlen)
    print("-- TESTING...")
    print("-- Test with temperature of", i, "--")
    print(m.generate(600, temperature=i, seq_seed=seed))

