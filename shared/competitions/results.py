"""This file contains classes for understanding competition results."""

class CompetitionResults():
    """
    A class to represent the result for a specific competition and solver.
    """
    def __init__(self, competition_name=None, competition_result=None, outcome_description=None):
        """Create the object and optionally initalize its members."""
        self.competition_name = competition_name
        self.competition_result = competition_result
        self.outcome_description = outcome_description

class CompetitionResultsCollector():
    """
    A class to represent all competition results for a solver.
    """
    def __init__(self):
        """Initiative the object."""
        self.competition_results = []

    def add_competition(self, competition_name, competition_result, outcome_description):
        """Add a single event to the competition list."""
        self.competition_results.append(
            CompetitionResults(competition_name, competition_result, outcome_description))

    def retrieve_competitions(self):
        """Retrieve all competition."""
        return self.competition_results

    def all_competition_names(self):
        """Retrieve a generator of all competition names."""
        return [item.competition_name for item in self.competition_results]

    def all_competition_results(self):
        """Retrieve a generator of all competition results."""
        return [item.competition_result for item in self.competition_results]

    def all_competition_outcome_descriptions(self):
        """Retrieve a generator of all competition outcome descriptions."""
        return [item.outcome_description for item in self.competition_results]
