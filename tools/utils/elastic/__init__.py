from elasticsearch import Elasticsearch, helpers 


class ConnectionError(Exception):
    """Elasticsearch connection error."""
    pass


class Elastic:
    """Helper for insert data into elasticsearch."""

    def __init__(self, index, doc_type):
        self.index = index
        self.doc_type = doc_type
        self.client = Elasticsearch(["http://elasticsearch:9200"])

        # if server is invalid (elasticsearch is not active)
        if not self.client.ping():
            raise ConnectionError("Elasticsearch server is down")

    def __enter__(self):
        return self.client

    def upload(self, documents):
        data = [{
            "_index": self.index,
            "_type": self.doc_type,
            "_source": document
        } for document in documents]

        helpers.bulk(self.client, data)

    def __exit__(self, exc_type, value, traceback):
        pass
