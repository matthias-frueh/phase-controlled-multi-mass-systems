"""Gemeinsame Einstellungen der Tests: Die Module in code/ liegen flach und importieren einander direkt."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code'))
sys.dont_write_bytecode = True
