import hashlib
import json
from time import time


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, difficulty=4):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions  # list of transaction dicts
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.mine_block()

    def calculate_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        h = self.calculate_hash()
        while not h.startswith(target):
            self.nonce += 1
            h = self.calculate_hash()
        print(f"Block #{self.index} mined (nonce={self.nonce}): {h}")
        return h


class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(Block(0, time(), [], "0", self.difficulty))

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append(
            {"sender": sender, "receiver": receiver, "amount": amount}
        )

    def mine_pending(self):
        """Bundle all pending transactions into a new mined block."""
        if not self.pending_transactions:
            return None
        block = Block(
            len(self.chain),
            time(),
            self.pending_transactions,
            self.chain[-1].hash,
            self.difficulty,
        )
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            cur, prev = self.chain[i], self.chain[i - 1]
            if cur.hash != cur.calculate_hash():
                return False
            if cur.previous_hash != prev.hash:
                return False
            if not cur.hash.startswith("0" * cur.difficulty):
                return False
        return True