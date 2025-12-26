#!/usr/bin/env python3
"""
THESIDIA // Astronomical & Temporal Pattern Recognition
Multi-calendar system integration for pattern detection across all ancient cultures
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import json
import math


@dataclass
class CalendarEvent:
    """Represents an event in a calendar system"""
    calendar: str
    date: str
    cycle_position: float  # 0.0 to 1.0, position in cycle
    cycle_name: str
    significance: str
    metadata: Dict[str, Any]


@dataclass
class AstronomicalPosition:
    """Planetary and astronomical positions"""
    timestamp: datetime
    planets: Dict[str, Dict[str, float]]  # planet -> {longitude, latitude, distance}
    lunar_phase: float  # 0.0 to 1.0
    solar_position: Dict[str, float]
    galactic_center_distance: float


class AstronomicalPatternEngine:
    """
    Multi-calendar astronomical pattern recognition engine
    
    Integrates:
    - Maya Long Count (5,125-year cycles)
    - Chinese 60-year cycles
    - Zodiac ages (2,160-year precessional periods)
    - Hindu Yuga cycles (4,320,000 years)
    - Egyptian calendar systems
    - Sumerian/Babylonian calendars
    - Celtic calendar systems
    - Native American calendar systems
    - And all forgotten/alternative calendar systems
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.calendars_file = self.data_dir / "astronomical_calendars.json"
        self.events_file = self.data_dir / "historical_events.json"
        self.patterns_file = self.data_dir / "temporal_patterns.json"
        
        # Astronomical constants (define BEFORE loading calendars)
        self.PLANETARY_PERIODS = {
            'mercury': 87.97,  # days
            'venus': 224.7,
            'earth': 365.256,
            'mars': 686.98,
            'jupiter': 4332.59,  # ~11.86 years
            'saturn': 10759.22,  # ~29.46 years
            'uranus': 30688.5,   # ~84 years
            'neptune': 60182,     # ~165 years
        }
        
        # Precession of equinoxes
        self.PRECESSION_PERIOD = 25772  # years (Great Year)
        self.ZODIAC_AGE_PERIOD = 2155  # years (one zodiac age)
        
        # Maya Long Count
        self.MAYA_BAKTUN = 144000  # days (~394.26 years)
        self.MAYA_GRAND_CYCLE = 13 * self.MAYA_BAKTUN  # ~5,125 years
        
        # Chinese 60-year cycle
        self.CHINESE_CYCLE = 60  # years
        
        # Hindu Yuga cycles
        self.YUGA_CYCLES = {
            'satya': 1728000,  # years
            'treta': 1296000,
            'dvapara': 864000,
            'kali': 432000
        }
        
        # Initialize calendar systems (AFTER constants defined)
        self.calendars = self._load_calendars()
        self.historical_events = self._load_events()
        self.patterns = self._load_patterns()
    
    def _load_calendars(self) -> Dict[str, Any]:
        """Load calendar system definitions"""
        if self.calendars_file.exists():
            try:
                with open(self.calendars_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                pass  # Fall through to defaults
        
        # Default calendar systems
        return {
            'maya': {
                'name': 'Maya Long Count',
                'cycle_days': self.MAYA_GRAND_CYCLE,
                'description': '5,125-year grand cycle',
                'epoch': '3114-08-11 BCE'
            },
            'chinese': {
                'name': 'Chinese 60-Year Cycle',
                'cycle_days': self.CHINESE_CYCLE * 365.25,
                'description': '60-year sexagenary cycle',
                'epoch': '2637 BCE'
            },
            'zodiac': {
                'name': 'Zodiac Age',
                'cycle_days': self.ZODIAC_AGE_PERIOD * 365.25,
                'description': '2,160-year precessional age',
                'epoch': '0 CE'
            },
            'hindu': {
                'name': 'Hindu Yuga',
                'cycle_days': sum(self.YUGA_CYCLES.values()) * 365.25,
                'description': '4,320,000-year Maha Yuga',
                'epoch': '3102 BCE'
            },
            'egyptian': {
                'name': 'Egyptian Calendar',
                'cycle_days': 365,  # Fixed calendar
                'description': '365-day civil calendar',
                'epoch': '4241 BCE'
            },
            'sumerian': {
                'name': 'Sumerian/Babylonian',
                'cycle_days': 360,  # Base-60 system
                'description': '360-day year with intercalation',
                'epoch': '3761 BCE'
            },
            'celtic': {
                'name': 'Celtic Calendar',
                'cycle_days': 365.25,
                'description': 'Lunar-solar calendar',
                'epoch': 'Unknown'
            }
        }
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load historical events database"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                pass  # Fall through to empty list
        
        return []
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load detected temporal patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                pass  # Fall through to defaults
        
        return {'patterns': [], 'correlations': []}
    
    def calculate_planetary_position(self, planet: str, date: datetime) -> Dict[str, float]:
        """
        Calculate approximate planetary position
        Simplified calculation - for production use astronomical libraries
        """
        if planet.lower() not in self.PLANETARY_PERIODS:
            return {}
        
        period_days = self.PLANETARY_PERIODS[planet.lower()]
        
        # Reference date (J2000.0)
        reference = datetime(2000, 1, 1, 12, 0, 0)
        days_since = (date - reference).total_seconds() / 86400
        
        # Calculate position in orbit (0.0 to 1.0)
        orbit_position = (days_since % period_days) / period_days
        
        # Convert to degrees (longitude)
        longitude = orbit_position * 360
        
        return {
            'longitude': longitude,
            'phase': orbit_position,
            'days_in_cycle': days_since % period_days
        }
    
    def calculate_maya_long_count(self, date: datetime) -> Dict[str, Any]:
        """Calculate Maya Long Count position"""
        # Maya epoch: August 11, 3114 BCE
        maya_epoch = datetime(3114, 8, 11)
        
        # Calculate days since epoch
        days_since = (date - maya_epoch).total_seconds() / 86400
        
        # Calculate baktuns (20 katuns = 1 baktun)
        baktuns = int(days_since / self.MAYA_BAKTUN)
        days_in_baktun = days_since % self.MAYA_BAKTUN
        
        # Calculate position in grand cycle (13 baktuns)
        cycle_position = (baktuns % 13) / 13.0
        
        return {
            'baktun': baktuns,
            'days_since_epoch': days_since,
            'cycle_position': cycle_position,
            'in_grand_cycle': baktuns < 13,
            'grand_cycle_complete': baktuns >= 13
        }
    
    def calculate_chinese_cycle(self, date: datetime) -> Dict[str, Any]:
        """Calculate Chinese 60-year cycle position"""
        # Reference: 1984 is year 1 of current cycle
        reference_year = 1984
        year = date.year
        
        cycle_year = ((year - reference_year) % self.CHINESE_CYCLE) + 1
        cycle_number = (year - reference_year) // self.CHINESE_CYCLE
        
        return {
            'cycle_year': cycle_year,
            'cycle_number': cycle_number,
            'cycle_position': cycle_year / self.CHINESE_CYCLE,
            'heavenly_stem': (cycle_year - 1) % 10,
            'earthly_branch': (cycle_year - 1) % 12
        }
    
    def calculate_zodiac_age(self, date: datetime) -> Dict[str, Any]:
        """Calculate current zodiac age based on precession"""
        # Approximate: Age of Pisces ending, Age of Aquarius beginning
        # Precession moves ~1 degree per 72 years
        reference_year = 0  # Approximate start of Age of Pisces
        years_since = date.year - reference_year
        
        # Calculate age position
        age_number = years_since // self.ZODIAC_AGE_PERIOD
        age_position = (years_since % self.ZODIAC_AGE_PERIOD) / self.ZODIAC_AGE_PERIOD
        
        # Zodiac ages (backwards due to precession)
        ages = ['Pisces', 'Aquarius', 'Capricorn', 'Sagittarius', 'Scorpio', 
                'Libra', 'Virgo', 'Leo', 'Cancer', 'Gemini', 'Taurus', 'Aries']
        
        current_age_index = (len(ages) - 1 - (age_number % len(ages))) % len(ages)
        current_age = ages[current_age_index]
        
        return {
            'age': current_age,
            'age_position': age_position,
            'transition_progress': age_position,
            'next_age': ages[(current_age_index - 1) % len(ages)]
        }
    
    def calculate_all_calendars(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate positions in all calendar systems"""
        if date is None:
            date = datetime.now()
        
        return {
            'date': date.isoformat(),
            'maya': self.calculate_maya_long_count(date),
            'chinese': self.calculate_chinese_cycle(date),
            'zodiac': self.calculate_zodiac_age(date),
            'planets': {
                planet: self.calculate_planetary_position(planet, date)
                for planet in self.PLANETARY_PERIODS.keys()
            }
        }
    
    def find_pattern_correlations(self, event_date: datetime, 
                                  window_days: int = 365) -> List[Dict[str, Any]]:
        """
        Find historical events that occurred at similar calendar positions
        """
        correlations = []
        
        # Calculate calendar positions for event
        event_calendars = self.calculate_all_calendars(event_date)
        
        # Search historical events
        for event in self.historical_events:
            event_dt = datetime.fromisoformat(event['date'])
            
            # Check if within time window
            days_diff = abs((event_dt - event_date).days)
            if days_diff > window_days:
                continue
            
            # Calculate calendar positions for historical event
            hist_calendars = self.calculate_all_calendars(event_dt)
            
            # Find matching calendar positions
            matches = []
            
            # Check Maya cycle position
            maya_diff = abs(event_calendars['maya']['cycle_position'] - 
                          hist_calendars['maya']['cycle_position'])
            if maya_diff < 0.1:  # Within 10% of cycle
                matches.append({
                    'calendar': 'maya',
                    'similarity': 1.0 - maya_diff,
                    'event_position': hist_calendars['maya']['cycle_position'],
                    'current_position': event_calendars['maya']['cycle_position']
                })
            
            # Check Chinese cycle
            chinese_diff = abs(event_calendars['chinese']['cycle_position'] - 
                             hist_calendars['chinese']['cycle_position'])
            if chinese_diff < 0.1:
                matches.append({
                    'calendar': 'chinese',
                    'similarity': 1.0 - chinese_diff,
                    'event_position': hist_calendars['chinese']['cycle_position'],
                    'current_position': event_calendars['chinese']['cycle_position']
                })
            
            # Check planetary positions
            for planet in self.PLANETARY_PERIODS.keys():
                if planet in event_calendars['planets'] and planet in hist_calendars['planets']:
                    phase_diff = abs(event_calendars['planets'][planet]['phase'] - 
                                   hist_calendars['planets'][planet]['phase'])
                    if phase_diff < 0.15:  # Within 15% of orbit
                        matches.append({
                            'calendar': f'planet_{planet}',
                            'similarity': 1.0 - phase_diff,
                            'event_position': hist_calendars['planets'][planet]['phase'],
                            'current_position': event_calendars['planets'][planet]['phase']
                        })
            
            if matches:
                correlations.append({
                    'event': event,
                    'matches': matches,
                    'days_apart': days_diff,
                    'overall_similarity': sum(m['similarity'] for m in matches) / len(matches)
                })
        
        # Sort by similarity
        correlations.sort(key=lambda x: x['overall_similarity'], reverse=True)
        
        return correlations[:10]  # Top 10
    
    def predict_cycle_phase(self, calendar: str, days_ahead: int = 365) -> Dict[str, Any]:
        """Predict future calendar positions"""
        future_date = datetime.now() + timedelta(days=days_ahead)
        return self.calculate_all_calendars(future_date)
    
    def detect_recurring_patterns(self) -> List[Dict[str, Any]]:
        """
        Detect recurring patterns across calendar systems and historical events
        """
        patterns = []
        
        # Group events by calendar positions
        event_groups = {}
        
        for event in self.historical_events:
            event_dt = datetime.fromisoformat(event['date'])
            calendars = self.calculate_all_calendars(event_dt)
            
            # Create signature from key positions
            signature = (
                round(calendars['maya']['cycle_position'], 2),
                round(calendars['chinese']['cycle_position'], 2),
                round(calendars['zodiac']['age_position'], 2)
            )
            
            if signature not in event_groups:
                event_groups[signature] = []
            
            event_groups[signature].append(event)
        
        # Find signatures with multiple events
        for signature, events in event_groups.items():
            if len(events) >= 2:
                patterns.append({
                    'signature': signature,
                    'event_count': len(events),
                    'events': events,
                    'pattern_type': 'calendar_correlation',
                    'confidence': min(1.0, len(events) / 5.0)  # Higher confidence with more events
                })
        
        return patterns
    
    def save_patterns(self):
        """Save detected patterns to file"""
        patterns = self.detect_recurring_patterns()
        
        self.patterns = {
            'patterns': patterns,
            'last_updated': datetime.now().isoformat(),
            'total_patterns': len(patterns)
        }
        
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")


if __name__ == '__main__':
    # Test the system
    engine = AstronomicalPatternEngine()
    
    # Calculate current positions
    now = datetime.now()
    positions = engine.calculate_all_calendars(now)
    
    print("Current Calendar Positions:")
    print(json.dumps(positions, indent=2, default=str))
    
    # Find correlations for a specific date
    test_date = datetime(2020, 1, 1)
    correlations = engine.find_pattern_correlations(test_date)
    
    print(f"\nPattern Correlations for {test_date}:")
    print(f"Found {len(correlations)} correlations")

