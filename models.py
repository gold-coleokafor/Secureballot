class Voter:
    """A registered voter. The PIN is not stored here, only in the database."""

    def __init__(self, voter_id, has_voted=False):
        self.voter_id = voter_id
        self.has_voted = has_voted

    @classmethod
    def from_dict(cls, data):
        """Build a Voter from the dictionary the database gives us."""
        return cls(data["voter_id"], data["has_voted"])

    def __str__(self):
        status = "voted" if self.has_voted else "not voted yet"
        return f"{self.voter_id} ({status})"


class Candidate:
    """A candidate with the two vote counts used by the audit."""

    def __init__(self, candidate_id, name, vote_count=0, audit_count=0):
        self.candidate_id = candidate_id
        self.name = name
        self.vote_count = vote_count
        self.audit_count = audit_count

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["candidate_id"],
            data["name"],
            data.get("vote_count", 0),
            data.get("audit_count", 0),
        )

    def counts_match(self):
        """True if the results count and the audit count agree."""
        return self.vote_count == self.audit_count

    def __str__(self):
        return f"{self.candidate_id}. {self.name}"


class Admin:
    """The registration officer."""

    def __init__(self, admin_id):
        self.admin_id = admin_id

    def __str__(self):
        return f"Admin {self.admin_id}"
