#!/usr/bin/env python3
"""
Script to run Alembic migrations
"""
import sys
import os
from alembic.config import Config
from alembic import command

def main():
    # Set up the alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    if len(sys.argv) < 2:
        print("Usage: python run_alembic.py <command> [args...]")
        print("Examples:")
        print("  python run_alembic.py current")
        print("  python run_alembic.py upgrade head")
        print("  python run_alembic.py history")
        return
    
    cmd = sys.argv[1]
    
    try:
        if cmd == "current":
            command.current(alembic_cfg)
        elif cmd == "upgrade":
            if len(sys.argv) > 2:
                command.upgrade(alembic_cfg, sys.argv[2])
            else:
                command.upgrade(alembic_cfg, "head")
        elif cmd == "downgrade":
            if len(sys.argv) > 2:
                command.downgrade(alembic_cfg, sys.argv[2])
            else:
                print("Downgrade requires a revision argument")
        elif cmd == "history":
            command.history(alembic_cfg)
        elif cmd == "show":
            if len(sys.argv) > 2:
                command.show(alembic_cfg, sys.argv[2])
            else:
                print("Show requires a revision argument")
        else:
            print(f"Unknown command: {cmd}")
            print("Available commands: current, upgrade, downgrade, history, show")
    except Exception as e:
        print(f"Error running alembic command: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

