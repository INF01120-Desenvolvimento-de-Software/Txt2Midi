import pygame

from midi_engine.Exceptions import MidiLoadError


class MidiPlayer:
    paused = False

    @staticmethod
    def load_midi(file_path):
        try:
            pygame.mixer.music.load(file_path)
        except pygame.error as error:
            raise MidiLoadError(file_path) from error

    @classmethod
    def play_audio(cls):
        if cls.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()
        cls.paused = False

    @classmethod
    def pause_audio(cls):

        pygame.mixer.music.pause()
        cls.paused = True

    @classmethod
    def reset_audio(cls):
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        cls.paused = False

    @classmethod
    def stop_audio(cls):
        pygame.mixer.music.stop()
        cls.paused = False