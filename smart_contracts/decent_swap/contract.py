import beaker
from pyteal import *


app = beaker.Application("decent_swap")

escrow_address = Addr("LBRWYH2H3XXUUWYASOHU346CEU2DYH2GSJQYP2YHLVQXSP2SYPLGEABF2U")
dao_address = Addr("LBRWYH2H3XXUUWYASOHU346CEU2DYH2GSJQYP2YHLVQXSP2SYPLGEABF2U")


# @app.external
# def hello(name: abi.String, *, output: abi.String) -> Expr:
#     return output.set(Concat(Bytes("Hello, "), name.get()))


# define escrow approval program
@app.external
def escrow_approval_program():
    on_initialization = Seq(
        [
            App.localPut(Int(0), Bytes("seller"), Txn.sender()),
            App.localPut(Int(0), Bytes("buyer"), Txn.application_id()),
        ]
    )

    on_payment = Seq(
        [
            If(Txn.application_id() == App.id(), on_initialization),
            # Ensure the payment comes from the buyer
            If(
                Txn.sender() != App.localGet(Int(0), Bytes("buyer")),
                Err() # type: ignore
            ),
            # check if the payment is complete
            If(
                And(
                    App.localGet(Int(0), Bytes("buyer")) == Txn.sender(),
                    App.localGet(Int(0), Bytes("seller")) == escrow_address,
                ),
                Return(Int(1)),  # Return 1 to signify a successful payment
            ),
        ]
    )

    return Seq([on_payment])


# Define the approval program
@app.external
def dao_approval_program():

    # Define transaction types
    payment_tx = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.receiver() == dao_address
    )

    # Logic to handle payments to the DAO
    on_payment = Seq([
        Assert(payment_tx),  # Ensure the transaction is a payment to the DAO
        App.localPut(Int(0), Bytes("votes"), Btoi(Txn.asset_amount())),  # Store the number of votes
    ])

    # Logic to handle voting
    on_vote = Seq([
        Assert(And(Txn.application_args.length() == Int(1), Txn.application_args[0] == Bytes("vote"))),
        App.localPut(Int(0), Bytes("last_vote"), Btoi(Txn.application_args[1]))  # Store the last vote
    ])

    return Seq([Cond([payment_tx, on_payment], [Txn.application_args.length() > Int(0), on_vote])])


# Define the approval program
@app.external
def dispute_resolution_approval_program():

    # Logic to handle disputes
    on_dispute = Seq([
        Assert(Txn.type_enum() == TxnType.ApplicationCall),  # Ensure it's an application call
        App.localPut(Int(0), Bytes("dispute"), Int(1))  # Set a flag to indicate a dispute
    ])

    return on_dispute


@app.external
def rewards_distribution_approval_program():

    # Logic to handle rewards distribution
    on_reward = Seq([
        Assert(Txn.type_enum() == TxnType.ApplicationCall),  # Ensure it's an application call
        App.localPut(Int(0), Bytes("reward"), Btoi(Txn.application_args[0]))  # Store the reward amount
    ])

    return on_reward
