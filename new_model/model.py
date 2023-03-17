import const as c
import numpy as np
from tensorflow.keras import Input
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Model


def load_npy(path):
    with open(path, 'rb') as f:
        data = np.load(f)
    return data


# generate target given source sequence
def predict_sequence(infenc, infdec, source, n_steps, cardinality):
    # encode
    state = infenc.predict(source)
    # start of sequence input
    target_seq = np.array([0.0 for _ in range(cardinality)]).reshape(1, 1, cardinality)
    # collect predictions
    output = list()
    for t in range(n_steps):
        # predict next char
        yhat, h, c = infdec.predict([target_seq] + state)
        # store prediction
        output.append(yhat[0, 0, :])
        # update state
        state = [h, c]
        # update target sequence
        target_seq = yhat
    return np.array(output)


train_encoder_input = load_npy(c.ENCODER_INPUT_TRAIN_PATH)
train_decoder_input = load_npy(c.DECODER_INPUT_TRAIN_PATH)
train_decoder_output = load_npy(c.DECODER_OUTPUT_TRAIN_PATH)

# val_encoder_input = load_npy(c.ENCODER_INPUT_VAL_PATH)
# val_decoder_input = load_npy(c.DECODER_INPUT_VAL_PATH)
# val_decoder_output = load_npy(c.DECODER_OUTPUT_VAL_PATH)

test_encoder_input = load_npy(c.ENCODER_INPUT_TEST_PATH)
test_decoder_input = load_npy(c.DECODER_INPUT_TEST_PATH)
test_decoder_output = load_npy(c.DECODER_OUTPUT_TEST_PATH)

encoder_inputs_shape = (train_encoder_input.shape[1], train_encoder_input.shape[2])
decoder_inputs_shape = ((train_decoder_input.shape[1]), train_decoder_input.shape[2])

# define training encoder
encoder_inputs = Input(shape=encoder_inputs_shape)
encoder = LSTM(c.UNITS, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_inputs)
encoder_states = [state_h, state_c]

# define training decoder
decoder_inputs = Input(shape=decoder_inputs_shape)
decoder_lstm = LSTM(c.UNITS, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
decoder_dense = Dense(c.MAX_CHAR_LEN, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
model.fit(
    [train_encoder_input, train_decoder_input],
    train_decoder_output,
    epochs=c.EPOCH,
    validation_split=0.2
)

# inferance
# define inference encoder
encoder_model = Model(encoder_inputs, encoder_states)

# define inference decoder
decoder_state_input_h = Input(shape=(c.UNITS,))
decoder_state_input_c = Input(shape=(c.UNITS,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_outputs, state_h, state_c = decoder_lstm(
    decoder_inputs,
    initial_state=decoder_states_inputs
)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model([decoder_inputs] + decoder_states_inputs,
                      [decoder_outputs] + decoder_states)

