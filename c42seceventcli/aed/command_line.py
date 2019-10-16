from c42seceventcli.aed.event_extraction_cli import main as extract_aed_events


# Call event_extraction_cli from command line via 'c42aed' custom command, defined in setup.py
def main():
    extract_aed_events()
