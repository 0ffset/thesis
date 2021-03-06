'''
Factory classes for training data.
Inspired by https://github.com/magenta/ddsp/blob/master/ddsp/training/data.py
'''
import os
import pickle
import tensorflow as tf

class DataProvider:
    AUTOTUNE = tf.data.experimental.AUTOTUNE
    SHUFFLE_BUFFER_SIZE = 1000
    
    '''Base class for reading training data.'''
    def __init__(self, data_dir=None):
        if data_dir is None:
            raise ValueError("Path to .tfrecord file cannot be None.")
        metadata_path = os.path.join(data_dir, "metadata.pickle")
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        self.metadata = metadata
        self.data_dir = data_dir
        self.audio_rate = metadata["audio_rate"]
        self.input_rate = metadata["input_rate"]
        self.input_keys = metadata.get("input_keys", ["f0"])
        self.n_samples = metadata["n_samples"]
        self.n_samples_train = metadata.get("n_samples_train", None)
        self.n_samples_valid = metadata.get("n_samples_valid", None)
        self.n_samples_test = metadata.get("n_samples_test", None)
        self.example_secs = metadata["example_secs"]
        self.hop_secs = metadata["hop_secs"]
        self.audio_length = self.example_secs * self.audio_rate
        self.input_length = self.example_secs * self.input_rate

    def get_dataset(self, shuffle):
        raise NotImplementedError

    def get_batch(self, batch_size, shuffle=True, repeats=-1):
        '''Get a dataset with batches of data.'''
        dataset = self.get_dataset(shuffle)
        dataset = dataset.repeat(repeats)
        dataset = dataset.batch(batch_size, drop_remainder=True)
        dataset = dataset.prefetch(buffer_size=self.AUTOTUNE)
        return dataset
    
    def get_single_batch(self, batch_size=1, batch_number=1):
        '''Get a single batch from the dataset.'''
        dataset = self.get_batch(batch_size, shuffle=False)
        data_iter = iter(dataset)
        for _ in range(batch_number):
            batch = next(data_iter)
        return batch

class TFRecordProvider(DataProvider):
    '''Class for handling data stored in TFRecords.'''
    def __init__(self, data_dir=None, split="all"):
        '''TFRecordProvider constructor.'''
        super(TFRecordProvider, self).__init__(data_dir)
        if split not in ["all", "train", "valid", "test"]:
            raise ValueError("split must be either all, train, valid or test.")
        if split == "all":
            file_name = "*.tfrecord"
        else:
            file_name = "*%s.tfrecord" % split
        self.split = split
        self.file_pattern = os.path.join(self.data_dir, file_name)
    
    def get_dataset(self, shuffle=True):
        '''Read dataset from files.'''
        def parse_tfexample(record):
            '''Parse a single data example into to a dictionary structure according to self.features_dict'''
            return tf.io.parse_single_example(record, self.features_dict)
        
        tfrecords = tf.data.Dataset.list_files(self.file_pattern, shuffle=shuffle)
        dataset = tfrecords.interleave(map_func=tf.data.TFRecordDataset,
                                       cycle_length=40,
                                       num_parallel_calls=self.AUTOTUNE)
        dataset = dataset.map(parse_tfexample, num_parallel_calls=self.AUTOTUNE)
        if shuffle:
            dataset = dataset.shuffle(self.SHUFFLE_BUFFER_SIZE, reshuffle_each_iteration=True)
        return dataset

    @property
    def features_dict(self):
        '''Dictionary of features to read from dataset.'''
        features = {"audio": tf.io.FixedLenFeature([self.audio_length], dtype=tf.float32)}
        for key in self.input_keys:
            features[key] = tf.io.FixedLenFeature([self.input_length], dtype=tf.float32)
        return features
