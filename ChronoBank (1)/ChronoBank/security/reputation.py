# ChronoBank/security/reputation.py

class ReputationManager:
    @staticmethod
    def can_make_high_risk_transaction(user):
        """
        Allow only users with high reputation (>50) and low risk (<30)
        to make high-risk transactions.
        """
        return user.get("reputation") > 50 and user.get("risk_score") < 40

    @staticmethod
    def adjust_reputation(user, delta, save_callback=None):
        """
        Increase or decrease the reputation and inversely adjust risk score.
        Range is clamped between 0 and 100.
        """
        user["reputation"] = max(0, min(100, user.get("reputation", 50) + delta))
        user["risk_score"] = max(0, min(100, user.get("risk_score", 50) - delta))

        if save_callback:
            save_callback()
