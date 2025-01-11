"""This file contains classes for understanding competition results."""

class CompetitionResults():
    """
    A class to represent the result for a specific event and solver.
    """
    def __init__(self, event_name=None, event_result=None, outcome_description=None):
        """Create the object and optionally initalize its members."""
        self.event_name = event_name
        self.event_result = event_result
        self.outcome_description = outcome_description

class CompetitionResultsCollector():
    """
    A class to represent all event results for a solver.
    """
    def __init__(self):
        """Initiative the object."""
        self.event_results = []

    def add_event(self, event_name, event_result, outcome_description):
        """Add a single event to the event list."""
        self.event_results.append(
            CompetitionResults(event_name, event_result, outcome_description))

    def retrieve_events(self):
        """Retrieve all events."""
        return self.event_results

    def all_event_names(self):
        """Retrieve a generator of all event names."""
        return [item.event_name for item in self.event_results]

    def all_event_results(self):
        """Retrieve a generator of all event results."""
        return [item.event_result for item in self.event_results]

    def all_event_outcome_descriptions(self):
        """Retrieve a generator of all event outcome descriptions."""
        return [item.outcome_description for item in self.event_results]
