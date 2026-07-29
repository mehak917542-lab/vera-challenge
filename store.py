# In-memory context storage for the challenge.
# The judge keeps our server running during the test,
# so in-memory persistence is sufficient.

categories = {}
merchants = {}
customers = {}
triggers = {}

# Conversation state will be used later by /v1/reply
conversations = {}

# Used later to prevent duplicate trigger messages
sent_suppression_keys = set()


def get_store_for_scope(scope: str):
    """Return the correct context dictionary for a scope."""

    stores = {
        "category": categories,
        "merchant": merchants,
        "customer": customers,
        "trigger": triggers,
    }

    return stores.get(scope)

def get_category(category_id: str):
    """Get a category payload by ID."""
    item = categories.get(category_id)

    if not item:
        return None

    return item["payload"]


def get_merchant(merchant_id: str):
    """Get a merchant payload by ID."""
    item = merchants.get(merchant_id)

    if not item:
        return None

    return item["payload"]


def get_trigger(trigger_id: str):
    """Get a trigger payload by ID."""
    item = triggers.get(trigger_id)

    if not item:
        return None

    return item["payload"]


def get_customer(customer_id: str):
    """Get a customer payload by ID."""
    item = customers.get(customer_id)

    if not item:
        return None

    return item["payload"]

def seed_test_data():
    """Load deterministic development data for local testing."""

    categories["dentists"] = {
        "version": 1,
        "payload": {
            "slug": "dentists",
            "voice": "peer_clinical"
        }
    }

    merchants["m_001_drmeera_dentist_delhi"] = {
        "version": 1,
        "payload": {
            "merchant_id": "m_001_drmeera_dentist_delhi",
            "category_slug": "dentists",
            "identity": {
                "name": "Dr. Meera's Dental Clinic",
                "owner_name": "Dr. Meera",
                "city": "Delhi",
                "locality": "Lajpat Nagar",
                "languages": ["en"]
            }
        }
    }

    triggers["trg_test_research"] = {
        "version": 1,
        "payload": {
            "id": "trg_test_research",
            "scope": "merchant",
            "kind": "research_digest_release",
            "source": "external",
            "payload": {
                "merchant_id": "m_001_drmeera_dentist_delhi"
            },
            "urgency": 2,
            "suppression_key": "research:dentists:test"
        }
    }


# Load development data whenever the local server starts.
seed_test_data()