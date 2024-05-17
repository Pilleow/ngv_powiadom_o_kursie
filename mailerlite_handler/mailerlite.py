import mailerlite as mlite


class MailerLite:

    def __init__(self, api_key: str):
        self.client = mlite.Client({
            "api_key": api_key
        })

    def create_subscriber(self, email: str, first_name: str, last_name: str, add_to_groups: list=[]):
        out = self.client.subscribers.create(email, groups=add_to_groups, status='active', fields={
            'name': first_name,
            'last_name': last_name,
        })
        if "errors" in out:
            raise RuntimeError(str(out["errors"]))
        return out
