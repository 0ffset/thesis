'''
End-to-end models for neural audio synthesis.
'''
from ddsp.training.models import Autoencoder
from ddsp.losses import SpectralLoss

from .losses import MelSpectralLoss
from .preprocessors import F0Preprocessor, OscF0Preprocessor
from .decoders import F0RnnFcDecoder, MultiInputRnnFcDecoder
from .processors import HarmonicPlusNoise

class F0RnnFcHPNDecoder(Autoencoder):
    '''
    Full RNN-FC decoder harmonic-plus-noise synthesizer stack for decoding f0
    signals into audio.
    '''
    def __init__(self, window_secs=None,
                       audio_rate=None,
                       input_rate=None,
                       f0_denom=1.,
                       n_harmonic_distribution=60,
                       n_noise_magnitudes=65,
                       losses=None,
                       feature_domain="freq",
                       name="f0_rnn_fc_hps_decoder"):
        # Initialize preprocessor
        if window_secs * input_rate % 1.0 != 0.0:
            raise ValueError("window_secs and input_rate must result in an integer number of samples per window.")
        time_steps = int(window_secs * input_rate)
        preprocessor = F0Preprocessor(time_steps=time_steps,
                                      denom=f0_denom,
                                      rate=input_rate,
                                      feature_domain=feature_domain)

        # Initialize decoder
        decoder = F0RnnFcDecoder(rnn_channels=512,
                                 rnn_type="gru",
                                 ch=512,
                                 layers_per_stack=3,
                                 output_splits=(("amps", 1),
                                                ("harmonic_distribution", n_harmonic_distribution),
                                                ("noise_magnitudes", n_noise_magnitudes)))
        
        # Initialize processor group
        processor_group = HarmonicPlusNoise(window_secs=window_secs,
                                            audio_rate=audio_rate,
                                            input_rate=input_rate)
        
        # Initialize losses
        if losses is None:
            losses = [SpectralLoss(fft_sizes=(8192, 4096, 2048, 1024, 512, 256, 128),
                                   loss_type="L1",
                                   mag_weight=1.0,
                                   logmag_weight=1.0)]
        
        # Call parent constructor
        super(F0RnnFcHPNDecoder, self).__init__(preprocessor=preprocessor,
                                                encoder=None,
                                                decoder=decoder,
                                                processor_group=processor_group,
                                                losses=losses)

class OscF0RnnFcHPNDecoder(Autoencoder):
    '''
    Full RNN-FC decoder harmonic-plus-noise synthesizer stack for decoding f0
    and osc signals into audio.
    '''
    def __init__(self, window_secs=None,
                       audio_rate=None,
                       input_rate=None,
                       f0_denom=1.,
                       n_harmonic_distribution=60,
                       n_noise_magnitudes=65,
                       losses=None,
                       name="osc_f0_rnn_fc_hps_decoder"):
        # Initialize preprocessor
        if window_secs * input_rate % 1.0 != 0.0:
            raise ValueError("window_secs and input_rate must result in an integer number of samples per window.")
        time_steps = int(window_secs * input_rate)
        preprocessor = OscF0Preprocessor(time_steps=time_steps,
                                         denom=f0_denom,
                                         rate=input_rate)

        # Initialize decoder
        decoder = MultiInputRnnFcDecoder(rnn_channels=512,
                                         rnn_type="gru",
                                         ch=512,
                                         layers_per_stack=3,
                                         input_keys=["f0_sub_scaled", "osc_scaled"],
                                         output_splits=(("amps", 1),
                                                        ("harmonic_distribution", n_harmonic_distribution),
                                                        ("noise_magnitudes", n_noise_magnitudes)))
        
        # Initialize processor group
        processor_group = HarmonicPlusNoise(window_secs=window_secs,
                                            audio_rate=audio_rate,
                                            input_rate=input_rate)
        
        # Initialize losses
        if losses is None:
            losses = [SpectralLoss(fft_sizes=(8192, 4096, 2048, 1024, 512, 256, 128),
                                   loss_type="L1",
                                   mag_weight=1.0,
                                   logmag_weight=1.0)]
        
        # Call parent constructor
        super(OscF0RnnFcHPNDecoder, self).__init__(preprocessor=preprocessor,
                                                   encoder=None,
                                                   decoder=decoder,
                                                   processor_group=processor_group,
                                                   losses=losses)
