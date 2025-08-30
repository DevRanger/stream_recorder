#!/usr/bin/env python3
"""
VAD Auto-Tuner: Statistical Analysis and Automatic Parameter Adjustment
Analyzes channel performance and automatically adjusts VAD parameters for optimal voice detection.
"""

import json
import numpy as np
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class ChannelMetrics:
    """Container for channel audio analysis metrics"""
    timestamp: float
    energy_level: float
    zcr: float
    spectral_centroid: float
    was_recorded: bool
    recording_duration_ms: int
    noise_floor_estimate: float
    speech_probability: float

@dataclass
class AutoAdjustConfig:
    """Configuration for auto-adjustment per channel"""
    enabled: bool
    analysis_window_hours: int
    adjustment_frequency_hours: int
    min_samples_required: int
    sensitivity_factor: float

class VadMetricsCollector:
    """Collects and stores audio metrics for analysis"""
    
    def __init__(self, db_path: str = "vad_metrics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                timestamp REAL NOT NULL,
                energy_level REAL NOT NULL,
                zcr REAL NOT NULL,
                spectral_centroid REAL NOT NULL,
                was_recorded BOOLEAN NOT NULL,
                recording_duration_ms INTEGER,
                noise_floor_estimate REAL,
                speech_probability REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_channel_timestamp 
            ON channel_metrics(channel_name, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def collect_metrics(self, channel_name: str, audio_chunk: np.ndarray, 
                       sample_rate: int, was_recorded: bool, 
                       recording_duration_ms: int = 0):
        """Collect metrics from an audio chunk"""
        
        # Calculate audio characteristics
        energy_level = np.mean(audio_chunk ** 2)
        zcr = self._calculate_zcr(audio_chunk)
        spectral_centroid = self._calculate_spectral_centroid(audio_chunk, sample_rate)
        noise_floor = self._estimate_noise_floor(audio_chunk)
        speech_prob = self._estimate_speech_probability(audio_chunk, sample_rate)
        
        metrics = ChannelMetrics(
            timestamp=time.time(),
            energy_level=energy_level,
            zcr=zcr,
            spectral_centroid=spectral_centroid,
            was_recorded=was_recorded,
            recording_duration_ms=recording_duration_ms,
            noise_floor_estimate=noise_floor,
            speech_probability=speech_prob
        )
        
        self._store_metrics(channel_name, metrics)
        return metrics
    
    def _calculate_zcr(self, audio_chunk: np.ndarray) -> float:
        """Calculate Zero Crossing Rate"""
        signs = np.sign(audio_chunk)
        sign_changes = np.diff(signs)
        zero_crossings = np.sum(np.abs(sign_changes)) / 2
        return zero_crossings / len(audio_chunk)
    
    def _calculate_spectral_centroid(self, audio_chunk: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral centroid (brightness measure)"""
        fft = np.fft.fft(audio_chunk)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_chunk), 1/sample_rate)
        
        # Only use positive frequencies
        half_len = len(freqs) // 2
        magnitude = magnitude[:half_len]
        freqs = freqs[:half_len]
        
        if np.sum(magnitude) == 0:
            return 0.0
        
        centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        return centroid
    
    def _estimate_noise_floor(self, audio_chunk: np.ndarray) -> float:
        """Estimate noise floor using lower percentiles"""
        energy_levels = audio_chunk ** 2
        return np.percentile(energy_levels, 10)  # 10th percentile as noise floor
    
    def _estimate_speech_probability(self, audio_chunk: np.ndarray, sample_rate: int) -> float:
        """Estimate probability that audio contains speech"""
        # Simple heuristic based on energy distribution and spectral characteristics
        energy = np.mean(audio_chunk ** 2)
        zcr = self._calculate_zcr(audio_chunk)
        spectral_centroid = self._calculate_spectral_centroid(audio_chunk, sample_rate)
        
        # Speech typically has:
        # - Moderate energy levels
        # - ZCR in range 0.05-0.3
        # - Spectral centroid in speech range (300-3000 Hz)
        
        energy_score = 1.0 if 1e-06 < energy < 1e-03 else 0.5
        zcr_score = 1.0 if 0.05 < zcr < 0.3 else 0.3
        spectral_score = 1.0 if 300 < spectral_centroid < 3000 else 0.4
        
        return (energy_score + zcr_score + spectral_score) / 3.0
    
    def _store_metrics(self, channel_name: str, metrics: ChannelMetrics):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO channel_metrics 
            (channel_name, timestamp, energy_level, zcr, spectral_centroid, 
             was_recorded, recording_duration_ms, noise_floor_estimate, speech_probability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            channel_name, metrics.timestamp, metrics.energy_level, metrics.zcr,
            metrics.spectral_centroid, metrics.was_recorded, metrics.recording_duration_ms,
            metrics.noise_floor_estimate, metrics.speech_probability
        ))
        
        conn.commit()
        conn.close()
    
    def get_channel_metrics(self, channel_name: str, hours_back: int = 24) -> List[ChannelMetrics]:
        """Retrieve metrics for a channel within specified time window"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (hours_back * 3600)
        
        cursor.execute("""
            SELECT timestamp, energy_level, zcr, spectral_centroid, was_recorded,
                   recording_duration_ms, noise_floor_estimate, speech_probability
            FROM channel_metrics 
            WHERE channel_name = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """, (channel_name, cutoff_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ChannelMetrics(*row) for row in rows]

class VadAutoTuner:
    """Analyzes channel performance and automatically adjusts VAD parameters"""
    
    def __init__(self, config_path: str = "radio_channels.json"):
        self.config_path = config_path
        self.metrics_collector = VadMetricsCollector()
        self.logger = logging.getLogger(__name__)
        self.adjustment_history = defaultdict(list)
    
    def load_channel_config(self) -> Dict:
        """Load channel configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_channel_config(self, config: Dict):
        """Save updated channel configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def analyze_channel_performance(self, channel_name: str, 
                                  auto_adjust_config: AutoAdjustConfig) -> Dict:
        """Analyze channel performance and calculate optimal parameters"""
        
        metrics = self.metrics_collector.get_channel_metrics(
            channel_name, auto_adjust_config.analysis_window_hours
        )
        
        if len(metrics) < auto_adjust_config.min_samples_required:
            self.logger.warning(f"Insufficient data for {channel_name}: "
                              f"{len(metrics)} samples (need {auto_adjust_config.min_samples_required})")
            return {}
        
        analysis = self._perform_statistical_analysis(metrics, auto_adjust_config)
        recommendations = self._calculate_parameter_recommendations(analysis, auto_adjust_config)
        
        return {
            'analysis': analysis,
            'recommendations': recommendations,
            'sample_count': len(metrics)
        }
    
    def _perform_statistical_analysis(self, metrics: List[ChannelMetrics], 
                                    config: AutoAdjustConfig) -> Dict:
        """Perform statistical analysis on collected metrics"""
        
        # Separate recorded vs non-recorded samples
        recorded_samples = [m for m in metrics if m.was_recorded]
        not_recorded_samples = [m for m in metrics if not m.was_recorded]
        
        # Calculate statistics for energy levels
        all_energy = [m.energy_level for m in metrics]
        recorded_energy = [m.energy_level for m in recorded_samples]
        not_recorded_energy = [m.energy_level for m in not_recorded_samples]
        
        # Calculate noise floor (10th percentile of non-recorded samples)
        noise_floor = np.percentile(not_recorded_energy, 10) if not_recorded_energy else 0
        
        # Calculate speech energy threshold (median of recorded samples)
        speech_threshold = np.median(recorded_energy) if recorded_energy else 0
        
        # Analyze false positives (low speech probability but recorded)
        false_positives = [m for m in recorded_samples if m.speech_probability < 0.3]
        false_positive_rate = len(false_positives) / len(recorded_samples) if recorded_samples else 0
        
        # Analyze potential missed recordings (high speech probability but not recorded)
        potential_missed = [m for m in not_recorded_samples if m.speech_probability > 0.7]
        potential_missed_rate = len(potential_missed) / len(not_recorded_samples) if not_recorded_samples else 0
        
        # Calculate ZCR statistics
        recorded_zcr = [m.zcr for m in recorded_samples]
        zcr_range = (np.percentile(recorded_zcr, 5), np.percentile(recorded_zcr, 95)) if recorded_zcr else (0.05, 0.35)
        
        # Calculate recording duration statistics
        durations = [m.recording_duration_ms for m in recorded_samples if m.recording_duration_ms > 0]
        short_recordings = len([d for d in durations if d < 1000])  # < 1 second
        short_recording_rate = short_recordings / len(durations) if durations else 0
        
        return {
            'total_samples': len(metrics),
            'recorded_samples': len(recorded_samples),
            'recording_rate': len(recorded_samples) / len(metrics),
            'noise_floor': noise_floor,
            'speech_threshold': speech_threshold,
            'false_positive_rate': false_positive_rate,
            'potential_missed_rate': potential_missed_rate,
            'zcr_range': zcr_range,
            'avg_recording_duration': statistics.mean(durations) if durations else 0,
            'short_recording_rate': short_recording_rate,
            'energy_stats': {
                'min': min(all_energy),
                'max': max(all_energy),
                'median': statistics.median(all_energy),
                'p10': np.percentile(all_energy, 10),
                'p90': np.percentile(all_energy, 90)
            }
        }
    
    def _calculate_parameter_recommendations(self, analysis: Dict, 
                                           config: AutoAdjustConfig) -> Dict:
        """Calculate recommended VAD parameter adjustments"""
        
        recommendations = {}
        
        # Energy threshold recommendation
        if analysis['false_positive_rate'] > 0.2:  # Too many false positives
            # Increase threshold to reduce false positives
            new_threshold = analysis['speech_threshold'] * 0.8
            recommendations['energy_threshold'] = new_threshold
            recommendations['energy_threshold_reason'] = "Reducing false positives"
        
        elif analysis['potential_missed_rate'] > 0.1:  # Missing too many recordings
            # Decrease threshold to catch more speech
            new_threshold = analysis['noise_floor'] * config.sensitivity_factor
            recommendations['energy_threshold'] = new_threshold
            recommendations['energy_threshold_reason'] = "Improving sensitivity"
        
        # ZCR range recommendation
        if analysis['zcr_range'][0] > 0 and analysis['zcr_range'][1] > 0:
            # Adjust ZCR range based on actual speech patterns
            zcr_min = max(0.01, analysis['zcr_range'][0] * 0.8)  # 20% below observed range
            zcr_max = min(0.9, analysis['zcr_range'][1] * 1.2)   # 20% above observed range
            recommendations['zcr_min'] = zcr_min
            recommendations['zcr_max'] = zcr_max
            recommendations['zcr_reason'] = "Optimizing for observed speech patterns"
        
        # Minimum transmission duration recommendation
        if analysis['short_recording_rate'] > 0.3:  # Too many short recordings
            # Increase minimum transmission duration
            current_avg = analysis['avg_recording_duration']
            new_min = max(1000, current_avg * 0.5)  # At least 1 second, or half of average
            recommendations['min_transmission_ms'] = new_min
            recommendations['min_transmission_reason'] = "Reducing short recordings"
        
        # Speech frames to start recommendation
        if analysis['false_positive_rate'] > 0.15:
            recommendations['speech_frames_to_start'] = 8  # More conservative
            recommendations['speech_frames_reason'] = "Reducing false positives"
        elif analysis['potential_missed_rate'] > 0.15:
            recommendations['speech_frames_to_start'] = 3  # More sensitive
            recommendations['speech_frames_reason'] = "Improving responsiveness"
        
        return recommendations
    
    def apply_auto_adjustments(self, channel_name: str, force: bool = False) -> bool:
        """Apply automatic adjustments if criteria are met"""
        
        config = self.load_channel_config()
        channel_config = None
        
        # Find the channel configuration
        for channel in config['channels']:
            if channel['name'] == channel_name:
                channel_config = channel
                break
        
        if not channel_config:
            self.logger.error(f"Channel {channel_name} not found in configuration")
            return False
        
        auto_adjust_config = channel_config.get('auto_adjust', {})
        if not auto_adjust_config.get('enabled', False) and not force:
            return False
        
        # Parse auto-adjust configuration
        adjust_config = AutoAdjustConfig(
            enabled=auto_adjust_config.get('enabled', True),
            analysis_window_hours=auto_adjust_config.get('analysis_window_hours', 24),
            adjustment_frequency_hours=auto_adjust_config.get('adjustment_frequency_hours', 168),
            min_samples_required=auto_adjust_config.get('min_samples_required', 50),
            sensitivity_factor=auto_adjust_config.get('sensitivity_factor', 1.5)
        )
        
        # Check if enough time has passed since last adjustment
        last_adjustment = self.adjustment_history[channel_name]
        if last_adjustment and not force:
            hours_since_last = (time.time() - last_adjustment[-1]) / 3600
            if hours_since_last < adjust_config.adjustment_frequency_hours:
                return False
        
        # Perform analysis
        analysis_result = self.analyze_channel_performance(channel_name, adjust_config)
        
        if not analysis_result:
            return False
        
        recommendations = analysis_result['recommendations']
        if not recommendations:
            self.logger.info(f"No adjustments needed for {channel_name}")
            return False
        
        # Apply recommendations
        vad_config = channel_config['vad']
        applied_changes = []
        
        for param, value in recommendations.items():
            if param.endswith('_reason'):
                continue
            
            if param in vad_config:
                old_value = vad_config[param]
                vad_config[param] = value
                applied_changes.append(f"{param}: {old_value} -> {value}")
                
                reason = recommendations.get(f"{param}_reason", "Optimization")
                self.logger.info(f"Adjusted {channel_name} {param}: {old_value} -> {value} ({reason})")
        
        if applied_changes:
            # Save updated configuration
            self.save_channel_config(config)
            
            # Record adjustment in history
            self.adjustment_history[channel_name].append(time.time())
            
            # Log analysis summary
            analysis = analysis_result['analysis']
            self.logger.info(f"Auto-adjustment for {channel_name}:")
            self.logger.info(f"  Samples analyzed: {analysis['total_samples']}")
            self.logger.info(f"  Recording rate: {analysis['recording_rate']:.2%}")
            self.logger.info(f"  False positive rate: {analysis['false_positive_rate']:.2%}")
            self.logger.info(f"  Potential missed rate: {analysis['potential_missed_rate']:.2%}")
            self.logger.info(f"  Changes applied: {', '.join(applied_changes)}")
            
            return True
        
        return False
    
    def run_auto_adjustment_cycle(self, specific_channel: str = None):
        """Run auto-adjustment for all enabled channels or a specific channel"""
        
        config = self.load_channel_config()
        adjusted_channels = []
        
        for channel in config['channels']:
            channel_name = channel['name']
            
            if specific_channel and channel_name != specific_channel:
                continue
            
            auto_adjust_config = channel.get('auto_adjust', {})
            if auto_adjust_config.get('enabled', False):
                try:
                    if self.apply_auto_adjustments(channel_name):
                        adjusted_channels.append(channel_name)
                except Exception as e:
                    self.logger.error(f"Error adjusting {channel_name}: {e}")
        
        self.logger.info(f"Auto-adjustment cycle complete. Adjusted channels: {adjusted_channels}")
        return adjusted_channels

def main():
    """Command-line interface for VAD auto-tuner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VAD Auto-Tuner")
    parser.add_argument('--channel', help="Specific channel to analyze/adjust")
    parser.add_argument('--analyze-only', action='store_true', help="Only analyze, don't adjust")
    parser.add_argument('--force', action='store_true', help="Force adjustment regardless of timing")
    parser.add_argument('--config', default='radio_channels.json', help="Configuration file path")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    tuner = VadAutoTuner(args.config)
    
    if args.analyze_only:
        # Just perform analysis
        config = tuner.load_channel_config()
        for channel in config['channels']:
            if args.channel and channel['name'] != args.channel:
                continue
            
            auto_adjust_config = channel.get('auto_adjust', {})
            if auto_adjust_config.get('enabled', False):
                adjust_config = AutoAdjustConfig(
                    enabled=True,
                    analysis_window_hours=auto_adjust_config.get('analysis_window_hours', 24),
                    adjustment_frequency_hours=auto_adjust_config.get('adjustment_frequency_hours', 168),
                    min_samples_required=auto_adjust_config.get('min_samples_required', 50),
                    sensitivity_factor=auto_adjust_config.get('sensitivity_factor', 1.5)
                )
                
                result = tuner.analyze_channel_performance(channel['name'], adjust_config)
                if result:
                    print(f"\nAnalysis for {channel['name']}:")
                    print(json.dumps(result, indent=2))
    else:
        # Run adjustment cycle
        tuner.run_auto_adjustment_cycle(args.channel)

if __name__ == "__main__":
    main()
