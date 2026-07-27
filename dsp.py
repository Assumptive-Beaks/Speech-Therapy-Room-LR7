import pygame
import numpy as np
from config import Config

class SoundGenerator:
    def __init__(self, fs=44100, dots=None):
        self.fs = fs
        self.base_volume = 1.8
        self.master_volume = Config.DEFAULT_VOLUME
        self.dots = dots if dots is not None else [] 
        self.RADIUS = Config.RADIUS 
        
        try:
            pygame.mixer.init(frequency=fs, size=-16, channels=2, buffer=512)
        except pygame.error:
            pass 
        
        # 音響設定の定義
        self.FIXED_SOUND_PARAMS = {
            (0, 1): {'decay_rate': 12, 'f_low': 500, 'f_high': 3000, 'am_depth': 0.4},  # 2拍目
            (0, 3): {'decay_rate': 8, 'f_low': 2000, 'f_high': 6000, 'am_depth': 0.5},   # 3拍目
            (0, 4): {'decay_rate': 5, 'f_low': 100, 'f_high': 800, 'am_depth': 0.3},    # 4拍目
            (0, 2): {'decay_rate': 6, 'f_low': 50, 'f_high': 400, 'am_depth': 0.6},     # 1拍目 
            (1, 3): {'f0': 500, 'am_rate': 8, 'am_depth': 0.1},             
            (3, 4): {'f0': 2200, 'jitter': 0.25, 'am_depth': 0.2},
        }
        
        self.line_sound_map = {
            (0, 1): self.drum_hit,
            (0, 3): self.drum_hit,
            (0, 4): self.drum_hit,
            (0, 2): self.drum_hit,
            (1, 3): self.fluid_vortex,
            (3, 4): self.bubble_pop,
        }

    # --- 高速フィルタリングエンジン (FFTベース) ---
    def _apply_fft_filter(self, signal, low=None, high=None):
        """
        forループを使わず、FFTで帯域をカットする。
        low: ハイパスの境界 (Hz)
        high: ローパスの境界 (Hz)
        """
        n = len(signal)
        if n == 0: return signal
        
        freqs = np.fft.fftfreq(n, d=1/self.fs)
        spec = np.fft.fft(signal)
        
        # ローパス処理
        if high is not None:
            spec[np.abs(freqs) > high] = 0
        # ハイパス処理
        if low is not None:
            spec[np.abs(freqs) < low] = 0
            
        return np.fft.ifft(spec).real

    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))
        
    # --- 各音響生成関数 ---
    def drum_hit(self, dur=0.25, f_low=500, f_high=10000, decay_rate=15):
        """FFTフィルタにより劇的にキレを増したドラム音"""
        t = np.linspace(0, dur, int(self.fs*dur), endpoint=False)
        noise = np.random.randn(len(t))
        
        filtered_noise = self._apply_fft_filter(noise, low=f_low, high=f_high)
        
        decay = np.exp(-t * decay_rate)
        return filtered_noise * decay

    def bubble_pop(self, f0=2200, jitter=0.25, dur=0.25):
        t = np.linspace(0, dur, int(self.fs*dur), endpoint=False)
        decay = np.exp(-t*8)
        freq = f0 * (1 + jitter*np.sin(2*np.pi*8*t)) 
        return decay * np.sin(2*np.pi*freq*t)

    def fluid_vortex(self, f0=120, am_rate=8, am_depth=0.85, dur=0.6):
        t = np.linspace(0, dur, int(self.fs*dur), endpoint=False)
    
        fm_depth = 0.02 
        fm_rate = am_rate * 0.7
    
        inst_freq = f0 + (f0 * fm_depth) * np.sin(2 * np.pi * fm_rate * t)
        phase = 2 * np.pi * np.cumsum(inst_freq) / self.fs
        carrier = np.sin(phase)
    
        am = (1.0 - am_depth) + am_depth * (0.5 * (1 + np.sin(2 * np.pi * am_rate * t)))
    
        return carrier * am
    
    def am_noise_carrier(self, low=None, high=None, dur=1.0):
        """フラグに応じてローパス・ハイパス・バンドパスが劇的に変わるノイズ"""
        t = np.linspace(0, dur, int(self.fs*dur), endpoint=False)
        n = np.random.randn(len(t))
        
        filtered_noise = self._apply_fft_filter(n, low=low, high=high)
        
        if np.max(np.abs(filtered_noise)) > 0:
            filtered_noise /= (np.max(np.abs(filtered_noise)) + 1e-9)
        
        mod = 0.5 * (1 + np.sin(2*np.pi*2*t))
        return filtered_noise * mod

    def distortion(self, wave, threshold=0.1, max_iter=4):
        if len(wave) == 0: return wave
        pre_wave = wave.copy()
        pre_wave[1:] = wave[1:] - 0.5 * wave[:-1] 
        boosted = pre_wave * 2.5 
        folded = boosted.copy()
        for _ in range(max_iter):
            folded = np.where(folded > threshold, 2*threshold - folded, folded)
            folded = np.where(folded < -threshold, -2*threshold - folded, folded)
        return folded
    
    def generate_sound(self, path_indices, path_points, duration_base=0.9):
        BPM = 120
        beat_duration = 60.0 / BPM 
        duration = 4 * beat_duration
        
        DELAY_OFFSET = beat_duration / 4
        delay_samples = int(self.fs * DELAY_OFFSET)

        if not self.dots or not path_indices or len(path_points) < 2:
            return self._create_sound_from_wave(np.zeros(int(self.fs * duration)))
            
        mix = np.zeros(int(self.fs*duration))
        
        # フラグ管理
        distortion_flag = False
        highpass_flag = False
        lowpass_flag = False
        play_bubble_pop = False 
        
        # ノルム計算
        i1_start, i2_end = path_indices[0], path_indices[-1]
        (x_start, y_start), (x_end, y_end) = path_points[0], path_points[-1]
        Norm_X, Norm_Y = 0.5, 0.5
        
        if i1_start < len(self.dots) and i2_end < len(self.dots):
            (cx1, cy1), (cx2, cy2) = self.dots[i1_start], self.dots[i2_end]
            X_total_diff = abs(x_start - cx1) + abs(x_end - cx2)
            Y_total_diff = abs(y_start - cy1) + abs(y_end - cy2)
            MAX_DIFF_BASE = self.RADIUS * 2.0 
            Norm_X = max(0.0, min(1.0, X_total_diff / MAX_DIFF_BASE))
            Norm_Y = max(0.0, min(1.0, Y_total_diff / MAX_DIFF_BASE))
            
        # 経路の解析
        for i in range(len(path_indices) - 1):
            line = tuple(sorted((path_indices[i], path_indices[i+1])))
            
            # 特殊ラインによるフラグ付与
            if line == (1, 2): highpass_flag = True
            elif line == (2, 4): lowpass_flag = True
            elif line == (0, 0): distortion_flag = True # 自己結合があれば
            elif line == (3, 4): play_bubble_pop = True

            # メインの音響生成
            if line in self.line_sound_map and line != (3, 4) and line != (0, 2):
                params = self.FIXED_SOUND_PARAMS[line].copy()
                
                if self.line_sound_map[line] == self.drum_hit:
                    # ドラムの動的パラメータ
                    f_l = max(20, params['f_low'] * (1 - 0.5 * Norm_Y))
                    f_h = min(20000, params['f_high'] * (1 + 0.5 * Norm_X))
                    sound = self.drum_hit(dur=beat_duration, f_low=f_l, f_high=f_h, decay_rate=params['decay_rate'])
                    start_offset = { (0, 1): 1, (0, 3): 2, (0, 4): 3 }.get(line, 0) * beat_duration
                
                elif line == (1, 3): # fluid_vortex
                    f0 = 400 + 1600 * Norm_Y
                    am_r = 1 + 29 * Norm_X
                    am_d = 0.01 + 0.99 * Norm_X
                    sound_raw = self.fluid_vortex(f0=f0, am_rate=am_r, am_depth=am_d, dur=duration - DELAY_OFFSET)
                    sound = np.pad(sound_raw, (delay_samples, 0))[:len(mix)]
                    start_offset = 0

                # ミックス
                start_sample = int(self.fs * start_offset)
                if start_sample + len(sound) <= len(mix):
                    peak = np.max(np.abs(sound))
                    if peak > 0: sound = (sound / peak) * params.get('am_depth', 1.0)
                    mix[start_sample:start_sample + len(sound)] += sound

        # --- 1拍目ドラム (0, 2) の自動補完 ---
        if not any(tuple(sorted((path_indices[i], path_indices[i+1]))) == (0, 2) for i in range(len(path_indices)-1)):
            p = self.FIXED_SOUND_PARAMS[(0, 2)]
            s = self.drum_hit(dur=beat_duration, f_low=p['f_low']*(1-0.5*Norm_Y), f_high=p['f_high']*(1+0.5*Norm_X), decay_rate=p['decay_rate'])
            mix[:len(s)] += (s / np.max(np.abs(s))) * p['am_depth']

        # --- bubble_pop 処理 ---
        if play_bubble_pop:
            p = self.FIXED_SOUND_PARAMS[(3, 4)]
            s_raw = self.bubble_pop(f0=500+4000*Norm_Y, jitter=0.01+0.79*Norm_X, dur=beat_duration-DELAY_OFFSET)
            s = np.pad(s_raw, (delay_samples, 0))[:int(self.fs*beat_duration)]
            start_idx = int(self.fs * beat_duration)
            mix[start_idx:start_idx+len(s)] += (s / np.max(np.abs(s))) * p['am_depth']

        # --- 【重要】am_noise_carrier フィルタリング変化 ---
        if lowpass_flag or highpass_flag:
            l_cutoff = None 
            h_cutoff = None
            
            if lowpass_flag and highpass_flag:
                l_cutoff = 500
                h_cutoff = 4000
            elif lowpass_flag:
                h_cutoff = 1200 
            elif highpass_flag:
                l_cutoff = 2500 
            
            s_raw = self.am_noise_carrier(low=l_cutoff, high=h_cutoff, dur=2*beat_duration - DELAY_OFFSET)
            s = np.pad(s_raw, (delay_samples, 0))[:int(self.fs*2*beat_duration)]
            start_idx = int(self.fs * beat_duration) # 2拍目から
            if start_idx + len(s) <= len(mix):
                mix[start_idx:start_idx+len(s)] += s * 0.25

        # 最終エフェクトとノーマライズ
        if distortion_flag: mix = self.distortion(mix)
        
        mix = np.clip(mix, -0.95, 0.95)
        final_wave = mix * self.base_volume * self.master_volume
        return self._create_sound_from_wave(final_wave)

    def _create_sound_from_wave(self, wave):
        audio_int16 = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio_int16, audio_int16))
        return pygame.sndarray.make_sound(stereo)

    def get_ecg_heartbeat(self, f0=1000, dur=0.1):
        t = np.linspace(0, dur, int(self.fs * dur), endpoint=False)
        wave = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 40) * self.master_volume * 0.2
        return self._create_sound_from_wave(wave)

    def get_ecg_flatline(self, f0=1000, dur=2.0):
        num_samples = int(self.fs * dur)
        actual_f0 = np.round(num_samples * f0 / self.fs) * self.fs / num_samples
        t = np.linspace(0, dur, num_samples, endpoint=False)
        wave = np.sin(2 * np.pi * actual_f0 * t) * self.master_volume * 0.3
        return self._create_sound_from_wave(wave)