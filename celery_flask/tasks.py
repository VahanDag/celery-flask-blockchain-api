import json

from flask import jsonify
from web3 import Web3, exceptions
from web3.middleware import geth_poa_middleware

from celery_flask import celery

with open('/media/sf_VBoxSharedFiles/nftAbi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)



@celery.task(bind=True, default_retry_delay=20)
def admin_action(self,data, admin_address, admin_private_key, nonce):
    try:
        print("ARE YOU HERE?")
        w3 = Web3(Web3.HTTPProvider('https://polygon-mumbai.g.alchemy.com/v2/HTAxg7fG4iLGhAueAQEObeaqlzNM1qMH/'))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        contract_address = w3.to_checksum_address("0x9D51bBaB56C01e90DbaCCBD99ca97B0CE2155CDf")
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        # print(f" ADDRESS: {contract_address}")

        # Her bir admin hesabı için doğru nonce değerini alıyoruz
        # nonce = w3.eth.get_transaction_count(w3.to_checksum_address(admin_address))
        print(f"NONCE: {nonce} ADMIN: {admin_address}") 

        function_name = data['function_name']
        function_params = data['function_params']
        
        if function_name not in contract.functions:
            raise ValueError("Error: Invalid function name.")
        
        if function_name == "updateFactorX":
            user_address = w3.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]
            new_factorX = function_params["factorX"]

            contract_function = contract.functions[function_name](token_id,user_address,new_factorX)

        elif function_name == "levelUp":
            user_address = w3.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]

            contract_function = contract.functions[function_name](token_id,user_address)  
        
        elif function_name == "mintReward":
            user_address = w3.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]
            reward_price = function_params["reward_price"]

            contract_function = contract.functions[function_name](token_id,user_address, reward_price)  
        
        elif function_name == "changeInitialPrice":
            new_initial_charge_price = function_params["new_initial_charge_price"]

            contract_function = contract.functions[function_name](new_initial_charge_price)
            
        try:
            gas_estimate = contract_function.estimate_gas({'from': admin_address})
            gas_estimate += int(gas_estimate * 0.20)
        except exceptions.ContractLogicError as error:
            # Loglama yapılacak yer
            raise Exception(f'Gas estimate failed: {error}')



        txn = contract_function.build_transaction({
            'chainId': 80001,
            'gas': gas_estimate,
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=admin_private_key)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        
    except Exception as exc:
        raise self.retry(exc=exc, max_retries=3)
    
    return {
            'transactionHash': txn_hash.hex(),
        }