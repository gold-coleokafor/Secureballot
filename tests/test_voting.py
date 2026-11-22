"""
test_voting.py - Unit Tests for VotingService & HowToVote
"""

import unittest
from unittest.mock import MagicMock, patch
from voting import VotingService
from how_to_vote import show_how_to_vote


class TestVotingService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.ELECTION_NAME = "Secure Ballot 2026"
        self.voting_service = VotingService(self.mock_db)

    def test_navigation_exit_on_zero(self):
        with patch('builtins.input', side_effect=['0']):
            self.assertEqual(self.voting_service.run_vote(), 'exit')

    def test_navigation_return_none_on_99(self):
        with patch('builtins.input', side_effect=['99']):
            self.assertIsNone(self.voting_service.run_vote())

    def test_one_vote_per_voter_enforced(self):
        mock_voter = MagicMock()
        mock_voter.has_voted = True
        self.mock_db.get_voter.return_value = mock_voter

        with patch('builtins.input', side_effect=['00101', '1234', '']):
            self.assertIsNone(self.voting_service.run_vote())
            self.mock_db.get_voter.assert_called_with('00101')

    def test_successful_voting_order(self):
        mock_voter = MagicMock()
        mock_voter.has_voted = False
        self.mock_db.get_voter.return_value = mock_voter
        self.mock_db.check_pin.return_value = True
        self.mock_db.get_results.return_value = [(1, "Candidate A"), (2, "Candidate B")]
        self.mock_db.add_vote.return_value = True

        # Flow: ID=V001, PIN=1234, Candidate=1, Confirm=1
        with patch('builtins.input', side_effect=['V001', '1234', '1', '1', '']):
            result = self.voting_service.run_vote()
            self.mock_db.get_voter.assert_called_once_with('V001')
            self.mock_db.check_pin.assert_called_once_with('V001', '1234')
            self.mock_db.add_vote.assert_called_once_with('V001', 1)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()