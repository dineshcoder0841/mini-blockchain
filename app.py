import math
from flask import Flask, render_template, request, redirect, url_for, flash
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = "change-this-secret"
blockchain = Blockchain()


@app.route("/")
def index():
    return render_template("index.html", blockchain=blockchain, valid=blockchain.is_valid())


@app.route("/add", methods=["POST"])
def add_transaction():
    sender = request.form["sender"].strip()
    receiver = request.form["receiver"].strip()
    if not sender or not receiver:
        flash("Sender and receiver cannot be empty.", "danger")
        return redirect(url_for("index"))
    if sender.lower() == receiver.lower():
        flash("Sender and receiver must be different.", "danger")
        return redirect(url_for("index"))
    try:
        amount = float(request.form["amount"])
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number.", "danger")
        return redirect(url_for("index"))

    blockchain.add_transaction(sender, receiver, amount)
    flash("Transaction added to pending pool. Click 'Mine Block' to confirm it.", "success")
    return redirect(url_for("index"))


@app.route("/mine", methods=["POST"])
def mine_block():
    block = blockchain.mine_pending()
    if block is None:
        flash("No pending transactions to mine.", "warning")
    else:
        flash(f"Block #{block.index} mined successfully!", "success")
    return redirect(url_for("index"))

@app.route("/tamper/<int:index>/<field>/<value>")
def tamper(index, field, value):
    if index < 1 or index >= len(blockchain.chain):
        flash("Block not found. Use block number 1 or higher.", "warning")
        return redirect(url_for("index"))

    block = blockchain.chain[index]
    tx = block.transactions[0]          # first transaction in that block

    try:
        if field == "amount":
            tx["amount"] = float(value)
        elif field in ("sender", "receiver"):
            tx[field] = value
        else:
            flash("Field must be amount, sender or receiver.", "warning")
            return redirect(url_for("index"))
    except ValueError:
        flash("Amount must be a number.", "warning")
        return redirect(url_for("index"))

    # Attacker is smarter: recompute the block's own hash to hide the change
    if request.args.get("rehash") == "1":
        block.hash = block.calculate_hash()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)