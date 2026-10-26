import pygame

from midi_engine.Exceptions import MidiLoadError


class MidiPlayer:
    paused = False

    @classmethod
    def load_midi(cls, file_path):
        try:
            pygame.mixer.music.load(file_path)
            cls.paused = False
        except pygame.error as error:
            raise MidiLoadError(file_path) from error

    @classmethod
    def play_audio(cls):
        try:
            if cls.paused:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play()
            cls.paused = False
        except pygame.error:
            pass

    @classmethod
    def pause_audio(cls):
        try:
            pygame.mixer.music.pause()
            cls.paused = True
        except pygame.error:
            pass

    @classmethod
    def reset_audio(cls):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
            cls.paused = False
        except pygame.error:
            pass

    @classmethod
    def stop_audio(cls):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            cls.paused = False
        except pygame.error:
            pass
