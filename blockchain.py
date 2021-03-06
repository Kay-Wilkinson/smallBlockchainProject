import hashlib
from hashlib import sha256
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from textwrap import dedent

import requests
from flask import Flask, jsonify, request 



class Blockchain(object):
	def _init_(self):
		self.chain = []
		self.current_transactions = []

		# create the genesis block
		self.new_block(previous_hash=1, proof=100)

	def new_block(self, proof, previous_hash=None):
		#create a new block and add it to the chain 
		"""
		:param proof: <int> The proof given by the Proof of Work algorithm
		:param previous_hash: (Optional) <str> Hash of previous Block
		:return: <dict> New Block 

		"""

		block = {
		'index': len(self.chain) + 1,
		'timestamp': time(),
		'transactions': self.current_transactions,
		'proof': proof,
		'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		#reset the current list of transactions
		self.current_transactions = []

		self.chain.append(block)
		return block
		# pass 

	def new_transaction(self, sender, recipient, amount):
		"""
		#creates a new transaction to the list of transactions
		:param sender: <str> Address of the Sender
		:param recipient: <str> Address of the Recipient
		:param amountL <int> Amount
		:return: <int> The index of the BLock that will hold this transaction
		"""
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
			})

		return self.last_block['index'] + 1 
		# returns index of the block that the transaction was added to - the next one to mined. 
		# pass

	def proof_of_work(self, last_proof):
		"""
		Simple POW algorith,m:
		- Find a number p' such that hash(pp') contains leading 4 zeros, where p is the previous p'
		- p is the previous proof, and p' is the new proof

		:param last_proof: <int>
		:return: <int>
		"""

		proof = 0 
		while self.valid_proof(last_proof, proof) is False:
			proof += 1 
		return proof 
	@staticmethod
	def valid_proof(last_proof, proof):
		"""
		Validates the proof : Does hash(last_proof, proof) contain 4 leading zeroes?

		:param last_proof: <int> Previous proof
		:param proof: <int> Current proof
		:return: <bool> True if correct, False if not. 
		"""
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"
		#changing the hash to a different integer set will change the difficulty of the POW.
		#This change would have a quadratic impact upon computational power to mine

	
	@property 
	def last_block(self):
		#returns the tail of the chain
		#pass
		return self.chain[-1] 

	@staticmethod 
	# no implicit arguments of the class it is called from. Can refactor this to method?
	def hash(block):
		#hashes the block
		"""
		Creates a SHA-256 hash of the Block

		:param block: <dict> Block
		:return: <str>
		"""
		#Dict must be ordered or inconsistent hashes D: 
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()
		pass


#Instantiate our Ndode
app = Flask(__name__)

#Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

#Instantiate the Blockchain
blockchain = Blockchain()

# @app.route('/mine', methods=['GET'])
# def mine():
# 	return "Mining new Block"

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	return "Adding new transaction"
	values = request.get_json()

	#Form verifcation in POST data 
	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing values', 400
	#create a new transaction
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
	response = {'message': f'Transaction will be added to Block {index}'}
	return jsonify(response), 201 

@app.route('/chain', methods=["GET"])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
	#We run the proof of work algorithm to get the next proof...
	last_block = blockchain.last_block
	last_proof = last_proof['proof']
	proof = blockchain.proof_of_work(last_proof)

	#recieve reward
	#Sender is "0" to signify that this node has mined a new coin.
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
		)

	#forge a new block by adding it to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
	'message': "New Block Forged",
	'index': block['index'],
	'transactions': block['transactions'],
	'proof': block['proof'],
	'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)






















