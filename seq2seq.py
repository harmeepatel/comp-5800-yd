import const as c
import io
import re
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow_addons as tfa
import unicodedata


DEV = True

if DEV:
    DATA_PATH = c.T_DATA
else:
    DATA_PATH = c.DATA


def pe(line):
    print(line)
    exit()


class NMTDataset:
    def __init__(self, data_path):
        self.data_path = data_path
        self.input_lang_tokenizer = None
        self.target_lang_tokenizer = None

    def unicode_to_ascii(self, s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'
        )

    def preprocess_sentence(self, w):
        w = self.unicode_to_ascii(w.lower().strip())

        w = re.sub(r"([?.!,¿])", r" \1 ", w)
        w = re.sub(r'[" "]+', " ", w)

        w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)

        w = w.strip()

        w = f"{c.BOS} " + w + f" {c.EOS}"
        return w

    def create_dataset(self, path, num_examples):
        lines = io.open(path, encoding='UTF-8').read().strip().split('\n')
        word_pairs = [
            [
                self.preprocess_sentence(word) for word in line.split('\t')
            ]
            for line in lines[:num_examples]
        ]

        return zip(*word_pairs)

    # Step 3 and Step 4
    def tokenize(self, lang):
        lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='', oov_token=c.OOV)
        lang_tokenizer.fit_on_texts(lang)

        tensor = lang_tokenizer.texts_to_sequences(lang)

        tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, padding='post')

        return tensor, lang_tokenizer

    def load_dataset(self, path, num_examples=None):
        targ_lang, inp_lang = self.create_dataset(path, num_examples)

        input_tensor, inp_lang_tokenizer = self.tokenize(inp_lang)
        target_tensor, targ_lang_tokenizer = self.tokenize(targ_lang)

        return input_tensor, target_tensor, inp_lang_tokenizer, targ_lang_tokenizer

    def call(self, num_examples, BUFFER_SIZE, BATCH_SIZE):
        file_path = self.data_path
        input_tensor, target_tensor, self.input_lang_tokenizer, self.target_lang_tokenizer = self.load_dataset(
            file_path, num_examples)

        input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(
            input_tensor, target_tensor, test_size=0.2)

        train_dataset = tf.data.Dataset.from_tensor_slices(
            (input_tensor_train, target_tensor_train))
        train_dataset = train_dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

        val_dataset = tf.data.Dataset.from_tensor_slices((input_tensor_val, target_tensor_val))
        val_dataset = val_dataset.batch(BATCH_SIZE, drop_remainder=True)

        return train_dataset, val_dataset, self.input_lang_tokenizer, self.target_lang_tokenizer


#####


class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, enc_units, batch_sz):
        super(Encoder, self).__init__()
        self.batch_sz = batch_sz
        self.enc_units = enc_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)

        # -------- LSTM layer in Encoder ------- #
        self.lstm_layer = tf.keras.layers.LSTM(self.enc_units,
                                               return_sequences=True,
                                               return_state=True,
                                               recurrent_initializer='glorot_uniform')

    def call(self, x, hidden):
        x = self.embedding(x)
        output, h, c = self.lstm_layer(x, initial_state=hidden)
        return output, h, c

    def initialize_hidden_state(self):
        return [tf.zeros((self.batch_sz, self.enc_units)), tf.zeros((self.batch_sz, self.enc_units))]


class Decoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, dec_units, batch_sz, attention_type='luong'):
        super(Decoder, self).__init__()
        self.batch_sz = batch_sz
        self.dec_units = dec_units
        self.attention_type = attention_type

        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)

        self.fc = tf.keras.layers.Dense(vocab_size)

        self.decoder_rnn_cell = tf.keras.layers.LSTMCell(self.dec_units)

        self.sampler = tfa.seq2seq.sampler.TrainingSampler()

        self.attention_mechanism = self.build_attention_mechanism(self.dec_units,
                                                                  None,
                                                                  self.batch_sz * [max_length_input],
                                                                  self.attention_type)

        self.rnn_cell = self.build_rnn_cell(batch_sz)

        self.decoder = tfa.seq2seq.BasicDecoder(self.rnn_cell, sampler=self.sampler, output_layer=self.fc)

    def build_rnn_cell(self, batch_sz):
        rnn_cell = tfa.seq2seq.AttentionWrapper(self.decoder_rnn_cell,
                                                self.attention_mechanism, attention_layer_size=self.dec_units)
        return rnn_cell

    def build_attention_mechanism(self, dec_units, memory, memory_sequence_length, attention_type='luong'):
        if (attention_type == 'bahdanau'):
            return tfa.seq2seq.BahdanauAttention(units=dec_units, memory=memory, memory_sequence_length=memory_sequence_length)
        else:
            return tfa.seq2seq.LuongAttention(units=dec_units, memory=memory, memory_sequence_length=memory_sequence_length)

    def build_initial_state(self, batch_sz, encoder_state, Dtype):
        decoder_initial_state = self.rnn_cell.get_initial_state(batch_size=batch_sz, dtype=Dtype)
        decoder_initial_state = decoder_initial_state.clone(cell_state=encoder_state)
        return decoder_initial_state

    def call(self, inputs, initial_state):
        x = self.embedding(inputs)
        outputs, _, _ = self.decoder(x, initial_state=initial_state, sequence_length=self.batch_sz * [max_length_output - 1])
        return outputs


optimizer = tf.keras.optimizers.Adam()


def loss_function(real, pred):
    cross_entropy = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction='none')
    loss = cross_entropy(y_true=real, y_pred=pred)
    mask = tf.logical_not(tf.math.equal(real, 0))
    mask = tf.cast(mask, dtype=loss.dtype)
    loss = mask * loss
    loss = tf.reduce_mean(loss)
    return loss


if __name__ == "__main__":

    dataset_creator = NMTDataset(DATA_PATH)
    train_dataset, val_dataset, input_lang, target_lang = dataset_creator.call(c.NUM_EXAMPLES, c.BUFFER_SIZE, c.BATCH_SIZE)

    input_batch, target_batch = next(iter(train_dataset))

    vocab_inp_size = len(input_lang.word_index) + 1
    vocab_tar_size = len(target_lang.word_index) + 1
    max_length_input = input_batch.shape[1]
    max_length_output = target_batch.shape[1]

    embedding_dim = 256
    units = 1024
    steps_per_epoch = c.NUM_EXAMPLES
    # Test Encoder Stack

    encoder = Encoder(vocab_inp_size, embedding_dim, units, c.BATCH_SIZE)

    # sample input
    sample_hidden = encoder.initialize_hidden_state()
    sample_output, sample_h, sample_c = encoder(input_batch, sample_hidden)
    print('Encoder output shape: (batch size, sequence length, units) {}'.format(sample_output.shape))
    print('Encoder h vecotr shape: (batch size, units) {}'.format(sample_h.shape))
    print('Encoder c vector shape: (batch size, units) {}'.format(sample_c.shape))

    # Test decoder stack

    decoder = Decoder(vocab_tar_size, embedding_dim, units, c.BATCH_SIZE, 'bahdanau')
    sample_x = tf.random.uniform((c.BATCH_SIZE, max_length_output))
    decoder.attention_mechanism.setup_memory(sample_output)
    initial_state = decoder.build_initial_state(c.BATCH_SIZE, [sample_h, sample_c], tf.float32)

    sample_decoder_outputs = decoder(sample_x, initial_state)

    print("Decoder Outputs Shape: ", sample_decoder_outputs.rnn_output.shape)
