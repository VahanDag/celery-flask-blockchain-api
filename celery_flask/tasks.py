
from web3 import exceptions

from celery_flask import celery, contract_init, w3_init

from .utils import log_flask_error


@celery.task(bind=True, default_retry_delay=10)
def admin_action(self,data, admin_address, admin_private_key, nonce):
    try:
        print("ARE YOU HERE?")

        print(f"NONCE: {nonce} ADMIN: {admin_address}") 

        function_name = data['function_name']
        function_params = data['function_params']
        
        
        if function_name == "updateFactorX":
            user_address = w3_init.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]
            new_factorX = function_params["factorX"]

            contract_function = contract_init.functions[function_name](token_id,user_address,new_factorX)

        elif function_name == "levelUp":
            user_address = w3_init.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]

            contract_function = contract_init.functions[function_name](token_id,user_address)  
        
        elif function_name == "mintReward":
            user_address = w3_init.to_checksum_address(function_params["user_address"])
            token_id = function_params["token_id"]
            reward_price = function_params["reward_price"]

            contract_function = contract_init.functions[function_name](token_id,user_address, reward_price)  
        
        elif function_name == "changeInitialPrice":
            new_initial_charge_price = function_params["new_initial_charge_price"]

            contract_function = contract_init.functions[function_name](new_initial_charge_price)
            
        try:
            gas_estimate = contract_function.estimate_gas({'from': admin_address})
            gas_estimate += int(gas_estimate * 0.20)
        except exceptions.ContractLogicError as error:
            log_flask_error(f"GAS ESTIMATE: {error}")
            raise self.retry(exc=error,max_retries =3)


        txn = contract_function.build_transaction({
            'chainId': 80001,
            'gas': gas_estimate,
            'nonce': nonce,
        })

        signed_txn = w3_init.eth.account.sign_transaction(txn, private_key=admin_private_key)
        txn_hash = w3_init.eth.send_raw_transaction(signed_txn.rawTransaction)
        # w3_init.eth.wait_for_transaction_receipt(txn_hash)
        
    except Exception as exc:
        # update_nonce(admin_address)
        raise self.retry(exc=exc, max_retries=3)
    
    return {
            'transactionHash': txn_hash.hex(),
        }