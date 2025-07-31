#!/usr/bin/env python3
"""
Entry point for running the screening bot as a module.
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add the parent directory to sys.path to enable proper imports
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Import and run the main application
    from test_phase1 import main
    import asyncio
    
    asyncio.run(main())
