from faster_whisper import WhisperModel
import io
import logging

from helpers import singleton

@singleton
class AudioTranscriber:
    def __init__(self, model_path="large-v3", device="cpu"):
        """
        Initialize the AudioTranscriber with the specified model configuration.
        
        Args:
            model_path (str): Path or size of the model to use
            device (str): Device to run the model on ('cuda' or 'cpu')
            compute_type (str): Computation type ('float16', 'int8_float16', or 'int8')
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        try:
            self.model = WhisperModel(
                model_path,
                device=device,
                compute_type="float16"
            )
            self.logger.info(f"Successfully loaded Whisper model: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(self, audio_data: io.BytesIO) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data (io.BytesIO): Audio data in BytesIO format
            
        Returns:
            str: Transcribed text
        """
        
        text = ""
        language = "tr"
        
        try:
            # Transcribe the audio
            segments, info = self.model.transcribe(audio_data, beam_size=5)
            
            # Log detection info
            self.logger.info(
                f"Detected language '{info.language}' with probability {info.language_probability}"
            )
            
            # Combine all segments into a single text
            text = " ".join(segment.text.strip() for segment in segments)
            language = info.language
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
        finally:
            return text.strip(), language

    def __call__(self, audio_data: io.BytesIO) -> str:
        """
        Allow the class to be called directly.
        
        Args:
            audio_data (io.BytesIO): Audio data to transcribe
            
        Returns:
            str: Transcribed text
        """
        return self.transcribe(audio_data)